import pytest
from datetime import date
from app.models.transacao.avaliacao import Avaliacao

def test_criar_avaliacao_valida():
    avaliacao = Avaliacao(
        id_transacao=1,
        nota=5,
        comentario="Ótimo jogo!",
        data_avaliacao=date(2026, 6, 20)
    )
    
    assert avaliacao.id_transacao == 1
    assert avaliacao.nota == 5
    assert avaliacao.comentario == "Ótimo jogo!"
    assert avaliacao.data_avaliacao == date(2026, 6, 20)

def test_criar_avaliacao_sem_data_usa_data_atual():
    avaliacao = Avaliacao(
        id_transacao=2,
        nota=4
    )
    
    assert avaliacao.id_transacao == 2
    assert avaliacao.nota == 4
    assert avaliacao.data_avaliacao == date.today()
    assert avaliacao.comentario is None
