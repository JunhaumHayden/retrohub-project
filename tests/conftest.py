import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os

# Garante que o modo de teste seja 'sqlite' para todas as execuções de teste
os.environ['APP_MODE'] = 'sqlite'

from app.database.base_model import Base
from app.models import * # Importa todos os modelos para que o SQLAlchemy os conheça
from app.container.container import Container
from app.database.data_source.SQLiteDataSource import SQLiteDataSource

@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Fixture do Pytest que cria e fornece uma sessão de banco de dados SQLite em memória
    para cada função de teste. Garante isolamento total entre os testes.
    """
    # Usa um banco de dados SQLite em memória
    engine = create_engine("sqlite:///:memory:")

    # Cria todas as tabelas definidas nos modelos que herdam de Base
    Base.metadata.create_all(engine)

    # Cria uma fábrica de sessões ligada à engine de teste
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        # Garante que a sessão seja fechada e o banco de dados limpo após o teste
        session.close()
        Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def test_container(db_session: Session) -> Container:
    """
    Fornece uma instância do Container configurada para usar um banco de dados
    de teste em memória.
    """
    # 1. Cria uma instância limpa do container
    container = Container()
    container.reset() # Garante que não há singletons de execuções anteriores

    # 2. Cria um DataSource que usa a sessão do teste atual
    test_data_source = SQLiteDataSource(db_url="sqlite:///:memory:")
    test_data_source.engine = db_session.get_bind()
    # Garante que o DataSource use a mesma sessão do teste
    test_data_source.SessionLocal = lambda: db_session

    # 3. Injeta o DataSource de teste diretamente no container
    # Isso sobrescreve a lógica padrão do container.data_source
    container._data_source = test_data_source
    
    yield container
    
    # Limpeza após o teste
    container.reset()
