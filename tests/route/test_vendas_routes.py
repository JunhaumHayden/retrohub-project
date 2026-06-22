"""
Pytest-based service-level tests for vendas (sales) routes.

These tests use the service layer (via the shared `test_container` fixture)
and avoid the HTTP layer for faster, more deterministic tests.
"""
import pytest
from decimal import Decimal
from app.models import Cliente, Catalogo, MidiaFisica, MidiaDigital


@pytest.fixture
def setup_venda_entities(test_container):
    """Create base entities for venda tests: cliente, catalogo and exemplares.

    Returns a dict with created objects and ids.
    """
    usuario_service = test_container.usuario_service
    catalogo_service = test_container.catalogo_service
    estoque_service = test_container.estoque_service
    venda_service = test_container.venda_service

    cliente = usuario_service.create_cliente(
        Cliente(
            nome="Cliente Venda",
            cpf="99988877766",
            email="venda@retrohub.com",
            senha="hash",
            dados_pagamento="Boleto"
        )
    )

    jogo = catalogo_service.create(Catalogo(titulo="Halo Combat Evolved"))

    midia_fisica = estoque_service.create_exemplar(
        MidiaFisica(
            catalogo=jogo,
            codigo_barras="XBOX-HALO-1",
            estado_conservacao="NOVO",
            valor_venda=Decimal("100.00"),
        )
    )

    midia_digital = estoque_service.create_exemplar(
        MidiaDigital(
            catalogo=jogo,
            chave_ativacao="AAAA-BBBB-CCCC",
            valor_venda=Decimal("79.90"),
        )
    )

    return {
        "cliente": cliente,
        "cliente_id": cliente.id,
        "jogo": jogo,
        "jogo_id": jogo.id,
        "midia_fisica": midia_fisica,
        "midia_digital": midia_digital,
        "venda_service": venda_service,
    }


class TestVendasServices:
    def test_solicitar_venda_fisica_sucesso(self, test_container, setup_venda_entities):
        svc = setup_venda_entities['venda_service']
        cliente_id = setup_venda_entities['cliente_id']
        jogo_id = setup_venda_entities['jogo_id']

        venda, erro = svc.criar_venda(cliente_id, jogo_id, 'FISICA')
        assert erro is None
        assert venda is not None
        assert float(venda.valor_total) == 100.00

    def test_solicitar_venda_sem_estoque(self, test_container, setup_venda_entities):
        svc = setup_venda_entities['venda_service']
        cliente_id = setup_venda_entities['cliente_id']
        jogo_id = setup_venda_entities['jogo_id']

        # First sale succeeds
        venda1, err1 = svc.criar_venda(cliente_id, jogo_id, 'FISICA')
        assert err1 is None

        # Second sale for physical media should fail because only one physical exemplar exists
        venda2, err2 = svc.criar_venda(cliente_id, jogo_id, 'FISICA')
        assert venda2 is None
        assert err2 is not None
        assert "Não há exemplares" in err2

    def test_listar_minhas_vendas(self, test_container, setup_venda_entities):
        svc = setup_venda_entities['venda_service']
        cliente_id = setup_venda_entities['cliente_id']
        jogo_id = setup_venda_entities['jogo_id']

        venda, err = svc.criar_venda(cliente_id, jogo_id, 'DIGITAL')
        assert err is None
        assert venda is not None
        assert getattr(venda, 'id', None) is not None
        assert getattr(venda, 'id_cliente', None) == cliente_id

        vendas = svc.get_by_cliente(cliente_id)
        assert isinstance(vendas, list)
        assert len(vendas) == 1

    def test_estornar_venda(self, test_container, setup_venda_entities):
        svc = setup_venda_entities['venda_service']
        cliente_id = setup_venda_entities['cliente_id']
        jogo_id = setup_venda_entities['jogo_id']

        venda, err = svc.criar_venda(cliente_id, jogo_id, 'DIGITAL')
        assert err is None
        assert venda is not None
        assert getattr(venda, 'id_cliente', None) == cliente_id

        success, err = svc.estornar_venda(venda.id, cliente_id)
        assert success is True
        assert err is None
