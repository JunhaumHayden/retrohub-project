from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.models import Aluguel, Exemplar, ItemTransacao, Jogo


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
        jogo = session.query(Jogo).get(exemplar.id_jogo)
        if jogo is not None and jogo.estoque_disponivel is not None and jogo.estoque_disponivel > 0:
            jogo.estoque_disponivel -= 1

    return aluguel, None
