from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.models import Aluguel, Exemplar, ItemTransacao, Catalogo, Multa

_CONDICOES_DEVOLUCAO = frozenset({"bom", "danificado", "extraviado"})


def _q2(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def registrar_retirada(session: Session, aluguel_id: int) -> Tuple[Optional[Aluguel], Optional[str]]:
    """
    Registra a saída física/digital do item: define o status ATIVO e atualiza o exemplar/catálogo.
    """
    aluguel = session.get(Aluguel, aluguel_id)
    if not aluguel:
        return None, "Aluguel não encontrado."

    try:
        aluguel.registrar_retirada()
    except ValueError as exc:
        return None, str(exc)

    agora = datetime.now(timezone.utc)
    aluguel.data_retirada = agora
    aluguel.data_inicio = agora.date()
    periodo = aluguel.periodo or 0
    if periodo > 0:
        aluguel.data_prevista_devolucao = aluguel.data_inicio + timedelta(days=periodo)

    item = session.query(ItemTransacao).filter_by(id_transacao=aluguel.id).first()
    if not item:
        return None, "Item da transação não encontrado."
    exemplar = session.get(Exemplar, item.id_exemplar)
    if exemplar:
        exemplar.situacao = "ALUGADO"
        jogo = session.get(Catalogo, exemplar.id_catalogo)
        if jogo is not None and jogo.estoque_disponivel is not None and jogo.estoque_disponivel > 0:
            jogo.estoque_disponivel -= 1

    return aluguel, None


def registrar_devolucao(
    session: Session,
    aluguel_id: int,
    condicao_item: str,
    id_funcionario_recebimento: int,
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

    aluguel = session.get(Aluguel, aluguel_id)
    if not aluguel:
        return None, "Aluguel não encontrado."
    if getattr(aluguel, "data_devolucao_real", None):
        return None, "Devolução já registrada para este aluguel."

    try:
        aluguel.finalizar_aluguel()
    except ValueError as exc:
        return None, str(exc)

    agora = datetime.now(timezone.utc)
    d_real = agora.date()

    item = session.query(ItemTransacao).filter_by(id_transacao=aluguel.id).first()
    if not item:
        return None, "Item da transação não encontrado."

    exemplar = session.get(Exemplar, item.id_exemplar)
    jogo = session.get(Catalogo, exemplar.id_catalogo) if exemplar else None
    valor_diaria = jogo.valor_diaria_aluguel if jogo and jogo.valor_diaria_aluguel else Decimal("0")
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
    aluguel.condicao_item = cond_norm
    aluguel.id_funcionario_recebimento = id_funcionario_recebimento
    aluguel.dias_atraso = dias_atraso
    aluguel.multa_aplicada = multa_valor
    aluguel.multa_paga = bool(multa_valor == 0)

    if exemplar:
        exemplar.situacao = "DISPONIVEL"
    if jogo is not None and jogo.estoque_disponivel is not None:
        jogo.estoque_disponivel += 1

    if multa_valor > 0:
        session.add(
            Multa(
                id_aluguel=aluguel.id,
                dias_atraso=dias_atraso,
                valor=multa_valor,
                status="PENDENTE",
                data_calculo=d_real,
            )
        )

    return aluguel, None
