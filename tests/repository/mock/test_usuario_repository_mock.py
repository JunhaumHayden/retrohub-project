import pytest
from app.models import Cliente, Funcionario
from app.repository.mock.usuario_repository_mock import UsuarioRepositoryMock
from app.database.data_source.MockDataSource import MockDataSource

@pytest.fixture
def mock_usuario_repo():
    """Fixture para fornecer uma instância limpa do repositório mock."""
    # Usar um MockDataSource limpo, sem os dados do JSON, para testes de unidade
    return UsuarioRepositoryMock(MockDataSource())

def test_create_and_get_cliente_mock(mock_usuario_repo):
    """Testa a criação e busca de um Cliente no repositório mock."""
    repo = mock_usuario_repo
    novo_cliente = Cliente(
        nome="Cliente Mock",
        cpf="111.111.111-11",
        email="cliente.mock@test.com",
        senha="123"
    )
    
    criado = repo.create(novo_cliente)
    assert criado.id is not None
    
    encontrado = repo.get_cliente_by_id(criado.id)
    assert encontrado is not None
    assert encontrado.nome == "Cliente Mock"

def test_create_and_get_funcionario_mock(mock_usuario_repo):
    """Testa a criação e busca de um Funcionario no repositório mock."""
    repo = mock_usuario_repo
    novo_funcionario = Funcionario(
        nome="Funcionario Mock",
        cpf="222.222.222-22",
        email="func.mock@test.com",
        senha="123",
        matricula="FM-01"
    )
    
    criado = repo.create(novo_funcionario)
    assert criado.id is not None
    
    encontrado = repo.get_funcionario_by_id(criado.id)
    assert encontrado is not None
    assert encontrado.matricula == "FM-01"

def test_list_all_mock(mock_usuario_repo):
    """Testa a listagem de todos os usuários no repositório mock."""
    repo = mock_usuario_repo
    repo.create(Cliente(nome="C1", cpf="c1", email="c1@m.com", senha="1"))
    repo.create(Funcionario(nome="F1", cpf="f1", email="f1@m.com", senha="1", matricula="F1"))
    
    todos = repo.list_all()
    assert len(todos) == 2
