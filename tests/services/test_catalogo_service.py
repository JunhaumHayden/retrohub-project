import pytest
from app.models import Catalogo
from app.services.catalogo_service import CatalogoService
from app.models.enums import StatusSituacao

# A fixture 'test_container' é injetada automaticamente pelo conftest.py

def test_create_and_get_catalogo(test_container):
    """Testa a criação e busca de um item do Catálogo usando o DB."""
    catalogo_service = test_container.catalogo_service
    
    novo_item = Catalogo(
        titulo="Jogo de Teste DB",
        descricao="Um jogo para testar o serviço.",
        genero="Teste DB",
        classificacao="Livre",
        situacao=StatusSituacao.DISPONIVEL.value
    )
    
    criado = catalogo_service.create(novo_item)
    assert criado.id is not None
    
    encontrado = catalogo_service.get_by_id(criado.id)
    assert encontrado is not None
    assert encontrado.titulo == "Jogo de Teste DB"

def test_update_catalogo(test_container):
    """Testa a atualização de um item do Catálogo usando o DB."""
    catalogo_service = test_container.catalogo_service
    item = Catalogo(titulo="Título Original DB")
    criado = catalogo_service.create(item)
    
    dados_update = {"titulo": "Título Atualizado DB"}
    atualizado = catalogo_service.update(criado.id, dados_update)
    
    assert atualizado.titulo == "Título Atualizado DB"
    
    encontrado = catalogo_service.get_by_id(criado.id)
    assert encontrado.titulo == "Título Atualizado DB"

def test_inactivate_and_activate_catalogo(test_container):
    """Testa a inativação e ativação de um item do Catálogo."""
    catalogo_service = test_container.catalogo_service
    item = Catalogo(titulo="Jogo Ativo/Inativo", situacao=StatusSituacao.DISPONIVEL.value)
    criado = catalogo_service.create(item)
    
    # Inativar
    inativado = catalogo_service.inactivate(criado.id)
    assert inativado.situacao == StatusSituacao.INDISPONIVEL.value
    
    # Ativar
    ativado = catalogo_service.activate(criado.id)
    assert ativado.situacao == StatusSituacao.DISPONIVEL.value

def test_get_estoque_disponivel(test_container):
    """Testa o cálculo de estoque disponível pelo serviço."""
    catalogo_service = test_container.catalogo_service
    # Este teste é mais complexo e dependeria da criação de exemplares.
    # Por enquanto, vamos testar o caso simples de um catálogo sem exemplares.
    
    novo_item = Catalogo(titulo="Jogo Sem Estoque")
    criado = catalogo_service.create(novo_item)
    
    estoque = catalogo_service.get_estoque_disponivel(criado.id)
    assert estoque == 0
