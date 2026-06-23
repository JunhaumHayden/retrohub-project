import pytest
from sqlalchemy import text
from app.models import Usuario, Catalogo, Transacao

def test_1_connection_is_active(db_session):
    """Testa se a conexão com o banco está ativa executando um simples SELECT 1."""
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1, "O banco de dados não respondeu ao comando SELECT 1."

def test_2_query_usuarios_exist(db_session):
    """Testa se as tabelas relacionadas a usuários foram criadas corretamente."""
    # Since we are using an empty in-memory DB for tests, we can't assert > 0 here
    # Instead, we just verify the table exists and can be queried without error.
    result = db_session.query(Usuario).count()
    assert result == 0, "A tabela de usuários deveria estar vazia no início do teste."

def test_3_query_jogos_exist(db_session):
    """Testa se a tabela de catálogo foi criada corretamente."""
    result = db_session.query(Catalogo).count()
    assert result == 0, "A tabela 'catalogo' deveria estar vazia no início do teste."

def test_4_query_transacoes(db_session):
    """Testa se a tabela de transações foi criada corretamente."""
    result = db_session.query(Transacao).count()
    assert result == 0, "A tabela 'transacoes' deveria estar vazia no início do teste."
