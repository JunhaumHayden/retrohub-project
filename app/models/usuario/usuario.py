from abc import ABC
from datetime import date
from typing import Optional
from sqlalchemy import Column, Integer, String, Date
from app.database.base_model import Base

class Usuario(Base):
    """ Classe Abstrata Base para representar um usuário (cliente ou funcionario)"""
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    senha = Column(String(255), nullable=False)
    data_cadastro = Column(Date, default=date.today)
    data_nascimento = Column(Date)

    def __init__(
            self,
            nome: str,
            cpf: str,
            email: str,
            senha: str,
            id: int = None,
            data_cadastro: Optional[date] = None,
            data_nascimento: Optional[date] = None
    ):
        if type(self) is Usuario:
            raise TypeError("Erro: Operação Não permitida")
        
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.senha = senha
        self.data_cadastro = data_cadastro or date.today()
        self.data_nascimento = data_nascimento
        
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, nome='{self.nome}', tipo='{self.__class__.__name__.lower()}')>"

    def __str__(self):
        return f"{self.__class__.__name__} id={self.id}, nome={self.nome}, cpf={self.cpf}, email={self.email}, data_cadastro={self.data_cadastro}, data_nascimento={self.data_nascimento}"
