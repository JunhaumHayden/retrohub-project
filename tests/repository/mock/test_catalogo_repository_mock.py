import pytest
from app.models import Catalogo
from app.repository.mock.catalogo_repository_mock import CatalogoRepositoryMock
from app.database.data_source.MockDataSource import MockDataSource

@pytest.fixture
def mock_catalogo_repo():
    """Fixture para fornecer uma instância limpa do repositório mock de catálogo."""
    return CatalogoRepositoryMock(MockDataSource())

def test_create_and_get_catalogo_mock(mock_catalogo_repo):
    """Testa a criação e busca de um item do Catálogo no repositório mock."""
    repo = mock_catalogo_repo
    novo_item = Catalogo(titulo="Jogo Mock")
    
    criado = repo.create(novo_item)
    assert criado.id is not None
    
    encontrado = repo.get_by_id(criado.id)
    assert encontrado is not None
    assert encontrado.titulo == "Jogo Mock"

def test_get_by_title_mock(mock_catalogo_repo):
    """Testa a busca por título no repositório mock."""
    repo = mock_catalogo_repo
    repo.create(Catalogo(titulo="Título Único"))
    
    encontrado = repo.get_by_title("Título Único")
    assert encontrado is not None
    
    nao_encontrado = repo.get_by_title("Inexistente")
    assert nao_encontrado is None

def test_list_all_mock(mock_catalogo_repo):
    """Testa a listagem de todos os itens no repositório mock."""
    repo = mock_catalogo_repo
    repo.create(Catalogo(titulo="Jogo A"))
    repo.create(Catalogo(titulo="Jogo B"))
    
    todos = repo.list_all()
    assert len(todos) == 2
