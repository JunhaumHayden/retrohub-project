import unittest
from app import create_app
from app.database.database_config import Base
from app.database.factories.database_manager import DatabaseManager
from app.models import Funcionario, Usuario, Jogo, Exemplar, MidiaFisica, MidiaDigital, Transacao, ItemTransacao

class TestEstoqueRoutes(unittest.TestCase):
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
        
        session.query(ItemTransacao).delete()
        session.query(Transacao).delete()
        session.query(MidiaFisica).delete()
        session.query(MidiaDigital).delete()
        session.query(Exemplar).delete()
        session.query(Jogo).delete()
        session.query(Funcionario).delete()
        session.query(Usuario).delete()
        session.commit()
        
        # Mock de um funcionário autorizado
        self.funcionario = Funcionario(
            nome="Gerente de Estoque",
            cpf="11122233344",
            email="estoque@retrohub.com",
            senha="hash",
            matricula="EST001",
            cargo="Gerente",
            setor="Estoque"
        )
        session.add(self.funcionario)
        
        # Mock de um jogo na vitrine
        self.jogo = Jogo(
            titulo="Chrono Trigger",
            plataforma="SNES",
            valor_venda=200.00
        )
        session.add(self.jogo)
        
        session.commit()
        
        self.func_id = self.funcionario.id_usuario
        self.jogo_id = self.jogo.id
        self.headers = {'X-Funcionario-Id': str(self.func_id)}
        session.close()

    def test_1_cadastro_midia_fisica_sucesso(self):
        """Testa o cadastro de um cartucho físico (201 Created)."""
        payload = {
            "id_jogo": self.jogo_id,
            "codigo_barras": "12345-SNES-CT",
            "estado_conservacao": "BOM"
        }
        response = self.client.post('/api/estoque/fisico', json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['codigo_barras'], "12345-SNES-CT")
        self.assertEqual(data['tipo_midia'], "FISICA")

    def test_2_cadastro_midia_fisica_duplicada(self):
        """Testa prevenção de código de barras duplicado (400 Bad Request)."""
        payload = {
            "id_jogo": self.jogo_id,
            "codigo_barras": "UNIQUE-CODE",
            "estado_conservacao": "PERFEITO"
        }
        self.client.post('/api/estoque/fisico', json=payload, headers=self.headers)
        
        # Envia o mesmo código
        response = self.client.post('/api/estoque/fisico', json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("já está cadastrado", response.get_json()['erro'])

    def test_3_cadastro_midia_digital_sucesso(self):
        """Testa o cadastro de uma chave digital (201 Created)."""
        payload = {
            "id_jogo": self.jogo_id,
            "chave_ativacao": "XXXX-YYYY-ZZZZ",
            "data_expiracao": "2030-12-31"
        }
        response = self.client.post('/api/estoque/digital', json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['chave_ativacao'], "XXXX-YYYY-ZZZZ")
        self.assertEqual(data['tipo_midia'], "DIGITAL")

    def test_4_listar_estoque_do_jogo(self):
        """Testa o retorno de todos os exemplares de um jogo (200 OK)."""
        # Cadastra 1 Físico e 1 Digital
        self.client.post('/api/estoque/fisico', json={"id_jogo": self.jogo_id, "codigo_barras": "CT-01", "estado_conservacao": "RUIM"}, headers=self.headers)
        self.client.post('/api/estoque/digital', json={"id_jogo": self.jogo_id, "chave_ativacao": "CT-DIG-01"}, headers=self.headers)
        
        response = self.client.get(f'/api/estoque/jogo/{self.jogo_id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        
        # Verifica o polimorfismo do retorno (cada um com seus campos)
        tipos = [item['tipo_midia'] for item in data]
        self.assertIn("FISICA", tipos)
        self.assertIn("DIGITAL", tipos)

    def test_5_atualizar_estado_fisico(self):
        """Testa a atualização do estado de conservação (200 OK)."""
        res_create = self.client.post('/api/estoque/fisico', json={"id_jogo": self.jogo_id, "codigo_barras": "CT-UPDATE", "estado_conservacao": "NOVO"}, headers=self.headers)
        midia_id = res_create.get_json()['id']
        
        res_update = self.client.put(f'/api/estoque/fisico/{midia_id}', json={"estado_conservacao": "BOM COM PEQUENOS ARRANHÕES"}, headers=self.headers)
        self.assertEqual(res_update.status_code, 200)
        self.assertEqual(res_update.get_json()['estado_conservacao'], "BOM COM PEQUENOS ARRANHÕES")

    def test_6_exclusao_exemplar(self):
        """Testa a exclusão de um exemplar que não tem transações (200 OK)."""
        res_create = self.client.post('/api/estoque/fisico', json={"id_jogo": self.jogo_id, "codigo_barras": "CT-DELETE", "estado_conservacao": "PESSIMO"}, headers=self.headers)
        midia_id = res_create.get_json()['id']
        
        res_delete = self.client.delete(f'/api/estoque/{midia_id}', headers=self.headers)
        self.assertEqual(res_delete.status_code, 200)
        
        # Tenta buscar pelo ID do Jogo e deve vir vazio
        res_list = self.client.get(f'/api/estoque/jogo/{self.jogo_id}', headers=self.headers)
        self.assertEqual(len(res_list.get_json()), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
