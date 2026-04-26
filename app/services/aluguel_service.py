"""Camada de serviço para o domínio Aluguel.

Concentra toda a regra de negócio do ciclo de vida de um aluguel
(`solicitar` → `aprovar` → `registrar_retirada` → `registrar_devolucao`),
incluindo cálculo de multa por atraso e orquestração do estado do
exemplar associado. As rotas viram thin controllers que apenas delegam
para este serviço.

Política de multa:
- 10% da diária do catálogo por dia de atraso.
- Teto: 100% do valor total do aluguel.
- Sem atraso → ``Multa.valor = 0`` e ``Multa.status = 'PAGO'`` (não há nada a cobrar).

Política de exemplares:
- Solicitar    → exemplar passa de DISPONIVEL para RESERVADO.
- Cancelar     → exemplar volta para DISPONIVEL.
- Retirada     → exemplar passa para ALUGADO.
- Devolução    → exemplar volta para DISPONIVEL.

Funções legadas (``registrar_retirada`` / ``registrar_devolucao``) são
mantidas como wrappers para preservar imports antigos, mas delegam para
o serviço atual usando o ``container`` global.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import TYPE_CHECKING, Optional, Tuple

from app.models.enums import StatusAluguel, StatusPagamento
from app.models.transacao.aluguel.aluguel import Aluguel
from app.models.transacao.aluguel.multa import Multa
from app.models.transacao.item_transacao import ItemTransacao
from app.models.estoque.exemplar import Exemplar
from app.models.estoque.midia_fisica import MidiaFisica
from app.models.estoque.midia_digital import MidiaDigital

if TYPE_CHECKING:
    from app.database.interfaces.data_source_interface import DataSourceInterface
    from app.services.catalogo_service import CatalogoService
    from app.models.usuario.cliente import Cliente
    from app.models.usuario.funcionario import Funcionario


_CONDICOES_DEVOLUCAO = frozenset({"bom", "danificado", "extraviado"})

_PERIODO_MIN = 1
_PERIODO_MAX = 30


def _q2(value: Decimal) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class AluguelService:
    """Serviço de aplicação para o domínio Aluguel."""

    def __init__(
            self,
            data_source: "DataSourceInterface",
            catalogo_service: "CatalogoService",
    ):
        self.ds = data_source
        self.catalogo_service = catalogo_service

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------
    def listar_por_cliente(self, cliente_id: int) -> list[Aluguel]:
        return [
            a for a in self.ds.get_all(Aluguel)
            if a.id_cliente == cliente_id
        ]

    def obter(
            self, aluguel_id: int, cliente_id: Optional[int] = None,
    ) -> Optional[Aluguel]:
        """Retorna o aluguel; se ``cliente_id`` for passado, exige posse."""
        aluguel = self.ds.get_by_id(Aluguel, aluguel_id)
        if not aluguel:
            return None
        if cliente_id is not None and aluguel.id_cliente != cliente_id:
            return None
        return aluguel

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------
    def _exemplar_disponivel(
            self, id_catalogo: int, tipo_midia: str,
    ) -> Optional[Exemplar]:
        """Procura um exemplar do catálogo dado, com a situação DISPONIVEL,
        no formato (FISICA / DIGITAL) requerido."""
        midias_fisicas_ids = {m.id for m in self.ds.get_all(MidiaFisica)}
        midias_digitais_ids = {m.id for m in self.ds.get_all(MidiaDigital)}

        for ex in self.ds.get_all(Exemplar):
            if ex.id_catalogo != id_catalogo:
                continue
            if (ex.situacao or "DISPONIVEL").upper() != "DISPONIVEL":
                continue
            if tipo_midia == "FISICA" and ex.id in midias_fisicas_ids:
                return ex
            if tipo_midia == "DIGITAL" and ex.id in midias_digitais_ids:
                return ex
        return None

    def _exemplar_do_aluguel(self, aluguel: Aluguel) -> Optional[Exemplar]:
        for item in self.ds.get_all(ItemTransacao):
            if item.id_transacao == aluguel.id:
                return self.ds.get_by_id(Exemplar, item.id_exemplar)
        return None

    @staticmethod
    def _exigir_status(aluguel: Aluguel, *permitidos: str) -> None:
        if aluguel.status not in permitidos:
            raise ValueError(
                f"Operação não permitida no status atual ({aluguel.status})."
            )

    # ------------------------------------------------------------------
    # Caso de uso: solicitar aluguel
    # ------------------------------------------------------------------
    def solicitar(
            self,
            cliente: "Cliente",
            id_jogo: int,
            dias_alugados: int,
            data_inicio: date,
            tipo_midia: str,
    ) -> Aluguel:
        """Cria um Aluguel novo (status SOLICITADO) e bloqueia um exemplar."""
        if not isinstance(dias_alugados, int) or not (
            _PERIODO_MIN <= dias_alugados <= _PERIODO_MAX
        ):
            raise ValueError(
                f"O período de aluguel deve ser entre {_PERIODO_MIN} e "
                f"{_PERIODO_MAX} dias."
            )
        if data_inicio < date.today():
            raise ValueError(
                "A data de início não pode ser anterior à data atual."
            )

        tipo_midia = (tipo_midia or "").upper()
        if tipo_midia not in {"FISICA", "DIGITAL"}:
            raise ValueError("tipo_midia deve ser FISICA ou DIGITAL.")

        jogo = self.catalogo_service.get_by_id(id_jogo)
        if not jogo or jogo.situacao != "DISPONIVEL":
            raise ValueError("Jogo não existe ou está indisponível no catálogo.")

        exemplar = self._exemplar_disponivel(jogo.id, tipo_midia)
        if not exemplar:
            raise ValueError(
                f"Não há exemplares da mídia {tipo_midia} disponíveis "
                "no momento para este jogo."
            )

        valor_diaria = getattr(exemplar, 'valor_diaria_aluguel', None)
        if not valor_diaria:
            raise ValueError(
                "Este exemplar não está disponível para aluguel "
                "(valor da diária não definido)."
            )

        valor_total = _q2(Decimal(valor_diaria) * dias_alugados)
        data_prevista = data_inicio + timedelta(days=dias_alugados)

        aluguel = Aluguel(
            valor_total=valor_total,
            data_transacao=datetime.utcnow(),
            cliente=cliente,
            periodo=dias_alugados,
            data_inicio=data_inicio,
            data_prevista_devolucao=data_prevista,
            status=StatusAluguel.SOLICITADO.value,
        )
        criado = self.ds.create(aluguel)

        item = ItemTransacao(
            id=None,
            transacao=criado,
            exemplar=exemplar,
            valor_unitario=valor_diaria,
            quantidade=dias_alugados,
        )
        self.ds.create(item)
        criado.adicionar_item(item)

        exemplar.situacao = "RESERVADO"
        self.ds.update(exemplar)

        return criado

    # ------------------------------------------------------------------
    # Caso de uso: aprovar (SOLICITADO -> APROVADO)
    # ------------------------------------------------------------------
    def aprovar(self, aluguel_id: int, funcionario: "Funcionario") -> Aluguel:
        aluguel = self.ds.get_by_id(Aluguel, aluguel_id)
        if not aluguel:
            raise LookupError("Aluguel não encontrado.")
        self._exigir_status(aluguel, StatusAluguel.SOLICITADO.value)
        aluguel.status = StatusAluguel.APROVADO.value
        aluguel.funcionario = funcionario
        self.ds.update(aluguel)
        return aluguel

    # ------------------------------------------------------------------
    # Caso de uso: cancelar (SOLICITADO|APROVADO -> CANCELADO)
    # ------------------------------------------------------------------
    def cancelar(self, aluguel_id: int, cliente_id: int) -> Aluguel:
        aluguel = self.obter(aluguel_id, cliente_id)
        if not aluguel:
            raise LookupError(
                "Aluguel não encontrado ou não pertence a este cliente."
            )
        self._exigir_status(
            aluguel,
            StatusAluguel.SOLICITADO.value,
            StatusAluguel.APROVADO.value,
        )
        if aluguel.data_inicio and aluguel.data_inicio <= date.today():
            raise ValueError(
                "Não é possível cancelar um aluguel cuja data de início "
                "já chegou."
            )
        aluguel.status = "CANCELADO"
        self.ds.update(aluguel)

        exemplar = self._exemplar_do_aluguel(aluguel)
        if exemplar and exemplar.situacao == "RESERVADO":
            exemplar.situacao = "DISPONIVEL"
            self.ds.update(exemplar)

        return aluguel

    # ------------------------------------------------------------------
    # Caso de uso: renovar (ATIVO -> ATIVO + dias)
    # ------------------------------------------------------------------
    def renovar(
            self, aluguel_id: int, cliente_id: int, dias_adicionais: int,
    ) -> Aluguel:
        if not isinstance(dias_adicionais, int) or not (
            _PERIODO_MIN <= dias_adicionais <= _PERIODO_MAX
        ):
            raise ValueError(
                f"O período de renovação deve ser entre {_PERIODO_MIN} e "
                f"{_PERIODO_MAX} dias."
            )
        aluguel = self.obter(aluguel_id, cliente_id)
        if not aluguel:
            raise LookupError(
                "Aluguel não encontrado ou não pertence a este cliente."
            )
        self._exigir_status(
            aluguel,
            StatusAluguel.ATIVO.value,
            StatusAluguel.ATRASADO.value,
        )

        exemplar = self._exemplar_do_aluguel(aluguel)
        valor_diaria = getattr(exemplar, 'valor_diaria_aluguel', None) if exemplar else None
        if not valor_diaria:
            raise ValueError(
                "Exemplar do aluguel não tem valor de diária definido."
            )

        acrescimo = _q2(Decimal(valor_diaria) * dias_adicionais)
        aluguel.periodo = (aluguel.periodo or 0) + dias_adicionais
        if aluguel.data_prevista_devolucao:
            aluguel.data_prevista_devolucao = (
                aluguel.data_prevista_devolucao + timedelta(days=dias_adicionais)
            )
        aluguel.valor_total = _q2(
            Decimal(aluguel.valor_total or 0) + acrescimo
        )
        self.ds.update(aluguel)
        return aluguel

    # ------------------------------------------------------------------
    # Caso de uso: registrar retirada (SOLICITADO|APROVADO -> ATIVO)
    # ------------------------------------------------------------------
    def registrar_retirada(
            self, aluguel_id: int, funcionario: "Funcionario",
    ) -> Aluguel:
        aluguel = self.ds.get_by_id(Aluguel, aluguel_id)
        if not aluguel:
            raise LookupError("Aluguel não encontrado.")
        self._exigir_status(
            aluguel,
            StatusAluguel.SOLICITADO.value,
            StatusAluguel.APROVADO.value,
        )

        agora = datetime.utcnow()
        aluguel.data_retirada = agora
        aluguel.data_inicio = agora.date()
        aluguel.status = StatusAluguel.ATIVO.value
        aluguel.funcionario = funcionario
        if aluguel.periodo:
            aluguel.data_prevista_devolucao = (
                aluguel.data_inicio + timedelta(days=aluguel.periodo)
            )
        self.ds.update(aluguel)

        exemplar = self._exemplar_do_aluguel(aluguel)
        if exemplar:
            exemplar.situacao = "ALUGADO"
            self.ds.update(exemplar)

        return aluguel

    # ------------------------------------------------------------------
    # Caso de uso: registrar devolução (ATIVO -> FINALIZADO + multa)
    # ------------------------------------------------------------------
    def registrar_devolucao(
            self,
            aluguel_id: int,
            condicao_item: str,
            funcionario: "Funcionario",
    ) -> Tuple[Aluguel, Multa]:
        cond = (condicao_item or "").strip().lower()
        if not cond:
            raise ValueError("O campo 'condicao_item' é obrigatório.")
        if cond not in _CONDICOES_DEVOLUCAO:
            raise ValueError(
                "condicao_item deve ser: bom, danificado ou extraviado."
            )

        aluguel = self.ds.get_by_id(Aluguel, aluguel_id)
        if not aluguel:
            raise LookupError("Aluguel não encontrado.")
        if aluguel.status not in (
            StatusAluguel.ATIVO.value,
            StatusAluguel.ATRASADO.value,
        ):
            raise ValueError(
                f"Devolução não permitida no status {aluguel.status}."
            )
        if getattr(aluguel, "data_devolucao_real", None):
            raise ValueError("Devolução já registrada para este aluguel.")

        agora = datetime.utcnow()
        d_real = agora.date()

        exemplar = self._exemplar_do_aluguel(aluguel)
        valor_diaria_attr = (
            getattr(exemplar, 'valor_diaria_aluguel', None) if exemplar else None
        )
        valor_diaria = (
            Decimal(valor_diaria_attr) if valor_diaria_attr else Decimal("0")
        )
        valor_total = (
            Decimal(aluguel.valor_total)
            if aluguel.valor_total is not None else Decimal("0")
        )

        dias_atraso = 0
        prev = aluguel.data_prevista_devolucao
        if prev is not None and d_real > prev:
            dias_atraso = (d_real - prev).days

        multa_bruta = (
            _q2(Decimal(dias_atraso) * (valor_diaria * Decimal("0.10")))
            if dias_atraso > 0 and valor_diaria > 0 else Decimal("0")
        )
        teto = _q2(valor_total) if valor_total > 0 else Decimal("0")
        multa_valor = (
            min(multa_bruta, teto) if teto > 0 else Decimal("0")
        )

        aluguel.data_devolucao_real = agora
        aluguel.data_devolucao = d_real
        aluguel.status = StatusAluguel.FINALIZADO.value
        aluguel.condicao_item = cond
        aluguel.funcionario_recebimento = funcionario
        aluguel.dias_atraso = dias_atraso

        multa = Multa(
            aluguel=aluguel,
            dias_atraso=dias_atraso,
            valor=multa_valor,
            status=(
                StatusPagamento.PAGO.value if multa_valor == 0
                else StatusPagamento.PENDENTE.value
            ),
            data_calculo=d_real,
        )
        self.ds.create(multa)

        aluguel.multa_aplicada = multa
        aluguel.multa_paga = (multa_valor == 0)
        self.ds.update(aluguel)

        if exemplar:
            exemplar.situacao = "DISPONIVEL"
            self.ds.update(exemplar)

        return aluguel, multa


# ---------------------------------------------------------------------------
# Wrappers legados (mantidos para preservar imports existentes).
# ---------------------------------------------------------------------------
def registrar_retirada(aluguel_id: int):  # pragma: no cover - legado
    """Wrapper legado: usa o container global e devolve a tupla
    ``(aluguel, mensagem_de_erro)`` esperada pela rota antiga."""
    from app.container.container import container
    try:
        aluguel = container.aluguel_service.registrar_retirada(
            aluguel_id, funcionario=None,
        )
        return aluguel, None
    except (ValueError, LookupError) as exc:
        return None, str(exc)


def registrar_devolucao(
        aluguel_id: int,
        condicao_item: str,
        id_funcionario_recebimento: int,
):  # pragma: no cover - legado
    from app.container.container import container
    try:
        aluguel, _multa = container.aluguel_service.registrar_devolucao(
            aluguel_id, condicao_item, funcionario=None,
        )
        return aluguel, None
    except (ValueError, LookupError) as exc:
        return None, str(exc)
