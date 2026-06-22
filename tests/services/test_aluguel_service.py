import pytest
from datetime import date, timedelta
from decimal import Decimal

from app.models import Cliente, Funcionario, Catalogo, MidiaFisica, Aluguel
from app.services.aluguel_service import AluguelService
from app.services.usuario_service import UsuarioService
from app.services.catalogo_service import CatalogoService
from app.services.estoque_service import EstoqueService
from app.models.enums import StatusAluguel

# A fixture 'test_container' é injetada automaticamente pelo conftest.py

@pytest.fixture
def setup_entities(test_container):
    """
    Cria entidades básicas usando os serviços do container, garantindo que
    tudo opere na mesma sessão de banco de dados gerenciada pelo container.
    """
    usuario_service: UsuarioService = test_container.usuario_service
    catalogo_service: CatalogoService = test_container.catalogo_service
    estoque_service: EstoqueService = test_container.estoque_service
    
    # O repositório agora gerencia o commit, então não precisamos mais de db_session.commit()
    cliente = usuario_service.create_cliente(Cliente(nome="Cliente Teste", cpf="123", email="c@t.com", senha="s"))
    funcionario = usuario_service.create_funcionario(Funcionario(nome="Func Teste", cpf="456", email="f@t.com", senha="s", matricula="F1"))
    catalogo = catalogo_service.create(Catalogo(titulo="Jogo Teste"))
    
    exemplar = estoque_service.create_exemplar(MidiaFisica(
        catalogo=catalogo,
        codigo_barras="AL-123",
        valor_diaria_aluguel=Decimal("10.0")
    ))
    
    return {
        "cliente_id": cliente.id,
        "funcionario_id": funcionario.id,
        "catalogo_id": catalogo.id,
        "exemplar_id": exemplar.id
    }

def test_fluxo_completo_aluguel(test_container, setup_entities):
    """Testa o fluxo completo de um aluguel usando o serviço com uma sessão de DB."""
    aluguel_service: AluguelService = test_container.aluguel_service

    # 1. Solicitar Aluguel
    aluguel, erro = aluguel_service.solicitar_aluguel(
        id_cliente=setup_entities["cliente_id"],
        id_catalogo=setup_entities["catalogo_id"],
        dias_alugados=3,
        data_inicio=date.today(),
        tipo_midia="FISICA"
    )
    assert erro is None
    assert aluguel is not None
    assert aluguel.status == StatusAluguel.SOLICITADO.value

    # 2. Processar Pagamento
    aluguel, erro = aluguel_service.processar_pagamento(aluguel.id, sucesso=True)
    assert erro is None
    assert aluguel.status == StatusAluguel.APROVADO.value

    # 3. Registrar Retirada
    aluguel, erro = aluguel_service.registrar_retirada(aluguel.id)
    assert erro is None
    assert aluguel.status == StatusAluguel.ATIVO.value

    # 4. Registrar Devolução
    aluguel, erro = aluguel_service.registrar_devolucao(aluguel.id, "bom", setup_entities["funcionario_id"])
    assert erro is None
    assert aluguel.status == StatusAluguel.FINALIZADO.value
