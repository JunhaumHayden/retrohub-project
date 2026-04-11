import unittest
from datetime import date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database_config import Base
from app.models import (
    Usuario, Cliente, Funcionario,
    Jogo, Exemplar, MidiaFisica, MidiaDigital,
    Transacao, Venda, Aluguel, Reserva,
    ItemTransacao, Comprovante, Multa, Avaliacao
)

class TestModelsMapping(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Inicializa um banco SQLite em memória para testar o mapeamento das classes."""
        # Usa sqlite em memória para os testes serem super rápidos e independentes
        cls.engine = create_engine('sqlite:///:memory:')
        
        # Cria todas as tabelas baseadas nos modelos importados
        Base.metadata.create_all(cls.engine)
        
        # Prepara a sessão
        Session = sessionmaker(bind=cls.engine)
        cls.session = Session()

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.engine.dispose()

    def setUp(self):
        """Inicia uma transação antes de cada teste para podermos dar rollback."""
        self.transaction = self.session.begin_nested()

    def tearDown(self):
        """Dá rollback na transação para manter o banco limpo para o próximo teste."""
        self.session.rollback()

    def test_create_cliente(self):
        """Testa a criação de um Cliente (herança de Usuario)."""
        cliente = Cliente(
            nome="João Cliente",
            cpf="11122233344",
            email="joao@cliente.com",
            senha="senha",
            dados_pagamento="Cartão Final 1234"
        )
        self.session.add(cliente)
        self.session.flush() # Força a ida pro banco

        # Verifica se o ID foi gerado (o que significa que salvou no DB)
        self.assertIsNotNone(cliente.id)
        self.assertEqual(cliente.id, cliente.id_usuario)

    def test_create_funcionario(self):
        """Testa a criação de um Funcionario (herança de Usuario)."""
        func = Funcionario(
            nome="Maria Func",
            cpf="99988877766",
            email="maria@func.com",
            senha="senha",
            matricula="MAT123",
            cargo="Vendedora"
        )
        self.session.add(func)
        self.session.flush()

        self.assertIsNotNone(func.id)
        self.assertEqual(func.matricula, "MAT123")

    def test_create_midia_fisica(self):
        """Testa a criação de uma Mídia Física como um Exemplar do Catálogo (Jogo)."""
        # 1. Primeiro cadastra-se o Jogo no Catálogo (Vitrine)
        jogo = Jogo(
            titulo="Super Metroid",
            plataforma="SNES",
            valor_venda=Decimal('150.00')
        )
        self.session.add(jogo)
        self.session.flush()

        # 2. Depois cadastra-se a mídia física vinculada ao jogo (Estoque real/Exemplar)
        midia = MidiaFisica(
            id_jogo=jogo.id,
            codigo_barras="123456789",
            estado_conservacao="Bom"
        )
        self.session.add(midia)
        self.session.flush()

        self.assertIsNotNone(midia.id)
        self.assertEqual(midia.id_jogo, jogo.id)
        self.assertEqual(midia.codigo_barras, "123456789")

    def test_create_venda(self):
        """Testa a criação de uma Venda (herança de Transacao) com seus relacionamentos."""
        cliente = Cliente(nome="C", cpf="1", email="1", senha="1")
        venda = Venda(
            valor_total=Decimal('50.00'),
            status="FINALIZADA"
        )
        
        # Associa manualmente, ou via objetos (como não definimos back_populates ainda, associamos o ID)
        self.session.add(cliente)
        self.session.flush()
        
        venda.id_cliente = cliente.id
        self.session.add(venda)
        self.session.flush()

        self.assertIsNotNone(venda.id)
        self.assertEqual(venda.status, "FINALIZADA")

if __name__ == '__main__':
    unittest.main(verbosity=2)
