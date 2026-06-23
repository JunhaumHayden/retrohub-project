import pytest
from app.models import Cliente, Funcionario
from app.services.usuario_service import UsuarioService

# A fixture 'test_container' é injetada automaticamente pelo conftest.py

def test_create_and_get_cliente(test_container):
    """Testa a criação e busca de um Cliente usando o DB."""
    usuario_service = test_container.usuario_service
    
    novo_cliente = Cliente(
        nome="Cliente DB Teste",
        cpf="123.456.789-00",
        email="cliente.db@teste.com",
        senha="senha123"
    )
    
    criado = usuario_service.create_cliente(novo_cliente)
    assert criado.id is not None
    
    encontrado = usuario_service.get_cliente_by_id(criado.id)
    assert encontrado is not None
    assert encontrado.nome == "Cliente DB Teste"

def test_update_cliente(test_container):
    """Testa a atualização de um cliente usando o DB."""
    usuario_service = test_container.usuario_service
    cliente = Cliente(
        nome="Nome Original",
        cpf="222.222.222-22",
        email="update.db@teste.com",
        senha="senha123"
    )
    criado = usuario_service.create_cliente(cliente)
    
    dados_update = {"nome": "Nome Atualizado"}
    atualizado = usuario_service.update_cliente(criado.id, dados_update)
    
    assert atualizado.nome == "Nome Atualizado"
    
    encontrado = usuario_service.get_cliente_by_id(criado.id)
    assert encontrado.nome == "Nome Atualizado"

def test_delete_cliente(test_container):
    """Testa a exclusão de um cliente usando o DB."""
    usuario_service = test_container.usuario_service
    cliente = Cliente(
        nome="Para Deletar DB",
        cpf="333.333.333-33",
        email="delete.db@teste.com",
        senha="senha123"
    )
    criado = usuario_service.create_cliente(cliente)
    
    deletado = usuario_service.delete_cliente(criado.id)
    assert deletado is True
    
    encontrado = usuario_service.get_cliente_by_id(criado.id)
    assert encontrado is None

def test_criar_cliente_duplicado_lanca_erro(test_container):
    """Testa se a criação de um cliente com CPF ou email duplicado lança um erro."""
    usuario_service = test_container.usuario_service
    cliente1 = Cliente(nome="Cliente 1", cpf="444.444.444-44", email="dup@teste.com", senha="1")
    usuario_service.create_cliente(cliente1)
    
    # Tenta criar com mesmo CPF
    cliente2 = Cliente(nome="Cliente 2", cpf="444.444.444-44", email="outro@email.com", senha="1")
    with pytest.raises(ValueError, match="Usuário com CPF .* já existe"):
        usuario_service.create_cliente(cliente2)
        
    # Tenta criar com mesmo email
    cliente3 = Cliente(nome="Cliente 3", cpf="555.555.555-55", email="dup@teste.com", senha="1")
    with pytest.raises(ValueError, match="Email .* já está em uso"):
        usuario_service.create_cliente(cliente3)
