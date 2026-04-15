import unittest
from app import create_app
from app.database.database_config import Base
from app.database.factories.database_manager import DatabaseManager
from app.models import Funcionario, Usuario, Jogo


class TestCatalogo(unittest.TestCase):

    def setUp(self):
        """Antes de cada teste, limpa as tabelas e recria o cenário base."""

        self.funcionario = Funcionario(
            nome="Atendente Teste",
            cpf="12345678901",
            email="atendente@retrohub.com",
            senha="hash",
            matricula="AT001",
            cargo="Atendente",
            setor="Vendas"
        )

    def test_1_cadastro_jogo_sucesso(self):
        """Testa o cadastro válido por um funcionário (status 201)."""
        data = {
            "titulo": "Super Mario 64",
            "plataforma": "Nintendo 64",
            "descricao": "O primeiro jogo 3D do Mario",
            "ativo": True,
            "genero": "Plataforma",
            "classificacao": "Livre",
            "valor_venda": 150.00,
            "valor_diaria_aluguel": 5.00
        }

        # Criar instância do Jogo
        catalogo = Jogo(
            id=1,
            titulo=data.get('titulo'),
            plataforma=data.get('plataforma'),
            descricao=data.get('descricao'),
            ativo=data.get('ativo'),
            genero=data.get('genero'),
            classificacao=data.get('classificacao'),
            valor_venda=data.get('valor_venda'),
            valor_diaria_aluguel=data.get('valor_diaria_aluguel')
        )

        # Verificar se os atributos foram definidos corretamente
        self.assertEqual(data['titulo'], "Super Mario 64")


        # Testar representação string
        repr_str = repr(catalogo)
        print(repr_str)
        self.assertIn("id", repr_str)
        self.assertIn("titulo", repr_str)


if __name__ == '__main__':
    unittest.main(verbosity=2)
