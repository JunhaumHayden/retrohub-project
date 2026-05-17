"""
AluguelService — RF 07 / sd Devolucao / act finalizarAluguel (iteração 2).

A devolução percorre todos os itens da transação, aplica multa se houver
atraso e gera comprovante de devolução (branch demo/presentation-20260512).
"""

from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Tuple

from app.database.mock_data_source import MockDataSource
from app.repository.mock.aluguel_repository_mock import AluguelRepositoryMock
from app.models import Aluguel, Comprovante, Multa
from app.models.estoque.midia_fisica import MidiaFisica
from app.models.enums import TipoComprovante, StatusAluguel

_CONDICOES_DEVOLUCAO = frozenset({"bom", "danificado", "extraviado"})


def _q2(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


_DATA_SOURCE = MockDataSource()
_DATA_SOURCE.load_data()
_REPO = AluguelRepositoryMock(_DATA_SOURCE)


def registrar_retirada(
        aluguel_id: int,
        repo: Optional[AluguelRepositoryMock] = None,
) -> Tuple[Optional[Aluguel], Optional[str]]:
    """RF 07 — registro de saída (retirada)."""
    _r = repo or _REPO
    aluguel = _r.get_by_id(aluguel_id)
    if not aluguel:
        return None, "Aluguel não encontrado."
    if aluguel.status not in (
        StatusAluguel.SOLICITADO.value,
        StatusAluguel.APROVADO.value,
    ):
        return None, "Retirada permitida apenas para aluguel solicitado ou aprovado."

    agora = datetime.utcnow()
    aluguel.data_retirada = agora
    aluguel.status = StatusAluguel.ATIVO.value
    di = agora.date()
    aluguel.data_inicio = di
    periodo = aluguel.periodo or 0
    if periodo > 0:
        aluguel.data_prevista_devolucao = di + timedelta(days=periodo)

    items = _r.get_items_by_transacao(aluguel.id) or []
    if not items:
        return None, "Itens da transação não encontrados."

    for item in items:
        exemplar = (
            _r.get_exemplar_by_id(item.id_exemplar)
            if item and item.id_exemplar is not None else None
        )
        if exemplar:
            exemplar.set_situacao("ALUGADO")
            _r.update(exemplar)

    _r.update(aluguel)
    return aluguel, None


def finalizar_aluguel(
        aluguel_id: int,
        condicao: str,
        id_funcionario_recebimento: int,
        repo: Optional[AluguelRepositoryMock] = None,
) -> bool:
    """
    act AluguelService.finalizarAluguel — delega para registrar_devolucao.

    Validações e efeitos (multa, itens, comprovante) estão em
    ``_registrar_devolucao`` (sd Devolucao de Itens do Catalogo).
    """
    aluguel, erro = _registrar_devolucao(
        aluguel_id,
        condicao,
        id_funcionario_recebimento,
        repo=repo,
    )
    if erro:
        raise ValueError(erro)
    return aluguel is not None


def _registrar_devolucao(
        aluguel_id: int,
        condicao_item: str,
        id_funcionario_recebimento: int,
        repo: Optional[AluguelRepositoryMock] = None,
) -> Tuple[Optional[Aluguel], Optional[str]]:
    """
    sd Devolucao — registrarDevolucao → getAluguelById → finalizarAluguel.

    loop [item_transacao]: setSituacao(DISPONIVEL), setEstadoConservacao;
    opt [dias>0]: Multa; setComprovante(DEVOLUCAO).
    """
    if not condicao_item or not str(condicao_item).strip():
        return None, "O campo 'condicao_item' é obrigatório."
    cond_norm = str(condicao_item).strip().lower()
    if cond_norm not in _CONDICOES_DEVOLUCAO:
        return None, "condicao_item deve ser: bom, danificado ou extraviado."

    _r = repo or _REPO
    aluguel = _r.get_by_id(aluguel_id)
    if not aluguel:
        return None, "Aluguel não encontrado."
    if aluguel.status not in (
        StatusAluguel.ATIVO.value,
        StatusAluguel.ATRASADO.value,
    ):
        return None, "Devolução permitida apenas para aluguel ativo ou atrasado."
    if getattr(aluguel, "data_devolucao_real", None):
        return None, "Devolução já registrada para este aluguel."

    agora = datetime.utcnow()
    d_real = agora.date()

    items = _r.get_items_by_transacao(aluguel.id) or []
    if not items:
        return None, "Itens da transação não encontrados."

    valor_diaria_total = Decimal("0")
    for item in items:
        exemplar = (
            _r.get_exemplar_by_id(item.id_exemplar)
            if item and item.id_exemplar is not None else None
        )
        if exemplar and getattr(exemplar, "valor_diaria_aluguel", None):
            valor_diaria_total += exemplar.valor_diaria_aluguel

    valor_total_aluguel = (
        aluguel.valor_total if aluguel.valor_total is not None else Decimal("0")
    )

    dias_atraso = 0
    prev = aluguel.data_prevista_devolucao
    if prev is not None and d_real > prev:
        dias_atraso = (d_real - prev).days

    multa_valor = Decimal("0")
    if dias_atraso > 0 and valor_diaria_total > 0:
        multa_bruta = _q2(
            Decimal(dias_atraso) * (valor_diaria_total * Decimal("0.10"))
        )
        teto = _q2(valor_total_aluguel)
        multa_valor = min(multa_bruta, teto) if teto > 0 else multa_bruta

    aluguel.data_devolucao_real = agora
    aluguel.data_devolucao = d_real
    aluguel.status = StatusAluguel.FINALIZADO.value
    aluguel.condicao_item = cond_norm
    aluguel.id_funcionario_recebimento = id_funcionario_recebimento
    aluguel.dias_atraso = dias_atraso
    aluguel.multa_paga = bool(multa_valor == 0)

    for item in items:
        exemplar = _r.get_exemplar_by_id(item.id_exemplar)
        if not exemplar:
            continue
        exemplar.set_situacao("DISPONIVEL")
        if isinstance(exemplar, MidiaFisica):
            exemplar.set_estado_conservacao(cond_norm)
        _r.update(exemplar)

    if multa_valor > 0:
        multa = Multa(
            id=None,
            dias_atraso=dias_atraso,
            valor=multa_valor,
            status="PENDENTE",
            data_calculo=d_real,
        )
        multa.set_multa(
            dias_atraso=dias_atraso,
            valor=multa_valor,
            status="PENDENTE",
            data_calculo=d_real,
        )
        saved_multa = _r.create_multa(multa)
        aluguel.set_multa(saved_multa)

    aluguel.set_comprovante(TipoComprovante.DEVOLUCAO.value)
    for comprovante in aluguel.comprovantes:
        if comprovante.id is None:
            saved = _r.create_comprovante(comprovante)
            comprovante.id = saved.id

    _r.update(aluguel)
    return aluguel, None


class AluguelService:
    """Diagrama de classes — AluguelService + repositório de aluguéis."""

    def __init__(self, repository: Optional[AluguelRepositoryMock] = None):
        self.repo = repository or _REPO

    def get_aluguel_by_id(self, aluguel_id: int) -> Optional[Aluguel]:
        return self.repo.get_by_id(aluguel_id)

    def registrar_retirada(self, aluguel_id: int):
        return registrar_retirada(aluguel_id, repo=self.repo)

    def registrar_devolucao(
            self,
            aluguel_id: int,
            condicao_item: str,
            id_funcionario_recebimento: int,
    ):
        return _registrar_devolucao(
            aluguel_id,
            condicao_item,
            id_funcionario_recebimento,
            repo=self.repo,
        )

    def finalizar_aluguel(
            self,
            aluguel_id: int,
            condicao: str,
            id_funcionario_recebimento: int,
    ) -> bool:
        return finalizar_aluguel(
            aluguel_id,
            condicao,
            id_funcionario_recebimento,
            repo=self.repo,
        )
