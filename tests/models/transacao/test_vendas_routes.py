import unittest
from datetime import datetime, date
from decimal import Decimal
from app import create_app
from app.database.database_config import Base
from app.database.factories.database_manager import DatabaseManager
from app.models import Cliente, Jogo, Exemplar, MidiaFisica, MidiaDigital, Transacao, Aluguel, Venda, ItemTransacao, Usuario

class TestVendasRoutes(unittest.TestCase):
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
            nome="Cliente Venda",
            cpf="99988877766",
            email="venda@retrohub.com",
            senha="hash",
            dados_pagamento="Boleto",
            data_nascimento=date(1995, 5, 5)
        )
        session.add(self.cliente)
        
        # Jogo com Mídia Física e Digital
        self.jogo = Jogo(
            titulo="Halo Combat Evolved",
            plataforma="Xbox",
            valor_venda=100.00,
            valor_diaria_aluguel=5.00
        )
        session.add(self.jogo)
        session.flush()

        self.midia_fisica = MidiaFisica(
            id_jogo=self.jogo.id,
            codigo_barras="XBOX-HALO-1",
            estado_conservacao="NOVO"
        )
        self.midia_digital = MidiaDigital(
            id_jogo=self.jogo.id,
            chave_ativacao="AAAA-BBBB-CCCC"
        )
        session.add_all([self.midia_fisica, self.midia_digital])
        session.commit()
        
        self.cliente_id = self.cliente.id_usuario
        self.jogo_id = self.jogo.id
        self.headers = {'X-Cliente-Id': str(self.cliente_id)}
        session.close()

    def test_1_solicitar_venda_fisica_sucesso(self):
        """Testa a solicitação de uma venda física (status 201)."""
        payload = {
            "id_jogo": self.jogo_id,
            "tipo_midia": "FISICA"
        }
        response = self.client.post('/api/vendas/solicitar', json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('id_transacao', data)
        self.assertEqual(data['valor_total'], 100.00)

    def test_2_solicitar_venda_sem_estoque(self):
        """Testa se a API bloqueia venda quando o estoque físico já foi vendido."""
        payload = {
            "id_jogo": self.jogo_id,
            "tipo_midia": "FISICA"
        }
        # 1. Vende a única cópia física
        self.client.post('/api/vendas/solicitar', json=payload, headers=self.headers)
        
        # 2. Tenta comprar de novo
        response = self.client.post('/api/vendas/solicitar', json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Não há exemplares da mídia FISICA disponíveis", response.get_json()['erro'])

    def test_3_listar_minhas_vendas(self):
        """Testa a listagem de vendas do cliente."""
        payload = {"id_jogo": self.jogo_id, "tipo_midia": "DIGITAL"}
        self.client.post('/api/vendas/solicitar', json=payload, headers=self.headers)
        
        response = self.client.get('/api/vendas/minhas-vendas', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)

    def test_4_estornar_venda(self):
        """Testa estornar uma venda."""
        payload = {"id_jogo": self.jogo_id, "tipo_midia": "DIGITAL"}
        res_create = self.client.post('/api/vendas/solicitar', json=payload, headers=self.headers)
        venda_id = res_create.get_json()['id_transacao']

        res_estorno = self.client.patch(f'/api/vendas/{venda_id}/cancelar', headers=self.headers)
        self.assertEqual(res_estorno.status_code, 200)
        self.assertIn("sucesso", res_estorno.get_json()['mensagem'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
