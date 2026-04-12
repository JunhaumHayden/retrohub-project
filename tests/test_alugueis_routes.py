import unittest
from datetime import datetime, timedelta, date
from decimal import Decimal
from app import create_app
from app.database.database_config import Base
from app.database.factories.database_manager import DatabaseManager
from app.models import Cliente, Jogo, Exemplar, MidiaFisica, MidiaDigital, Transacao, Aluguel, Venda, ItemTransacao, Usuario

class TestAlugueisRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
        session = DatabaseManager.get_session()
        engine = session.bind
        Base.metadata.drop_all(engine)
        session.close()

    def setUp(self):
        session = DatabaseManager.get_session()
        
        session.query(ItemTransacao).delete()
        session.query(Aluguel).delete()
        session.query(Venda).delete()
        session.query(Transacao).delete()
        session.query(MidiaFisica).delete()
        session.query(MidiaDigital).delete()
        session.query(Exemplar).delete()
        session.query(Jogo).delete()
        session.query(Cliente).delete()
        session.query(Usuario).delete()
        session.commit()
        
        # Cliente base
        self.cliente = Cliente(
            nome="Cliente Teste",
            cpf="11122233344",
            email="cliente@retrohub.com",
            senha="hash",
            dados_pagamento="Cartao Final 1234",
            data_nascimento=date(1990, 1, 1)
        )
        session.add(self.cliente)
        
        # Jogo com Mídia Física e Digital
        self.jogo = Jogo(
            titulo="Chrono Trigger",
            plataforma="SNES",
            valor_venda=200.00,
            valor_diaria_aluguel=5.00
        )
        session.add(self.jogo)
        session.flush()

        self.midia_fisica = MidiaFisica(
            id_jogo=self.jogo.id,
            codigo_barras="12345-SNES-CT",
            estado_conservacao="BOM"
        )
        self.midia_digital = MidiaDigital(
            id_jogo=self.jogo.id,
            chave_ativacao="XXXX-YYYY-ZZZZ"
        )
        session.add_all([self.midia_fisica, self.midia_digital])
        session.commit()
        
        self.cliente_id = self.cliente.id_usuario
        self.jogo_id = self.jogo.id
        self.headers = {'X-Cliente-Id': str(self.cliente_id)}
        session.close()

    def test_1_solicitar_aluguel_fisico_sucesso(self):
        """Testa a solicitação de um aluguel físico (status 201)."""
        hoje = date.today().strftime('%Y-%m-%d')
        payload = {
            "id_jogo": self.jogo_id,
            "dias_alugados": 5,
            "data_inicio": hoje,
            "tipo_midia": "FISICA"
        }
        response = self.client.post('/api/alugueis/solicitar', json=payload, headers=self.headers)
        if response.status_code != 201:
            print("ERROR JSON:", response.get_json())
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('id_transacao', data)
        self.assertEqual(data['valor_total'], 25.00) # 5 dias * 5.00

    def test_2_solicitar_aluguel_sem_estoque(self):
        """Testa se a API bloqueia aluguel quando não há estoque físico."""
        hoje = date.today().strftime('%Y-%m-%d')
        payload = {
            "id_jogo": self.jogo_id,
            "dias_alugados": 5,
            "data_inicio": hoje,
            "tipo_midia": "FISICA"
        }
        # 1. Aluga a única cópia física
        self.client.post('/api/alugueis/solicitar', json=payload, headers=self.headers)
        
        # 2. Tenta alugar de novo
        response = self.client.post('/api/alugueis/solicitar', json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Não há exemplares da mídia FISICA disponíveis", response.get_json()['erro'])

    def test_4_listar_meus_alugueis(self):
        """Testa a listagem de aluguéis do cliente."""
        hoje = date.today().strftime('%Y-%m-%d')
        payload = {"id_jogo": self.jogo_id, "dias_alugados": 2, "data_inicio": hoje, "tipo_midia": "DIGITAL"}
        self.client.post('/api/alugueis/solicitar', json=payload, headers=self.headers)
        
        response = self.client.get('/api/alugueis/meus-alugueis', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)

    def test_5_cancelar_aluguel(self):
        """Testa cancelar aluguel antes da data de início."""
        amanha = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        payload = {"id_jogo": self.jogo_id, "dias_alugados": 2, "data_inicio": amanha, "tipo_midia": "DIGITAL"}
        res_create = self.client.post('/api/alugueis/solicitar', json=payload, headers=self.headers)
        aluguel_id = res_create.get_json()['id_transacao']

        res_cancel = self.client.patch(f'/api/alugueis/{aluguel_id}/cancelar', headers=self.headers)
        self.assertEqual(res_cancel.status_code, 200)
        self.assertIn("sucesso", res_cancel.get_json()['mensagem'])

    def test_6_renovar_aluguel(self):
        """Testa a renovação de aluguel."""
        hoje = date.today().strftime('%Y-%m-%d')
        payload = {"id_jogo": self.jogo_id, "dias_alugados": 2, "data_inicio": hoje, "tipo_midia": "DIGITAL"}
        res_create = self.client.post('/api/alugueis/solicitar', json=payload, headers=self.headers)
        aluguel_id = res_create.get_json()['id_transacao']

        res_renovar = self.client.patch(f'/api/alugueis/{aluguel_id}/renovar', json={"dias_adicionais": 3}, headers=self.headers)
        self.assertEqual(res_renovar.status_code, 200)
        data = res_renovar.get_json()
        self.assertEqual(data['novo_valor_total'], 25.0) # 10.0 + (3 * 5.0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
