import pytest
from app.models import Catalogo
from app.repository.db.catalogo_repository_db import CatalogoRepositoryDB

def test_create_and_get_catalogo(db_session):
    """Testa a criação e busca de um item do Catálogo."""
    repo = CatalogoRepositoryDB(db_session)
    novo_item = Catalogo(
        titulo="Jogo de Teste",
        descricao="Um jogo para testar o repositório.",
        genero="Teste",
        classificacao="Livre"
    )
    
    # Criar
    criado = repo.create(novo_item)
    assert criado.id is not None
    assert criado.titulo == "Jogo de Teste"

    # Buscar por ID
    encontrado = repo.get_by_id(criado.id)
    assert encontrado is not None
    assert encontrado.titulo == "Jogo de Teste"

def test_update_catalogo(db_session):
    """Testa a atualização de um item do Catálogo."""
    repo = CatalogoRepositoryDB(db_session)
    item = Catalogo(titulo="Título Original")
    criado = repo.create(item)
    
    # Atualizar
    criado.titulo = "Título Atualizado"
    atualizado = repo.update(criado)
    
    assert atualizado.titulo == "Título Atualizado"
    
    # Verificar se a atualização persistiu
    encontrado = repo.get_by_id(criado.id)
    assert encontrado.titulo == "Título Atualizado"

def test_delete_catalogo(db_session):
    """Testa a exclusão de um item do Catálogo."""
    repo = CatalogoRepositoryDB(db_session)
    item = Catalogo(titulo="Para Deletar")
    criado = repo.create(item)
    
    # Deletar
    deletado = repo.delete(criado.id)
    assert deletado is True
    
    # Verificar se foi deletado
    encontrado = repo.get_by_id(criado.id)
    assert encontrado is None

def test_list_all_catalogo(db_session):
    """Testa a listagem de todos os itens do Catálogo."""
    repo = CatalogoRepositoryDB(db_session)
    
    repo.create(Catalogo(titulo="Jogo 1"))
    repo.create(Catalogo(titulo="Jogo 2"))
    
    todos = repo.list_all()
    assert len(todos) == 2

def test_get_by_title(db_session):
    """Testa a busca de um item do Catálogo pelo título."""
    repo = CatalogoRepositoryDB(db_session)
    repo.create(Catalogo(titulo="Jogo Único"))
    
    encontrado = repo.get_by_title("Jogo Único")
    assert encontrado is not None
    assert encontrado.titulo == "Jogo Único"
    
    nao_encontrado = repo.get_by_title("Título Inexistente")
    assert nao_encontrado is None
