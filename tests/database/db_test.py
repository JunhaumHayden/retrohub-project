import unittest
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

class TestDatabaseConnection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Inicializa a conexão com o banco de dados antes de rodar os testes."""
        # Carrega variáveis do .env caso exista
        load_dotenv()
        
        # Pega a URL do .env ou usa a conexão padrão (ideal para o Docker mapeado localmente)
        db_url = os.getenv('PG_DATABASE_URL', 'postgresql+psycopg2://admin:admin@localhost:5432/retrohub')
        
        try:
            # Cria a engine do SQLAlchemy e estabelece a conexão
            cls.engine = create_engine(db_url)
            cls.connection = cls.engine.connect()
            print("\n✅ Conexão com o banco de dados estabelecida com sucesso!")
        except Exception as e:
            cls.fail(f"Falha ao conectar no banco de dados: {e}")

    @classmethod
    def tearDownClass(cls):
        """Fecha a conexão após rodar todos os testes."""
        if hasattr(cls, 'connection'):
            cls.connection.close()
        if hasattr(cls, 'engine'):
            cls.engine.dispose()
            print("Conexão fechada.")

    def test_1_connection_is_active(self):
        """Testa se a conexão com o banco está ativa executando um simples SELECT 1."""
        result = self.connection.execute(text("SELECT 1")).scalar()
        self.assertEqual(result, 1, "O banco de dados não respondeu ao comando SELECT 1.")

    def test_2_query_usuarios_exist(self):
        """Testa se os dados de usuários populados pelo 02_data.sql foram inseridos."""
        result = self.connection.execute(text("SELECT COUNT(*) FROM usuario")).scalar()
        self.assertGreater(result, 0, "A tabela 'usuario' deveria conter dados inseridos na inicialização.")
        print(f"\n   -> Encontrados {result} usuários no banco.")

    def test_3_query_jogos_exist(self):
        """Testa se os dados de jogos populados pelo 02_data.sql existem e traz um exemplo."""
        result = self.connection.execute(text("SELECT titulo FROM jogo LIMIT 1")).scalar()
        self.assertIsNotNone(result, "A tabela 'jogo' deveria ter pelo menos um registro.")
        print(f"\n   -> Exemplo de jogo encontrado: '{result}'")

    def test_4_query_transacoes(self):
        """Testa se os relacionamentos estão funcionando consultando a tabela transacao."""
        query = """
            SELECT t.id, c.id_usuario, t.valor_total
            FROM transacao t
            JOIN cliente c ON t.id_cliente = c.id_usuario
            LIMIT 1
        """
        result = self.connection.execute(text(query)).fetchone()
        self.assertIsNotNone(result, "Deveria existir uma transação associada a um cliente.")
        print(f"\n   -> Transação encontrada. ID: {result[0]}, Valor: R${result[2]}")

if __name__ == '__main__':
    unittest.main(verbosity=2)
