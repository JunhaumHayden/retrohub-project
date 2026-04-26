import unittest
from datetime import date

from app.models import Funcionario, Venda
from app.models.enums import StatusVenda
from app.models.usuario.cliente import Cliente


class TestVenda(unittest.TestCase):

    def test_criar_venda(self):
        """Testa a criação de um objeto Venda em memória."""

        # Dados para um cliente
        nome = "Ana Almeida"
        cpf = "12345678901"
        email = "ana.almeida@example.com"
        senha = "senha123"
        data_nascimento = date(1990, 5, 15)
        dados_pagamento = "Pix Code"

        # Criar instância do Cliente
        cliente = Cliente(
            id_usuario=1,
            nome=nome,
            cpf=cpf,
            email=email,
            senha=senha,
            data_nascimento=data_nascimento,
            dados_pagamento=dados_pagamento
        )

        # Dados para criar o funcionario
        nome = "Bia Bianch"
        cpf = "22222222222"
        email = "bia.bianch@example.com"
        senha = "senha222"
        data_nascimento = date(1992, 2, 22)
        matricula = "mat2222"
        cargo = "Atendente"
        setor = "Balcao"
        data_admissao = date(2022, 1, 24)

        # Criar instância do funcionario
        funcionario = Funcionario(
            id_usuario=1,
            nome=nome,
            cpf=cpf,
            email=email,
            senha=senha,
            data_nascimento=data_nascimento,
            matricula=matricula,
            cargo=cargo,
            setor=setor,
            data_admissao=data_admissao
        )

        # Dados para criar a venda
        data_confirmacao = date(2026, 5, 15)
        status = StatusVenda.FINALIZADA.value

        # Criar instância da venda
        venda = Venda(
            id_transacao=10,
            status=status,
            data_confirmacao=data_confirmacao,
            cliente=cliente,
            funcionario=funcionario,
        )

        print("\n[FORMA 1] print(venda):")
        print(venda)

        print("\n[FORMA 2] repr(venda):")
        print(repr(venda))

        print("\n[FORMA 3] Atributos específicos:")
        print(f"  ID: {venda.id}")
        print(f"  Status: {venda.status}")
        print(f"  Cliente: {venda.cliente.nome}")
        print(f"  Funcionario: {venda.funcionario.nome}")

        # Verificar se os atributos foram definidos corretamente
        self.assertEqual(venda.id, 10)
        self.assertEqual(venda.status, status)
        self.assertEqual(venda.data_confirmacao, data_confirmacao)
        self.assertIs(venda.cliente, cliente)
        self.assertIs(venda.funcionario, funcionario)
        self.assertEqual(venda.tipo, "venda")

        # Testar representação string
        repr_str = repr(venda)
        self.assertIn("Venda", repr_str)
        self.assertIn("id=10", repr_str)


if __name__ == '__main__':
    unittest.main(verbosity=2)
