import os
from dotenv import load_dotenv

from app.database.factories.database_factory import DatabaseFactory
from app.database.base_model import Base
from app.models import * # Importa todos os modelos para que o SQLAlchemy os conheça

def initialize_database():
    """
    Inicializa o banco de dados com base na configuração do ambiente.
    Cria todas as tabelas definidas nos modelos ORM.
    """
    print("Carregando variáveis de ambiente...")
    load_dotenv()

    # Força o uso do SQLite para este script, ou usa o que estiver no .env
    os.environ['APP_MODE'] = os.getenv('APP_MODE', 'sqlite')
    print(f"Modo da aplicação definido como: {os.environ['APP_MODE']}")

    print("Obtendo DataSource da Factory...")
    data_source = DatabaseFactory.get_data_source()

    if not hasattr(data_source, 'engine'):
        print("O DataSource selecionado não é uma instância de banco de dados relacional (não possui 'engine').")
        print("O modo 'mock' não requer inicialização de banco de dados.")
        return

    print("Conectando ao banco de dados e criando tabelas...")
    try:
        # Acessa a engine do SQLAlchemy dentro do DataSource
        engine = data_source.engine
        
        # Apaga todas as tabelas existentes (para um início limpo)
        print("Apagando tabelas existentes (se houver)...")
        Base.metadata.drop_all(bind=engine)
        
        # Cria todas as tabelas
        print("Criando novas tabelas...")
        Base.metadata.create_all(bind=engine)
        
        print("Banco de dados inicializado com sucesso!")
        print(f"Arquivo do banco de dados deve estar em: {engine.url.database}")

    except Exception as e:
        print(f"Ocorreu um erro ao inicializar o banco de dados: {e}")

if __name__ == "__main__":
    initialize_database()
