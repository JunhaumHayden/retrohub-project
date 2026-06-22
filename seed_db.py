#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date
from app.database.base_model import Base
from app.models import Cliente, Funcionario, Catalogo, MidiaDigital
from decimal import Decimal

load_dotenv()

# Usa retrohub.db especificamente
db_path = "resources/database/sqlite/retrohub.db"
engine = create_engine(f'sqlite:///{db_path}')

print(f"Conectando a {db_path}...")

# Recria tabelas
print("Criando tabelas...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("✓ Tabelas criadas")

Session = sessionmaker(bind=engine)
session = Session()

try:
    # Insere cliente
    cliente = Cliente(
        nome='Cliente Teste',
        cpf='11122233344',
        email='cliente@retrohub.com',
        senha='hash',
        data_nascimento=date(1990, 1, 1),
        dados_pagamento='Cartao',
        tipo_cliente='BASICO'
    )
    session.add(cliente)
    session.flush()  # Força geração do ID
    print(f"✓ Cliente adicionado (ID: {cliente.id})")

    # Insere funcionário
    funcionario = Funcionario(
        nome='Funcionario Teste',
        cpf='22233344455',
        email='func@retrohub.com',
        senha='hash',
        data_nascimento=date(1985, 1, 1),
        matricula='FUNC001'
    )
    session.add(funcionario)
    session.flush()
    print(f"✓ Funcionário adicionado (ID: {funcionario.id})")

    # Insere catálogo
    catalogo = Catalogo(
        titulo='Chrono Trigger',
        situacao='DISPONIVEL'
    )
    session.add(catalogo)
    session.flush()
    print(f"✓ Catálogo adicionado (ID: {catalogo.id})")

    # Insere exemplar digital 1 (para venda)
    midia1 = MidiaDigital(
        catalogo=catalogo,
        situacao='DISPONIVEL',
        chave_ativacao='CHAVE-TESTE-123456',
        valor_venda=Decimal('49.99'),
        valor_diaria_aluguel=Decimal('5.99')
    )
    session.add(midia1)
    session.flush()
    print(f"✓ Exemplar digital 1 adicionado (ID: {midia1.id})")

    # Insere exemplar digital 2 (para aluguel)
    midia2 = MidiaDigital(
        catalogo=catalogo,
        situacao='DISPONIVEL',
        chave_ativacao='CHAVE-TESTE-789012',
        valor_venda=Decimal('49.99'),
        valor_diaria_aluguel=Decimal('5.99')
    )
    session.add(midia2)
    session.flush()
    print(f"✓ Exemplar digital 2 adicionado (ID: {midia2.id})")

    session.commit()
    print("\n✓ Banco preenchido com dados mínimos!")
    print(f"\n→ Use nos headers da demo: X-Cliente-Id: {cliente.id} | X-Funcionario-Id: {funcionario.id}")

except Exception as e:
    session.rollback()
    print(f"✗ Erro: {e}")
finally:
    session.close()
