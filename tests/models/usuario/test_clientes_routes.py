import unittest
from app import create_app
from app.database.database_config import Base
from app.database.factories.database_manager import DatabaseManager
from app.models import Cliente

class TestClientesRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Inicializa a aplicação Flask injetando um banco SQLite em memória para testes super rápidos."""
        test_config = {
            'db_type': 'sqlite',
            'db_url': 'sqlite:///:memory:'
        }
        cls.app = create_app(test_config=test_config)
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
        
        # Como usamos o mesmo DatabaseManager, ele agora está plugado no sqlite:///:memory:
        session = DatabaseManager.get_session()
        engine = session.bind
        Base.metadata.create_all(engine)

    @classmethod
    def tearDownClass(cls):
        """Fecha as conexões ao final da bateria de testes."""
        session = DatabaseManager.get_session()
        engine = session.bind
        Base.metadata.drop_all(engine)
        session.close()

    def setUp(self):
        """Antes de cada teste, limpa os registros para evitar interferência entre os testes (Isolamento)."""
        session = DatabaseManager.get_session()
        session.query(Cliente).delete()
        session.commit()

    def test_1_cadastro_cliente_sucesso(self):
        """Testa o fluxo feliz: Cadastro válido (status 201)."""
        payload = {
            "nome": "Bruce Wayne",
            "cpf": "12345678900",
            "email": "batman@wayne.com",
            "senha": "super_secret_password",
            "data_nascimento": "1990-05-15"
        }
        response = self.client.post('/api/clientes/cadastro', json=payload)
        self.assertEqual(response.status_code, 201)
        
        data = response.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['nome'], "Bruce Wayne")
        self.assertNotIn('senha', data)  # Segurança: A senha NUNCA deve ser retornada no JSON da API

    def test_2_cadastro_cliente_menor_idade(self):
        """Testa a barreira de negócio: Idade < 18 (status 400)."""
        payload = {
            "nome": "Robin",
            "cpf": "12345678901",
            "email": "robin@wayne.com",
            "senha": "123",
            "data_nascimento": "2020-01-01"  # Idade visivelmente menor que 18
        }
        response = self.client.post('/api/clientes/cadastro', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('erro', response.get_json())
        self.assertIn('18 anos', response.get_json()['erro'])

    def test_3_cadastro_email_duplicado(self):
        """Testa a restrição de banco: Email único (status 400)."""
        payload = {
            "nome": "Clark Kent",
            "cpf": "99999999999",
            "email": "superman@dailyplanet.com",
            "senha": "kryptonita_is_bad",
            "data_nascimento": "1980-01-01"
        }
        # 1. Cria o primeiro (deve dar 201)
        self.client.post('/api/clientes/cadastro', json=payload)
        
        # 2. Tenta criar de novo com o mesmo email (mas CPF diferente para não estourar no CPF primeiro)
        payload['cpf'] = "88888888888" 
        response = self.client.post('/api/clientes/cadastro', json=payload)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['erro'], "E-mail já cadastrado.")

    def test_4_listar_clientes(self):
        """Testa o GET Listar clientes (status 200)."""
        response = self.client.get('/api/clientes/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    def test_5_fluxo_excluir_cliente(self):
        """Testa o fluxo completo de integrar CREATE, DELETE e buscar por ID 404."""
        # 1. Cria
        payload = {
            "nome": "Barry Allen",
            "cpf": "11111111111",
            "email": "flash@starlabs.com",
            "senha": "fast",
            "data_nascimento": "1995-10-10"
        }
        res_create = self.client.post('/api/clientes/cadastro', json=payload)
        client_id = res_create.get_json()['id']
        
        # 2. Exclui (DELETE)
        res_delete = self.client.delete(f'/api/clientes/{client_id}')
        self.assertEqual(res_delete.status_code, 200)
        
        # 3. Tenta buscar (GET ONE) - Deve retornar 404 pois foi excluído
        res_get = self.client.get(f'/api/clientes/{client_id}')
        self.assertEqual(res_get.status_code, 404)

if __name__ == '__main__':
    unittest.main(verbosity=2)
