import pytest
from app.models.usuario.cliente import Cliente
from app.models.usuario.funcionario import Funcionario

def test_create_cliente_success(usuario_service):
    """Testa a criação bem-sucedida de um cliente."""
    cliente = Cliente(
        nome="Teste Cliente",
        cpf="123.456.789-00",
        email="teste@cliente.com",
        senha="senha_segura"
    )
    result = usuario_service.create_cliente(cliente)
    assert result is not None
    assert result.id is not None
    assert result.nome == "Teste Cliente"

def test_create_funcionario_success(usuario_service):
    """Testa a criação bem-sucedida de um funcionário."""
    funcionario = Funcionario(
        nome="Teste Funcionario",
        cpf="987.654.321-11",
        email="teste@funcionario.com",
        senha="senha_segura",
        matricula="F-1234"
    )
    result = usuario_service.create_funcionario(funcionario)
    assert result is not None
    assert result.id is not None
    assert result.matricula == "F-1234"

def test_update_cliente_success(usuario_service):
    """Testa a atualização bem-sucedida de um cliente."""
    cliente = Cliente(
        nome="Original",
        cpf="111.111.111-11",
        email="original@cliente.com",
        senha="123"
    )
    created = usuario_service.create_cliente(cliente)
    
    update_data = {"nome": "Atualizado"}
    updated = usuario_service.update_cliente(created.id, update_data)
    
    assert updated is not None
    assert updated.nome == "Atualizado"

def test_update_funcionario_success(usuario_service):
    """Testa a atualização bem-sucedida de um funcionário."""
    funcionario = Funcionario(
        nome="Original Func",
        cpf="222.222.222-22",
        email="original@func.com",
        senha="123",
        matricula="F-ORIG"
    )
    created = usuario_service.create_funcionario(funcionario)
    
    update_data = {"cargo": "Gerente"}
    updated = usuario_service.update_funcionario(created.id, update_data)
    
    assert updated is not None
    assert updated.cargo == "Gerente"