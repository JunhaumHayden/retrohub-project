"""
Pytest-based tests for estoque operations (refactored from unittest).

These tests use the service/data-source layer via the shared `test_container`
fixture so they are fast and independent from the HTTP layer.
"""
import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Catalogo, Funcionario, MidiaFisica, MidiaDigital


@pytest.fixture
def setup_estoque_entities(test_container):
    """Create a base scenario: one funcionario and one catalogo.

    Returns helpers and created objects used by tests.
    """
    usuario_service = test_container.usuario_service
    catalogo_service = test_container.catalogo_service

    funcionario = usuario_service.create_funcionario(
        Funcionario(nome='Gerente Estoque', cpf='11122233344', email='estoque@t.test', senha='s', matricula='EST001')
    )

    catalogo = catalogo_service.create(Catalogo(titulo='Chrono Trigger'))

    return {
        'funcionario': funcionario,
        'catalogo': catalogo,
        'estoque_service': test_container.estoque_service,
        'data_source': test_container.catalogo_repository.data_source,
        'catalogo_service': catalogo_service
    }


class TestEstoqueServices:
    def test_cadastro_midia_fisica_sucesso(self, test_container, setup_estoque_entities):
        estoque_service = setup_estoque_entities['estoque_service']
        catalogo = setup_estoque_entities['catalogo']

        midia = estoque_service.create_exemplar(MidiaFisica(catalogo=catalogo, codigo_barras='12345-SNES-CT', estado_conservacao='BOM'))

        assert midia is not None
        assert getattr(midia, 'id', None) is not None
        assert midia.codigo_barras == '12345-SNES-CT'
        assert midia.tipo_midia == 'FISICA'

    def test_cadastro_midia_fisica_duplicada(self, test_container, setup_estoque_entities):
        estoque_service = setup_estoque_entities['estoque_service']
        catalogo = setup_estoque_entities['catalogo']

        estoque_service.create_exemplar(MidiaFisica(catalogo=catalogo, codigo_barras='UNIQUE-CODE', estado_conservacao='PERFEITO'))

        # attempting to create another with same codigo_barras should raise DB integrity error
        with pytest.raises(IntegrityError):
            estoque_service.create_exemplar(MidiaFisica(catalogo=catalogo, codigo_barras='UNIQUE-CODE', estado_conservacao='PERFEITO'))

    def test_cadastro_midia_digital_sucesso(self, test_container, setup_estoque_entities):
        estoque_service = setup_estoque_entities['estoque_service']
        catalogo = setup_estoque_entities['catalogo']

        midia = estoque_service.create_exemplar(MidiaDigital(catalogo=catalogo, chave_ativacao='XXXX-YYYY-ZZZZ'))

        assert midia is not None
        assert getattr(midia, 'id', None) is not None
        assert midia.chave_ativacao == 'XXXX-YYYY-ZZZZ'
        assert midia.tipo_midia == 'DIGITAL'

    def test_listar_estoque_do_jogo(self, test_container, setup_estoque_entities):
        estoque_service = setup_estoque_entities['estoque_service']
        ds = setup_estoque_entities['data_source']
        catalogo = setup_estoque_entities['catalogo']

        estoque_service.create_exemplar(MidiaFisica(catalogo=catalogo, codigo_barras='CT-01', estado_conservacao='RUIM'))
        estoque_service.create_exemplar(MidiaDigital(catalogo=catalogo, chave_ativacao='CT-DIG-01'))

        fisicas = ds.get_all(MidiaFisica)
        digitais = ds.get_all(MidiaDigital)

        itens = [m for m in (fisicas + digitais) if getattr(m, 'id_catalogo', None) == catalogo.id]

        assert len(itens) == 2
        tipos = {it.tipo_midia for it in itens}
        assert 'FISICA' in tipos
        assert 'DIGITAL' in tipos

    def test_atualizar_estado_fisico(self, test_container, setup_estoque_entities):
        estoque_service = setup_estoque_entities['estoque_service']
        ds = setup_estoque_entities['data_source']
        catalogo = setup_estoque_entities['catalogo']

        midia = estoque_service.create_exemplar(MidiaFisica(catalogo=catalogo, codigo_barras='CT-UPDATE', estado_conservacao='NOVO'))

        # change state and persist (use valid enum value)
        midia.set_estado_conservacao('BOM')
        ds.update(midia)

        reloaded = ds.get_by_id(type(midia), midia.id)
        assert reloaded.estado_conservacao.name == 'BOM'

    def test_exclusao_exemplar(self, test_container, setup_estoque_entities):
        estoque_service = setup_estoque_entities['estoque_service']
        ds = setup_estoque_entities['data_source']
        catalogo = setup_estoque_entities['catalogo']

        midia = estoque_service.create_exemplar(MidiaFisica(catalogo=catalogo, codigo_barras='CT-DELETE', estado_conservacao='PESSIMO'))

        deleted = ds.delete(type(midia), midia.id)
        assert deleted is True

        # ensure no exemplares remain for the catalogo
        fisicas = ds.get_all(MidiaFisica)
        digitais = ds.get_all(MidiaDigital)
        itens = [m for m in (fisicas + digitais) if getattr(m, 'id_catalogo', None) == catalogo.id]
        assert len(itens) == 0

