from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Tuple

from app.database.mock_data_source import MockDataSource
from app.repository.mock.aluguel_repository_mock import AluguelRepositoryMock
from app.models import Aluguel, Exemplar, ItemTransacao, Catalogo, Multa

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

    # Get the item(s) for this transacao via repository
    items = _r.get_items_by_transacao(aluguel.id) or []
    item = items[0] if items else None
    if not item:
        return None, "Item da transação não encontrado."
    exemplar = _r.get_exemplar_by_id(item.id_exemplar) if item and item.id_exemplar is not None else None
    if exemplar:
        exemplar.situacao = "ALUGADO"
        _r.update(exemplar)

    _r.update(aluguel)
    return aluguel, None


class AluguelService:
    """Light wrapper service exposing the module functions via an instance suitable for DI."""

    def __init__(self, repository: Optional[AluguelRepositoryMock] = None):
        # avoid circular import at module top; accept repository injected by Container
        from app.repository.mock.aluguel_repository_mock import AluguelRepositoryMock as _ARM
        self.repo = repository or _REPO

    def registrar_retirada(self, aluguel_id: int):
        return registrar_retirada(aluguel_id, repo=self.repo)

    def registrar_devolucao(self, aluguel_id: int, condicao_item: str, id_funcionario_recebimento: int):
        return registrar_devolucao(aluguel_id, condicao_item, id_funcionario_recebimento, repo=self.repo)


def registrar_devolucao(
    aluguel_id: int,
    condicao_item: str,
    id_funcionario_recebimento: int,
    repo: Optional[AluguelRepositoryMock] = None,
) -> Tuple[Optional[Aluguel], Optional[str]]:
    """
    Registra devolução da mídia: finaliza aluguel, libera exemplar/estoque,
    condição do item e multa por atraso (10% da diária por dia, teto 100% do valor total).
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
    if aluguel.status != "ATIVO":
        return None, "Devolução permitida apenas para aluguel ativo."
    if getattr(aluguel, "data_devolucao_real", None):
        return None, "Devolução já registrada para este aluguel."

    agora = datetime.utcnow()
    d_real = agora.date()

    items = _r.get_items_by_transacao(aluguel.id) or []
    item = items[0] if items else None
    if not item:
        return None, "Item da transação não encontrado."

    exemplar = _r.get_exemplar_by_id(item.id_exemplar) if item and item.id_exemplar is not None else None
    # Use the exemplar's daily value (MidiaFisica/MidiaDigital) when available
    valor_diaria = (
        exemplar.valor_diaria_aluguel
        if exemplar and hasattr(exemplar, 'valor_diaria_aluguel') and exemplar.valor_diaria_aluguel
        else Decimal("0")
    )
    valor_total = aluguel.valor_total if aluguel.valor_total is not None else Decimal("0")

    dias_atraso = 0
    prev = aluguel.data_prevista_devolucao
    if prev is not None and d_real > prev:
        dias_atraso = (d_real - prev).days

    multa_bruta = Decimal("0")
    if dias_atraso > 0 and valor_diaria > 0:
        multa_bruta = _q2(Decimal(dias_atraso) * (valor_diaria * Decimal("0.10")))
    teto = _q2(valor_total) if valor_total > 0 else Decimal("0")
    if teto <= 0:
        multa_valor = Decimal("0")
    else:
        multa_valor = min(multa_bruta, teto)

    aluguel.data_devolucao_real = agora
    aluguel.data_devolucao = d_real
    aluguel.status = "FINALIZADO"
    aluguel.condicao_item = cond_norm
    # preserve previous shape: store received employee id and atraso info
    # Keep numeric id for routes/tests while model also has `funcionario_recebimento`
    aluguel.id_funcionario_recebimento = id_funcionario_recebimento
    aluguel.dias_atraso = dias_atraso
    aluguel.multa_paga = bool(multa_valor == 0)

    if exemplar:
        exemplar.situacao = "DISPONIVEL"
        _r.update(exemplar)

    # Save/update aluguel
    _r.update(aluguel)

    if multa_valor > 0:
        multa = Multa(
            id=None,
            dias_atraso=dias_atraso,
            valor=multa_valor,
            status="PENDENTE",
            data_calculo=d_real,
        )
        saved = _r.create_multa(multa)
        # attach multa object to aluguel for consistency (route will convert to float)
        aluguel.multa_aplicada = saved

    return aluguel, None
