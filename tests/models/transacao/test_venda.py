import pytest
from decimal import Decimal
from app.models import Cliente, Funcionario, Catalogo, MidiaFisica, Venda, ItemTransacao
from app.models.enums import StatusVenda

# A fixture 'db_session' é injetada automaticamente pelo conftest.py

@pytest.fixture
def setup_venda(db_session):
    """Fixture para criar entidades básicas necessárias para uma venda."""
    cliente = Cliente(nome="Cliente Venda", cpf="111.222.333-44", email="venda@test.com", senha="123")
    funcionario = Funcionario(nome="Func Venda", cpf="555.666.777-88", email="func.venda@test.com", senha="123", matricula="F-VD")
    catalogo = Catalogo(titulo="Jogo para Vender")
    
    db_session.add_all([cliente, funcionario, catalogo])
    db_session.flush()

    exemplar = MidiaFisica(
        catalogo=catalogo,
        codigo_barras="VENDA-001",
        valor_venda=Decimal("250.00")
    )
    db_session.add(exemplar)
    db_session.commit()
    
    return cliente, funcionario, exemplar

def test_criar_venda_e_relacionamentos(db_session, setup_venda):
    """
    Testa a criação de uma Venda, seu ItemTransacao e a persistência
    dos relacionamentos com Cliente, Funcionario e Exemplar.
    """
    cliente, funcionario, exemplar = setup_venda

    # 1. Criar a Venda (Transacao)
    venda = Venda(
        cliente=cliente,
        funcionario=funcionario,
        valor_total=exemplar.valor_venda,
        status=StatusVenda.FINALIZADA.value
    )
    
    # 2. Criar o Item da Transação
    item = ItemTransacao(
        transacao=venda,
        exemplar=exemplar,
        valor_unitario=exemplar.valor_venda,
        quantidade=1
    )
    
    # Adicionar à sessão e salvar
    db_session.add(venda)
    db_session.add(item)
    db_session.commit()

    # 3. Verificações
    assert venda.id is not None
    assert item.id is not None
    
    # Buscar a venda do banco para verificar os relacionamentos
    venda_persistida = db_session.get(Venda, venda.id)
    
    assert venda_persistida is not None
    assert venda_persistida.tipo == "VENDA"
    assert venda_persistida.cliente.nome == "Cliente Venda"
    assert venda_persistida.funcionario.nome == "Func Venda"
    
    # Verificar o item da transação
    assert len(venda_persistida.itens_transacao) == 1
    item_persistido = venda_persistida.itens_transacao[0]
    assert item_persistido.exemplar.codigo_barras == "VENDA-001"
    assert item_persistido.valor_unitario == Decimal("250.00")
    
    # Verificar o relacionamento inverso
    assert item_persistido.transacao.id == venda_persistida.id
