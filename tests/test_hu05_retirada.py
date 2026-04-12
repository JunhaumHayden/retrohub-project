import unittest
from datetime import date, timedelta

from app import create_app
from app.database.database_config import Base
from app.database.factories.database_manager import DatabaseManager
from app.models import (
    Cliente,
    Funcionario,
    Jogo,
    Exemplar,
    MidiaDigital,
    Transacao,
    Aluguel,
    Venda,
    ItemTransacao,
    Usuario,
)


class TestHu05Retirada(unittest.TestCase):
    """HU 05 — registro de saída (retirada): solicitar → PATCH retirada → ATIVO e data_retirada."""

    @classmethod
    def setUpClass(cls):
        test_config = {
            "db_type": "sqlite",
            "db_url": "sqlite:///:memory:",
        }
        cls.app = create_app(test_config=test_config)
        cls.app.config["TESTING"] = True
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
        session.query(MidiaDigital).delete()
        session.query(Exemplar).delete()
        session.query(Jogo).delete()
        session.query(Cliente).delete()
        session.query(Funcionario).delete()
        session.query(Usuario).delete()

        self.cliente = Cliente(
            nome="Cliente HU05",
            cpf="11122233344",
            email="hu05.cliente@retrohub.com",
            senha="hash",
            dados_pagamento="Cartao Final 9999",
            data_nascimento=date(1990, 1, 1),
        )
        self.funcionario = Funcionario(
            nome="Funcionario HU05",
            cpf="55566677788",
            email="hu05.func@retrohub.com",
            senha="hash",
            matricula="HU05-001",
            cargo="Atendente",
            setor="Loja",
        )
        session.add_all([self.cliente, self.funcionario])
        session.flush()

        self.jogo = Jogo(
            titulo="Secret of Mana",
            plataforma="SNES",
            valor_venda=150.00,
            valor_diaria_aluguel=4.00,
        )
        session.add(self.jogo)
        session.flush()

        self.midia_digital = MidiaDigital(
            id_jogo=self.jogo.id,
            chave_ativacao="HU05-KEY-DIGITAL",
        )
        session.add(self.midia_digital)
        session.commit()

        self.cliente_id = self.cliente.id_usuario
        self.funcionario_id = self.funcionario.id_usuario
        self.jogo_id = self.jogo.id
        self.headers_cliente = {"X-Cliente-Id": str(self.cliente_id)}
        self.headers_funcionario = {"X-Funcionario-Id": str(self.funcionario_id)}
        session.close()

    def test_retirada_apos_solicitacao_ativa_aluguel_e_preenche_data_retirada(self):
        """Cria aluguel (SOLICITADO), registra retirada e valida ATIVO + data_retirada."""
        hoje = date.today().strftime("%Y-%m-%d")
        dias = 3
        payload = {
            "id_jogo": self.jogo_id,
            "dias_alugados": dias,
            "data_inicio": hoje,
            "tipo_midia": "DIGITAL",
        }
        res_create = self.client.post(
            "/api/alugueis/solicitar",
            json=payload,
            headers=self.headers_cliente,
        )
        self.assertEqual(res_create.status_code, 201, res_create.get_json())
        aluguel_id = res_create.get_json()["id_transacao"]

        res_retirada = self.client.patch(
            f"/api/alugueis/{aluguel_id}/retirada",
            headers=self.headers_funcionario,
        )
        self.assertEqual(res_retirada.status_code, 200, res_retirada.get_json())
        body = res_retirada.get_json()

        self.assertEqual(body.get("status_transacao"), "ATIVO")
        self.assertEqual(body.get("status_aluguel"), "ATIVO")
        self.assertIsNotNone(body.get("data_retirada"))

        # data_fim_prevista / data_prevista_devolucao = retirada + período (dias de aluguel)
        self.assertIsNotNone(body.get("data_fim_prevista"))
        self.assertIsNotNone(body.get("data_prevista_devolucao"))
        self.assertEqual(body["data_fim_prevista"], body["data_prevista_devolucao"])

        esperado_fim = (date.today() + timedelta(days=dias)).isoformat()
        self.assertEqual(body["data_fim_prevista"][:10], esperado_fim)


if __name__ == "__main__":
    unittest.main(verbosity=2)
