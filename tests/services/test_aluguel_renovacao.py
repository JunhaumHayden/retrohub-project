import pytest
from datetime import date
from decimal import Decimal
from app.models.enums import StatusAluguel
from app.models import Cliente, Funcionario, Catalogo, MidiaFisica

@pytest.fixture
def setup_entities_local(test_container):
    usuario_service = test_container.usuario_service
    catalogo_service = test_container.catalogo_service
    estoque_service = test_container.estoque_service
    
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

def test_renovacao_aluguel(test_container, setup_entities_local):
    aluguel_service = test_container.aluguel_service
    cliente_id = setup_entities_local["cliente_id"]
    
    aluguel, erro = aluguel_service.solicitar_aluguel(
        id_cliente=cliente_id,
        id_catalogo=setup_entities_local["catalogo_id"],
        dias_alugados=3,
        data_inicio=date.today(),
        tipo_midia="FISICA"
    )
    assert erro is None
    print(f"\nAluguel id_cliente after solicitar_aluguel: {aluguel.id_cliente}")
    
    aluguel, erro = aluguel_service.processar_pagamento(aluguel.id, sucesso=True)
    assert erro is None
    print(f"Aluguel id_cliente after processar_pagamento: {aluguel.id_cliente}")
    
    aluguel, erro = aluguel_service.registrar_retirada(aluguel.id)
    assert erro is None
    print(f"Aluguel id_cliente after retirada: {aluguel.id_cliente}")
    
    aluguel_renovado, erro = aluguel_service.renovar_aluguel(aluguel.id, cliente_id, 2)
    assert erro is None, f"Erro na renovação: {erro}"
    assert aluguel_renovado is not None
