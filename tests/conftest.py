import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base_model import Base
from app.models import * # Importa todos os modelos para que o SQLAlchemy os conheça

@pytest.fixture(scope="function")
def db_session():
    """
    Fixture do Pytest para criar um banco de dados SQLite em memória para cada função de teste.
    Garante que os testes sejam isolados e não interfiram uns com os outros.
    """
    # Usa um banco de dados SQLite em memória para os testes
    engine = create_engine("sqlite:///:memory:")
    
    # Cria todas as tabelas definidas nos modelos que herdam de Base
    Base.metadata.create_all(engine)
    
    # Cria uma fábrica de sessões
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Cria a sessão
    session = SessionLocal()
    
    try:
        yield session
    finally:
        # Garante que a sessão seja fechada e o banco de dados limpo após o teste
        session.close()
        Base.metadata.drop_all(engine)
