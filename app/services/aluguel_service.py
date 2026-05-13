from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Tuple

from app.database.mock_data_source import MockDataSource
from app.repository.mock.aluguel_repository_mock import AluguelRepositoryMock
from app.models import Aluguel, Comprovante, Multa
from app.models.enums import TipoComprovante

_CONDICOES_DEVOLUCAO = frozenset({"bom", "danificado", "extraviado"})


def _q2(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# Use a mock data source + repository instance for service functions
_DATA_SOURCE = MockDataSource()
_DATA_SOURCE.load_data()
_REPO = AluguelRepositoryMock(_DATA_SOURCE)


def registrar_retirada(aluguel_id: int, repo: Optional[AluguelRepositoryMock] = None) -> Tuple[Optional[Aluguel], Optional[str]]:
    """
    Registra a saída física/digital do item: status ATIVO, data de retirada,
    previsão de fim com base no período e atualização do exemplar/catálogo.
    """
    _r = repo or _REPO
    aluguel = _r.get_by_id(aluguel_id)
    if not aluguel:
        return None, "Aluguel não encontrado."
    if aluguel.status not in ("SOLICITADO", "APROVADO"):
        return None, "Retirada permitida apenas para aluguel solicitado ou aprovado."

    agora = datetime.utcnow()
    aluguel.data_retirada = agora
    aluguel.status = "ATIVO"
    di = agora.date()
    aluguel.data_inicio = di
    periodo = aluguel.periodo or 0
    if periodo > 0:
        aluguel.data_prevista_devolucao = di + timedelta(days=periodo)

    items = _r.get_items_by_transacao(aluguel.id) or []
    if not items:
        return None, "Itens da transação não encontrados."

    for item in items:
        exemplar = _r.get_exemplar_by_id(item.id_exemplar) if item and item.id_exemplar is not None else None
        if exemplar:
            exemplar.situacao = "ALUGADO"
            _r.update(exemplar)

    _r.update(aluguel)
    return aluguel, None


class AluguelService:
    """Light wrapper service exposing the module functions via an instance suitable for DI."""

    def __init__(self, repository: Optional[AluguelRepositoryMock] = None):
        from app.repository.mock.aluguel_repository_mock import AluguelRepositoryMock as _ARM
        self.repo = repository or _REPO

    def registrar_retirada(self, aluguel_id: int):
        return registrar_retirada(aluguel_id, repo=self.repo)

    def registrar_devolucao(self, aluguel_id: int, condicao_item: str, id_funcionario_recebimento: int):
        return _registrar_devolucao(aluguel_id, condicao_item, id_funcionario_recebimento, repo=self.repo)


def _registrar_devolucao(
    aluguel_id: int,
    condicao_item: str,
    id_funcionario_recebimento: int,
    repo: Optional[AluguelRepositoryMock] = None,
) -> Tuple[Optional[Aluguel], Optional[str]]:
    """
    Registra devolução de mídias: finaliza aluguel, libera exemplares,
    calcula multa por atraso e gera comprovante de devolução.
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
    if aluguel.status not in ("ATIVO", "ATRASADO"):
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
        exemplar = _r.get_exemplar_by_id(item.id_exemplar) if item and item.id_exemplar is not None else None
        if exemplar and hasattr(exemplar, 'valor_diaria_aluguel') and exemplar.valor_diaria_aluguel:
            valor_diaria_total += exemplar.valor_diaria_aluguel

    valor_total_aluguel = aluguel.valor_total if aluguel.valor_total is not None else Decimal("0")

    dias_atraso = 0
    prev = aluguel.data_prevista_devolucao
    if prev is not None and d_real > prev:
        dias_atraso = (d_real - prev).days

    multa_valor = Decimal("0")
    if dias_atraso > 0 and valor_diaria_total > 0:
        multa_bruta = _q2(Decimal(dias_atraso) * (valor_diaria_total * Decimal("0.10")))
        teto = _q2(valor_total_aluguel)
        multa_valor = min(multa_bruta, teto) if teto > 0 else multa_bruta

    aluguel.data_devolucao_real = agora
    aluguel.data_devolucao = d_real
    aluguel.status = "FINALIZADO"
    aluguel.condicao_item = cond_norm
    aluguel.id_funcionario_recebimento = id_funcionario_recebimento
    aluguel.dias_atraso = dias_atraso
    aluguel.multa_paga = bool(multa_valor == 0)

    for item in items:
        exemplar = _r.get_exemplar_by_id(item.id_exemplar)
        if exemplar:
            exemplar.situacao = "DISPONIVEL"
            _r.update(exemplar)

    if multa_valor > 0:
        multa = Multa(
            id=None,
            dias_atraso=dias_atraso,
            valor=multa_valor,
            status="PENDENTE",
            data_calculo=d_real,
        )
        saved_multa = _r.create_multa(multa)
        aluguel.multa_aplicada = saved_multa

    # Gerar e adicionar comprovante de devolução
    novo_comprovante = Comprovante(
        id=None,  # O repositório deve gerar o ID
        tipo_comprovante=TipoComprovante.DEVOLUCAO.value,
        data_envio=agora,
    )
    # O ID do comprovante será definido pelo repositório
    saved_comprovante = _r.create_comprovante(novo_comprovante)
    aluguel.adicionar_comprovante(saved_comprovante)

    _r.update(aluguel)

    return aluguel, None
