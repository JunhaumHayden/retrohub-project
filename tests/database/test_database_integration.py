import pytest
from sqlalchemy import text
from app.models import Cliente, Catalogo, Transacao, ItemTransacao

# A fixture 'db_session' é injetada automaticamente pelo conftest.py

def test_database_session_is_active(db_session):
    """
    Testa se a sessão do banco de dados em memória está ativa e funcional.
    Substitui o antigo 'test_1_connection_is_active'.
    """
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1, "A sessão do banco de dados não respondeu ao comando SELECT 1."

def test_create_and_query_entities(db_session):
    """
    Testa a criação e consulta de entidades para garantir que o ORM e o DB estão funcionando.
    Substitui os antigos testes de verificação de dados pré-existentes.
    """
    # 1. Criar um Cliente
    novo_cliente = Cliente(
        nome="Cliente DB Integ",
        cpf="111.222.333-44",
        email="db.integ@test.com",
        senha="senha"
    )
    db_session.add(novo_cliente)
    db_session.commit()
    
    # Verificar se o cliente foi criado
    clientes = db_session.query(Cliente).all()
    assert len(clientes) == 1
    assert clientes[0].nome == "Cliente DB Integ"

    # 2. Criar um Jogo no Catálogo
    novo_jogo = Catalogo(titulo="Jogo de Integração")
    db_session.add(novo_jogo)
    db_session.commit()
    
    # Verificar se o jogo foi criado
    jogos = db_session.query(Catalogo).all()
    assert len(jogos) == 1
    assert jogos[0].titulo == "Jogo de Integração"

def test_transaction_and_relations(db_session):
    """
    Testa a criação de uma transação e seus relacionamentos.
    Substitui o antigo 'test_4_query_transacoes'.
    """
    # Criar entidades relacionadas
    cliente = Cliente(nome="Cliente Transação", cpf="t-1", email="t1@test.com", senha="1")
    catalogo = Catalogo(titulo="Jogo para Transação")
    
    db_session.add_all([cliente, catalogo])
    db_session.commit()

    # Criar uma transação
    nova_transacao = Transacao(
        cliente_id=cliente.id,
        valor_total=100.0,
        tipo="VENDA" # Exemplo
    )
    db_session.add(nova_transacao)
    db_session.commit()

    # Verificar se a transação foi criada e o relacionamento funciona
    transacao_criada = db_session.query(Transacao).filter_by(id=nova_transacao.id).one()
    assert transacao_criada is not None
    assert transacao_criada.cliente.nome == "Cliente Transação"
    assert transacao_criada.cliente_id == cliente.id
