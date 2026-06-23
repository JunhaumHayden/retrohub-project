import pytest
from app.models import Funcionario, Catalogo, MidiaFisica, MidiaDigital
from app.models.enums import StatusSituacao

def test_1_cadastro_catalogo_sucesso(db_session):
    """Testa o cadastro válido (status 201) e a persistência no DB em memória."""
    data = {
        "titulo": "Super Mario 64",
        "situacao": StatusSituacao.DISPONIVEL,
        "descricao": "O primeiro jogo 3D do Mario",
        "classificacao": "Livre",
        "genero": "Plataforma"
    }

    # Criar instância do Catalogo
    catalogo = Catalogo(
        titulo=data.get('titulo'),
        situacao=data.get('situacao'),
        descricao=data.get('descricao'),
        classificacao=data.get('classificacao'),
        genero=data.get('genero')
    )

    db_session.add(catalogo)
    db_session.commit()

    # Verificar se os atributos foram definidos e salvos corretamente
    assert catalogo.id is not None
    assert catalogo.titulo == "Super Mario 64"

    # Testar representação string
    repr_str = repr(catalogo)
    assert "id" in repr_str
    assert "titulo" in repr_str

def test_2_relacionamento_catalogo_exemplares(db_session):
    """Testa a agregação e navegação entre Catalogo e seus Exemplares (físico e digital)."""
    catalogo = Catalogo(
        titulo="The Legend of Zelda",
        situacao=StatusSituacao.DISPONIVEL
    )
    db_session.add(catalogo)
    db_session.flush() # Para gerar o ID do catálogo sem commitar a transação

    # Instanciando as subclasses
    exemplar_fisico = MidiaFisica(
        id_exemplar=1, # Fake ID just for testing relationship mapping
        codigo_barras="ZELDA-001",
        catalogo=catalogo
    )
    
    exemplar_digital = MidiaDigital(
        id_exemplar=2,
        chave_ativacao="ZELDA-DIGITAL",
        catalogo=catalogo
    )

    # Adicionando os objetos à lista do catálogo
    catalogo.exemplares.append(exemplar_fisico)
    catalogo.exemplares.append(exemplar_digital)

    db_session.commit()

    # Verifica se o catálogo "conhece" os exemplares
    assert len(catalogo.exemplares) == 2

    # Verifica se a navegação inversa ocorreu automaticamente
    assert exemplar_fisico.catalogo == catalogo
    assert exemplar_digital.catalogo.titulo == "The Legend of Zelda"
