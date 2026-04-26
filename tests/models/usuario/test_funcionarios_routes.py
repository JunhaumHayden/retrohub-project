import unittest
from app import create_app
from app.database.database_config import Base
from app.database.factories.database_manager import DatabaseManager
from app.models import Funcionario, Usuario

class TestFuncionariosRoutes(unittest.TestCase):
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
        """Antes de cada teste, limpa as tabelas e recria o cenário base com um Administrador válido."""
        session = DatabaseManager.get_session()
        
        # Limpa as tabelas dependentes primeiro e a base (Usuario) depois
        session.query(Funcionario).delete()
        session.query(Usuario).delete()
        session.commit()
        
        self.admin = Funcionario(
            nome="Admin Supremo",
            cpf="00000000000",
            email="admin@retrohub.com",
            senha="hash",
            matricula="ADM001",
            cargo="Administrador",
            setor="Diretoria"
        )
        session.add(self.admin)
        session.commit()
        
        self.admin_id = self.admin.id_usuario
        self.headers = {'X-Admin-Id': str(self.admin_id)}
        session.close()

    def test_1_cadastro_funcionario_sucesso(self):
        """Testa o cadastro válido por um admin (status 201)."""
        payload = {
            "nome": "Novo Funcionario",
            "cpf": "12312312312",
            "email": "novo@retrohub.com",
            "senha": "password",
            "data_nascimento": "1995-10-10",
            "matricula": "FUN002",
            "cargo": "Atendente"
        }
        response = self.client.post('/api/funcionarios/', json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['matricula'], "FUN002")

    def test_2_cadastro_sem_permissao(self):
        """Testa o bloqueio quando não envia o header ou não é admin (status 403)."""
        # 1. Sem header
        response1 = self.client.post('/api/funcionarios/', json={})
        self.assertEqual(response1.status_code, 403)
        self.assertIn("Header X-Admin-Id é obrigatório", response1.get_json()['erro'])

        # 2. Cria um atendente e tenta usar ele no header
        session = DatabaseManager.get_session()
        atendente = Funcionario(
            nome="Atendente", cpf="11122233344", email="ate@retro.com", senha="1",
            matricula="AT01", cargo="Atendente"
        )
        session.add(atendente)
        session.commit()
        atendente_id = atendente.id_usuario
        session.close()

        response2 = self.client.post('/api/funcionarios/', json={}, headers={'X-Admin-Id': str(atendente_id)})
        self.assertEqual(response2.status_code, 403)
        self.assertIn("não tem permissão", response2.get_json()['erro'])

    def test_3_cadastro_idade_minima(self):
        """Testa a validação de 18 anos (status 400)."""
        payload = {
            "nome": "Jovem Aprendiz",
            "cpf": "99988877766",
            "email": "jovem@retrohub.com",
            "senha": "123",
            "data_nascimento": "2020-01-01",
            "matricula": "J001",
            "cargo": "Atendente"
        }
        response = self.client.post('/api/funcionarios/', json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("18 anos", response.get_json()['erro'])

    def test_4_auto_exclusao_bloqueada(self):
        """Impede que o admin inative a si mesmo (status 400)."""
        response = self.client.delete(f'/api/funcionarios/{self.admin_id}', headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("a si mesmo", response.get_json()['erro'])

    def test_5_rebaixamento_ultimo_admin_bloqueado(self):
        """Impede que o último administrador mude seu próprio cargo."""
        payload = {"cargo": "Gerente"}
        response = self.client.put(f'/api/funcionarios/{self.admin_id}', json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("último administrador", response.get_json()['erro'])

    def test_6_excluir_ultimo_admin_bloqueado(self):
        """Impede a exclusão do último admin."""
        # Para testar isso limpo, vamos adicionar um 2º admin para excluir o 1º.
        session = DatabaseManager.get_session()
        admin2 = Funcionario(
            nome="Admin 2", cpf="22233344455", email="admin2@retro.com", senha="1",
            matricula="ADM002", cargo="Administrador"
        )
        session.add(admin2)
        session.commit()
        admin2_id = admin2.id_usuario
        session.close()

        # O Admin 2 exclui o Admin 1 (Sucesso, pois ficam 1)
        res1 = self.client.delete(f'/api/funcionarios/{self.admin_id}', headers={'X-Admin-Id': str(admin2_id)})
        self.assertEqual(res1.status_code, 200)

        # Agora o Admin 2 tenta rebaixar a si mesmo (Falha, pois só tem ele)
        res2 = self.client.put(f'/api/funcionarios/{admin2_id}', json={"cargo": "Atendente"}, headers={'X-Admin-Id': str(admin2_id)})
        self.assertEqual(res2.status_code, 400)

if __name__ == '__main__':
    unittest.main(verbosity=2)
