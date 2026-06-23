import pytest
from decimal import Decimal
from app.models import Catalogo, Exemplar, MidiaFisica, MidiaDigital
from app.models.enums import StatusSituacao

# A fixture 'db_session' é injetada automaticamente pelo conftest.py

@pytest.fixture
def catalogo_teste(db_session):
    """Fixture para criar um item de catálogo base para os testes de exemplar."""
    catalogo = Catalogo(
        titulo="Jogo Base para Exemplares",
        situacao=StatusSituacao.DISPONIVEL
    )
    db_session.add(catalogo)
    db_session.commit()
    return catalogo

def test_criar_midia_fisica(db_session, catalogo_teste):
    """Testa a criação e persistência de uma MidiaFisica."""
    midia_fisica = MidiaFisica(
        catalogo=catalogo_teste,
        codigo_barras="FIS-001",
        valor_diaria_aluguel=Decimal("9.99")
    )
    
    db_session.add(midia_fisica)
    db_session.commit()
    
    assert midia_fisica.id is not None
    assert midia_fisica.tipo_midia == "FISICA"
    assert midia_fisica.catalogo.titulo == "Jogo Base para Exemplares"
    
    # Verifica se o SQLAlchemy consegue buscar o objeto pelo ID do exemplar
    encontrado = db_session.get(Exemplar, midia_fisica.id)
    assert isinstance(encontrado, MidiaFisica)
    assert encontrado.codigo_barras == "FIS-001"

def test_criar_midia_digital(db_session, catalogo_teste):
    """Testa a criação e persistência de uma MidiaDigital."""
    midia_digital = MidiaDigital(
        catalogo=catalogo_teste,
        chave_ativacao="DIG-001",
        valor_venda=Decimal("199.99")
    )
    
    db_session.add(midia_digital)
    db_session.commit()
    
    assert midia_digital.id is not None
    assert midia_digital.tipo_midia == "DIGITAL"
    
    encontrado = db_session.get(Exemplar, midia_digital.id)
    assert isinstance(encontrado, MidiaDigital)
    assert encontrado.chave_ativacao == "DIG-001"

def test_consulta_polimorfica_de_exemplares(db_session, catalogo_teste):
    """Testa se a consulta por Exemplar retorna ambas as mídias (física e digital)."""
    db_session.add(MidiaFisica(catalogo=catalogo_teste, codigo_barras="POLI-FIS-001"))
    db_session.add(MidiaDigital(catalogo=catalogo_teste, chave_ativacao="POLI-DIG-001"))
    db_session.commit()
    
    # Consulta todos os exemplares associados ao catálogo
    exemplares_do_catalogo = db_session.query(Exemplar).filter_by(id_catalogo=catalogo_teste.id).all()
    
    assert len(exemplares_do_catalogo) == 2
    
    tipos_encontrados = {type(ex) for ex in exemplares_do_catalogo}
    assert MidiaFisica in tipos_encontrados
    assert MidiaDigital in tipos_encontrados

def test_relacionamento_catalogo_exemplares(db_session, catalogo_teste):
    """Testa a coleção 'exemplares' no objeto Catalogo."""
    catalogo = db_session.get(Catalogo, catalogo_teste.id)
    
    catalogo.exemplares.append(MidiaFisica(codigo_barras="REL-001"))
    catalogo.exemplares.append(MidiaDigital(chave_ativacao="REL-002"))
    
    db_session.commit()
    
    # Recarrega o objeto para garantir que a coleção foi persistida
    catalogo_recarregado = db_session.get(Catalogo, catalogo_teste.id)
    
    assert len(catalogo_recarregado.exemplares) == 2
    assert isinstance(catalogo_recarregado.exemplares[0], MidiaFisica)
    assert catalogo_recarregado.exemplares[1].catalogo.id == catalogo_recarregado.id


def test_maquina_estados_exemplar_disponivel_indisponivel():
    exemplar = Exemplar(id_catalogo=1, tipo_midia="FISICA", situacao=StatusSituacao.DISPONIVEL)

    exemplar.registrar_retirada()
    assert exemplar.situacao == StatusSituacao.INDISPONIVEL

    exemplar.registrar_devolucao()
    assert exemplar.situacao == StatusSituacao.DISPONIVEL

    with pytest.raises(ValueError, match="não está disponível"):
        exemplar.registrar_retirada()
        exemplar.registrar_retirada()
