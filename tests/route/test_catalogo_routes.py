"""
Pytest-based tests for catalogue operations (refactored from unittest).

These tests use the service layer (same approach used for alugueis tests)
and the shared `test_container` fixture to create entities and assert
business logic without depending on the HTTP layer.
"""
import pytest
from decimal import Decimal
from datetime import date

from app.models import Catalogo, Funcionario
from app.models.enums import StatusSituacao


@pytest.fixture
def setup_catalogo_entities(test_container):
    """Create a base scenario: one employee and a fresh DB Catalogo setup.

    Returns a dict with created objects and ids.
    """
    usuario_service = test_container.usuario_service
    catalogo_service = test_container.catalogo_service

    # create a funcionario (used historically by route tests)
    funcionario = usuario_service.create_funcionario(
        Funcionario(
            nome='Atendente Teste',
            cpf='12345678901',
            email='atendente@test.com',
            senha='s',
            matricula='AT001'
        )
    )

    # ensure no catalogos exist at start
    # create a catalogo helper
    def create_catalogo(titulo, plataforma=None):
        c = Catalogo(titulo=titulo)
        return catalogo_service.create(c)

    return {
        'funcionario': funcionario,
        'create_catalogo': create_catalogo,
        'catalogo_service': catalogo_service,
    }


class TestCatalogoServices:
    def test_cadastro_jogo_sucesso(self, test_container, setup_catalogo_entities):
        svc = setup_catalogo_entities['catalogo_service']
        catalogo = setup_catalogo_entities['create_catalogo']('Super Mario 64')

        assert catalogo is not None
        assert catalogo.titulo == 'Super Mario 64'
        assert getattr(catalogo, 'situacao', None) is not None

    def test_cadastro_campos_obrigatorios(self, test_container, setup_catalogo_entities):
        svc = setup_catalogo_entities['catalogo_service']
        # missing title should raise
        with pytest.raises(ValueError):
            svc.create(Catalogo(titulo=''))

    def test_cadastro_duplicidade(self, test_container, setup_catalogo_entities):
        svc = setup_catalogo_entities['catalogo_service']
        svc.create(Catalogo(titulo='Super Metroid'))
        with pytest.raises(ValueError):
            svc.create(Catalogo(titulo='Super Metroid'))

    def test_atualizar_jogo(self, test_container, setup_catalogo_entities):
        svc = setup_catalogo_entities['catalogo_service']
        created = setup_catalogo_entities['create_catalogo']('The Legend of Zelda')
        updated = svc.update(created.id, {'titulo': 'The Legend of Zelda (Classic)', 'valor_venda': 250.00})
        assert updated is not None
        assert updated.titulo == 'The Legend of Zelda (Classic)'

    def test_atualizar_duplicidade(self, test_container, setup_catalogo_entities):
        svc = setup_catalogo_entities['catalogo_service']
        c1 = setup_catalogo_entities['create_catalogo']('Doom')
        c2 = setup_catalogo_entities['create_catalogo']('Quake')
        with pytest.raises(ValueError):
            svc.update(c2.id, {'titulo': 'Doom'})

    def test_exclusao_logica(self, test_container, setup_catalogo_entities):
        svc = setup_catalogo_entities['catalogo_service']
        c = setup_catalogo_entities['create_catalogo']('Catalogo Teste')
        # inactivate
        result = svc.inactivate(c.id)
        assert result is not None
        assert getattr(result, 'situacao', None) == StatusSituacao.INDISPONIVEL.value

