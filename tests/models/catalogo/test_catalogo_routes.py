import unittest
from app import create_app
from app.database.database_config import Base
from app.database.factories.database_manager import DatabaseManager
from app.models import Funcionario, Usuario, Catalogo

class TestCatalogoRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Inicializa a aplicação Flask com banco em memória."""
        test_config = {
            'db_type': 'sqlite',
            'db_url': 'sqlite:///:memory:'
        }
        cls.app = create_app(test_config=test_config)
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
        
        session = DatabaseManager.get_session()
        engine = session.bind
        Base.metadata.create_all(engine)
        session.close()

    @classmethod
    def tearDownClass(cls):
        """Fecha as conexões ao final de tudo."""
        session = DatabaseManager.get_session()
        engine = session.bind
        Base.metadata.drop_all(engine)
        session.close()

    def setUp(self):
        """Antes de cada teste, limpa as tabelas e recria o cenário base."""
        session = DatabaseManager.get_session()
        
        session.query(Catalogo).delete()
        session.query(Funcionario).delete()
        session.query(Usuario).delete()
        session.commit()
        
        self.funcionario = Funcionario(
            nome="Atendente Teste",
            cpf="12345678901",
            email="atendente@retrohub.com",
            senha="hash",
            matricula="AT001",
            cargo="Atendente",
            setor="Vendas"
        )
        session.add(self.funcionario)
        session.commit()
        
        self.func_id = self.funcionario.id_usuario
        self.headers = {'X-Funcionario-Id': str(self.func_id)}
        session.close()

    def test_1_cadastro_jogo_sucesso(self):
        """Testa o cadastro válido por um funcionário (status 201)."""
        payload = {
            "titulo": "Super Mario 64",
            "plataforma": "Nintendo 64",
            "descricao": "O primeiro jogo 3D do Mario",
            "ativo": True,
            "genero": "Plataforma",
            "classificacao": "Livre",
            "valor_venda": 150.00,
            "valor_diaria_aluguel": 5.00
        }
        response = self.client.post('/api/catalogo/itens/', json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['titulo'], "Super Mario 64")

    def test_2_cadastro_campos_obrigatorios(self):
        """Testa a validação de campos obrigatórios."""
        payload = {
            "titulo": "", # Título vazio
            "plataforma": "Nintendo 64"
        }
        response = self.client.post('/api/catalogo/itens/', json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("obrigatório", response.get_json()['erro'])

    def test_3_cadastro_duplicidade(self):
        """Testa a prevenção contra duplicidade (título + plataforma)."""
        payload = {
            "titulo": "Super Metroid",
            "plataforma": "SNES"
        }
        # 1. Cria o primeiro (deve dar 201)
        self.client.post('/api/catalogo/itens/', json=payload, headers=self.headers)
        
        # 2. Tenta criar de novo com o mesmo titulo e plataforma
        response = self.client.post('/api/catalogo/itens/', json=payload, headers=self.headers)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("já está cadastrado", response.get_json()['erro'])

    def test_4_atualizar_jogo(self):
        """Testa a atualização de um item do catálogo (status 200)."""
        # Cria
        payload = {
            "titulo": "The Legend of Zelda",
            "plataforma": "NES"
        }
        res_create = self.client.post('/api/catalogo/itens/', json=payload, headers=self.headers)
        jogo_id = res_create.get_json()['id']
        
        # Atualiza
        update_payload = {
            "titulo": "The Legend of Zelda (Classic)",
            "valor_venda": 250.00
        }
        res_update = self.client.put(f'/api/catalogo/itens/{jogo_id}', json=update_payload, headers=self.headers)
        self.assertEqual(res_update.status_code, 200)
        data = res_update.get_json()
        self.assertEqual(data['titulo'], "The Legend of Zelda (Classic)")
        self.assertEqual(data['valor_venda'], 250.0)

    def test_5_atualizar_duplicidade(self):
        """Testa a prevenção de duplicidade na atualização."""
        # Cria Catalogo 1
        self.client.post('/api/catalogo/itens/', json={"titulo": "Doom", "plataforma": "PC"}, headers=self.headers)
        # Cria Catalogo 2
        res2 = self.client.post('/api/catalogo/itens/', json={"titulo": "Quake", "plataforma": "PC"}, headers=self.headers)
        jogo2_id = res2.get_json()['id']
        
        # Tenta atualizar o Catalogo 2 para ter o mesmo titulo e plataforma do Catalogo 1
        res_update = self.client.put(f'/api/catalogo/itens/{jogo2_id}', json={"titulo": "Doom"}, headers=self.headers)
        self.assertEqual(res_update.status_code, 400)
        self.assertIn("Já existe outro jogo", res_update.get_json()['erro'])

    def test_6_exclusao_logica(self):
        """Testa a exclusão (que na verdade inativa o jogo)."""
        payload = {
            "titulo": "Jogo Teste",
            "plataforma": "PC"
        }
        res_create = self.client.post('/api/catalogo/itens/', json=payload, headers=self.headers)
        jogo_id = res_create.get_json()['id']
        
        # Exclui
        res_delete = self.client.delete(f'/api/catalogo/itens/{jogo_id}', headers=self.headers)
        self.assertEqual(res_delete.status_code, 200)
        
        # Busca o jogo e verifica se 'ativo' é False
        res_get = self.client.get(f'/api/catalogo/itens/{jogo_id}')
        self.assertEqual(res_get.status_code, 200)
        self.assertFalse(res_get.get_json()['ativo'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
