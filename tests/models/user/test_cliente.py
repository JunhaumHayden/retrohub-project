import unittest
from datetime import date
from app.models.usuario.cliente import Cliente


class TestCliente(unittest.TestCase):

    def test_criar_cliente(self):
        """Testa a criação de um objeto Cliente em memória."""
        # Dados para criar o cliente
        nome = "João Silva"
        cpf = "12345678901"
        email = "joao.silva@example.com"
        senha = "senha123"
        data_nascimento = date(1990, 5, 15)
        dados_pagamento = "Cartão de Crédito ****1234"

        # Criar instância do Cliente
        cliente = Cliente(
            nome=nome,
            cpf=cpf,
            email=email,
            senha=senha,
            data_nascimento=data_nascimento,
            dados_pagamento=dados_pagamento
        )

        # Verificar se os atributos foram definidos corretamente
        self.assertEqual(cliente.nome, nome)
        self.assertEqual(cliente.cpf, cpf)
        self.assertEqual(cliente.email, email)
        self.assertEqual(cliente.senha, senha)
        self.assertEqual(cliente.data_nascimento, data_nascimento)
        self.assertEqual(cliente.dados_pagamento, dados_pagamento)

        # Verificar valores padrão
        # Nota: defaults do SQLAlchemy são aplicados apenas quando o objeto é adicionado a uma sessão
        # Para teste em memória, data_cadastro e tipo_cliente podem ser None se não definidos explicitamente
        # self.assertIsNotNone(cliente.data_cadastro)
        # self.assertEqual(cliente.tipo_cliente, 'regular')

        # Testar representação string
        repr_str = repr(cliente)
        self.assertIn("Cliente", repr_str)
        self.assertIn("João Silva", repr_str)


if __name__ == '__main__':
    unittest.main(verbosity=2)
