import os
from typing import Optional

from app.database.interfaces.data_source_interface import DataSourceInterface
from app.database.data_source.MockDataSource import MockDataSource
from app.database.data_source.PostgresDataSource import PostgresDataSource
from app.database.data_source.SQLiteDataSource import SQLiteDataSource

class DatabaseFactory:
    """
    Factory responsável por criar e fornecer a instância correta do DataSource
    com base na configuração do ambiente.
    """
    _data_source: Optional[DataSourceInterface] = None

    @classmethod
    def get_data_source(cls) -> DataSourceInterface:
        """
        Retorna uma instância singleton do DataSource configurado.
        A lógica para decidir qual fonte de dados usar (mock, postgres, etc.)
        é centralizada aqui.
        """
        if cls._data_source is None:
            db_type = os.getenv('APP_MODE', 'sqlite').lower()

            if db_type == 'mock':
                cls._data_source = MockDataSource()
            elif db_type == 'postgre':
                db_url = os.getenv('PG_DATABASE_URL')
                if not db_url:
                    raise ValueError("A variável de ambiente PG_DATABASE_URL não está definida.")
                cls._data_source = PostgresDataSource(db_url)
            elif db_type == 'postgre_test':
                db_url = os.getenv('PG_DATABASE_URL_TEST')
                if not db_url:
                    raise ValueError("A variável de ambiente PG_DATABASE_URL_TEST não está definida.")
                cls._data_source = PostgresDataSource(db_url)
            elif db_type == 'sqlite':
                # Padroniza o caminho do banco de dados para a pasta resources
                db_path = os.path.join('resources', 'database', 'sqlite', 'retrohub.db')
                db_url = os.getenv('SQLITE_DATABASE_URL', f'sqlite:///{db_path}')
                cls._data_source = SQLiteDataSource(db_url)
            else:
                raise ValueError(f"Tipo de banco de dados desconhecido: {db_type}")

            if hasattr(cls._data_source, 'load_data'):
                cls._data_source.load_data()
        
        return cls._data_source

    @classmethod
    def reset_data_source(cls):
        """
        Usado principalmente em testes para garantir que o DataSource seja
        reinicializado entre os testes, limpando dados em memória.
        """
        cls._data_source = None
