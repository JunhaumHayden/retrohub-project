import pytest
from app.models import Cliente, Funcionario
from app.repository.db.usuario_repository_db import UsuarioRepositoryDB

def test_create_and_get_cliente(db_session):
    """Testa a criação e busca de um Cliente."""
    repo = UsuarioRepositoryDB(db_session)
    novo_cliente = Cliente(
        nome="Cliente Teste",
        cpf="123.456.789-00",
        email="cliente@teste.com",
        senha="senha123"
    )
    
    # Criar
    criado = repo.create(novo_cliente)
    assert criado.id is not None
    assert criado.nome == "Cliente Teste"

    # Buscar por ID
    encontrado = repo.get_cliente_by_id(criado.id)
    assert encontrado is not None
    assert encontrado.nome == "Cliente Teste"

def test_create_and_get_funcionario(db_session):
    """Testa a criação e busca de um Funcionario."""
    repo = UsuarioRepositoryDB(db_session)
    novo_funcionario = Funcionario(
        nome="Funcionario Teste",
        cpf="987.654.321-11",
        email="func@teste.com",
        senha="senha123",
        matricula="F-001"
    )
    
    # Criar
    criado = repo.create(novo_funcionario)
    assert criado.id is not None
    assert criado.matricula == "F-001"

    # Buscar por ID
    encontrado = repo.get_funcionario_by_id(criado.id)
    assert encontrado is not None
    assert encontrado.nome == "Funcionario Teste"

def test_update_usuario(db_session):
    """Testa a atualização de um usuário."""
    repo = UsuarioRepositoryDB(db_session)
    cliente = Cliente(
        nome="Nome Original",
        cpf="222.222.222-22",
        email="update@teste.com",
        senha="senha123"
    )
    criado = repo.create(cliente)
    
    # Atualizar
    criado.nome = "Nome Atualizado"
    atualizado = repo.update(criado)
    
    assert atualizado.nome == "Nome Atualizado"
    
    # Verificar se a atualização persistiu
    encontrado = repo.get_cliente_by_id(criado.id)
    assert encontrado.nome == "Nome Atualizado"

def test_delete_usuario(db_session):
    """Testa a exclusão de um usuário."""
    repo = UsuarioRepositoryDB(db_session)
    cliente = Cliente(
        nome="Para Deletar",
        cpf="333.333.333-33",
        email="delete@teste.com",
        senha="senha123"
    )
    criado = repo.create(cliente)
    
    # Deletar
    deletado = repo.delete(criado)
    assert deletado is True
    
    # Verificar se foi deletado
    encontrado = repo.get_cliente_by_id(criado.id)
    assert encontrado is None

def test_list_clientes_and_funcionarios(db_session):
    """Testa a listagem separada de clientes e funcionários."""
    repo = UsuarioRepositoryDB(db_session)
    
    repo.create(Cliente(nome="Cliente 1", cpf="c1", email="c1@test.com", senha="1"))
    repo.create(Cliente(nome="Cliente 2", cpf="c2", email="c2@test.com", senha="1"))
    repo.create(Funcionario(nome="Func 1", cpf="f1", email="f1@test.com", senha="1", matricula="F1"))
    
    clientes = repo.list_clientes()
    assert len(clientes) == 2
    assert all(isinstance(c, Cliente) for c in clientes)
    
    funcionarios = repo.list_funcionarios()
    assert len(funcionarios) == 1
    assert isinstance(funcionarios[0], Funcionario)
