import unittest
from datetime import date, timedelta
from decimal import Decimal

from app import create_app
from app.database.database_config import Base
from app.database.factories.database_manager import DatabaseManager
from app.models import (
    Aluguel,
    Cliente,
    Funcionario,
    Jogo,
    Exemplar,
    MidiaDigital,
    Multa,
    Transacao,
    Venda,
    ItemTransacao,
    Usuario,
)


class TestHu06Hu07Devolucao(unittest.TestCase):
    """HU 06 — devolução; HU 07 — multa por atraso."""

    @classmethod
    def setUpClass(cls):
        test_config = {"db_type": "sqlite", "db_url": "sqlite:///:memory:"}
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
        session.query(Multa).delete()
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
            nome="Cliente Devolução",
            cpf="11122233344",
            email="dev.cliente@retrohub.com",
            senha="hash",
            dados_pagamento="Cartao",
            data_nascimento=date(1990, 1, 1),
        )
        self.funcionario = Funcionario(
            nome="Func Devolução",
            cpf="55566677788",
            email="dev.func@retrohub.com",
            senha="hash",
            matricula="DEV-01",
            cargo="Balcão",
            setor="Loja",
        )
        session.add_all([self.cliente, self.funcionario])
        session.flush()

        self.jogo = Jogo(
            titulo="EarthBound",
            plataforma="SNES",
            valor_venda=300.00,
            valor_diaria_aluguel=Decimal("10.00"),
            estoque_disponivel=10,
        )
        session.add(self.jogo)
        session.flush()

        self.midia_digital = MidiaDigital(
            id_jogo=self.jogo.id,
            chave_ativacao="DEV-KEY-01",
        )
        session.add(self.midia_digital)
        session.commit()

        self.jogo_id = self.jogo.id
        self.headers_cliente = {"X-Cliente-Id": str(self.cliente.id_usuario)}
        self.headers_funcionario = {"X-Funcionario-Id": str(self.funcionario.id_usuario)}
        session.close()

    def _criar_aluguel_ativo(self, dias_alugados: int):
        hoje = date.today().strftime("%Y-%m-%d")
        res = self.client.post(
            "/api/alugueis/solicitar",
            json={
                "id_jogo": self.jogo_id,
                "dias_alugados": dias_alugados,
                "data_inicio": hoje,
                "tipo_midia": "DIGITAL",
            },
            headers=self.headers_cliente,
        )
        self.assertEqual(res.status_code, 201, res.get_json())
        aid = res.get_json()["id_transacao"]
        ret = self.client.patch(
            f"/api/alugueis/{aid}/retirada",
            headers=self.headers_funcionario,
        )
        self.assertEqual(ret.status_code, 200, ret.get_json())
        return aid

    def test_devolucao_no_prazo_sem_multa(self):
        dias = 5
        aluguel_id = self._criar_aluguel_ativo(dias)

        res = self.client.patch(
            f"/api/alugueis/{aluguel_id}/devolucao",
            json={"condicao_item": "bom"},
            headers=self.headers_funcionario,
        )
        self.assertEqual(res.status_code, 200, res.get_json())
        body = res.get_json()
        self.assertEqual(body["status_transacao"], "FINALIZADO")
        self.assertIsNotNone(body.get("data_devolucao_real"))
        self.assertEqual(body.get("multa_aplicada"), 0.0)
        self.assertEqual(body.get("dias_atraso"), 0)
        self.assertTrue(body.get("multa_paga"))
        self.assertEqual(body.get("condicao_item"), "bom")
        self.assertEqual(body.get("id_funcionario_recebimento"), self.funcionario.id_usuario)

        session = DatabaseManager.get_session()
        self.assertEqual(session.query(Multa).filter_by(id_aluguel=aluguel_id).count(), 0)
        session.close()

    def test_devolucao_com_atraso_calcula_multa(self):
        dias = 2
        aluguel_id = self._criar_aluguel_ativo(dias)

        session = DatabaseManager.get_session()
        al = session.query(Aluguel).get(aluguel_id)
        al.data_prevista_devolucao = date.today() - timedelta(days=4)
        session.commit()
        session.close()

        res = self.client.patch(
            f"/api/alugueis/{aluguel_id}/devolucao",
            json={"condicao_item": "danificado"},
            headers=self.headers_funcionario,
        )
        self.assertEqual(res.status_code, 200, res.get_json())
        body = res.get_json()
        self.assertEqual(body["status_transacao"], "FINALIZADO")
        self.assertEqual(body["dias_atraso"], 4)
        # 4 * (10.00 * 0.10) = 4.00; teto = valor_total do aluguel (2 * 10 = 20)
        self.assertEqual(body["multa_aplicada"], 4.0)
        self.assertFalse(body.get("multa_paga"))

        session = DatabaseManager.get_session()
        multa = session.query(Multa).filter_by(id_aluguel=aluguel_id).first()
        self.assertIsNotNone(multa)
        self.assertEqual(multa.dias_atraso, 4)
        self.assertEqual(float(multa.valor), 4.0)
        self.assertEqual(multa.status, "PENDENTE")
        session.close()

    def test_multa_respeita_teto_100_porcento_valor_total(self):
        """Multa bruta acima do valor total do aluguel deve limitar ao valor_total."""
        aluguel_id = self._criar_aluguel_ativo(1)

        session = DatabaseManager.get_session()
        al = session.query(Aluguel).get(aluguel_id)
        al.data_prevista_devolucao = date.today() - timedelta(days=50)
        session.commit()
        session.close()

        res = self.client.patch(
            f"/api/alugueis/{aluguel_id}/devolucao",
            json={"condicao_item": "bom"},
            headers=self.headers_funcionario,
        )
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        # valor_total = 1 * 10 = 10; multa bruta seria 50 * 1 = 50; teto 10
        self.assertEqual(body["multa_aplicada"], 10.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
