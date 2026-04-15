from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.models import Aluguel, Exemplar, ItemTransacao, Catalogo, Multa

_CONDICOES_DEVOLUCAO = frozenset({"bom", "danificado", "extraviado"})


def _q2(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def registrar_retirada(session: Session, aluguel_id: int) -> Tuple[Optional[Aluguel], Optional[str]]:
    """
    Registra a saída física/digital do item: status ATIVO, data de retirada,
    previsão de fim com base no período e atualização do exemplar/catálogo.
    """
    aluguel = session.query(Aluguel).get(aluguel_id)
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

    item = session.query(ItemTransacao).filter_by(id_transacao=aluguel.id).first()
    if not item:
        return None, "Item da transação não encontrado."
    exemplar = session.query(Exemplar).get(item.id_exemplar)
    if exemplar:
        exemplar.situacao = "ALUGADO"
        jogo = session.query(Catalogo).get(exemplar.id_jogo)
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

    aluguel = session.query(Aluguel).get(aluguel_id)
    if not aluguel:
        return None, "Aluguel não encontrado."
    if aluguel.status != "ATIVO":
        return None, "Devolução permitida apenas para aluguel ativo."
    if getattr(aluguel, "data_devolucao_real", None):
        return None, "Devolução já registrada para este aluguel."

    agora = datetime.utcnow()
    d_real = agora.date()

    item = session.query(ItemTransacao).filter_by(id_transacao=aluguel.id).first()
    if not item:
        return None, "Item da transação não encontrado."

    exemplar = session.query(Exemplar).get(item.id_exemplar)
    jogo = session.query(Catalogo).get(exemplar.id_jogo) if exemplar else None
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
    aluguel.status = "FINALIZADO"
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
