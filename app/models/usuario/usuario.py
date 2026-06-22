from abc import ABC
from datetime import date
from typing import Optional
from sqlalchemy import Column, Integer, String, Date
from app.database.base_model import Base

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    senha = Column(String(255), nullable=False)
    data_cadastro = Column(Date, default=date.today)
    data_nascimento = Column(Date)
    
    tipo_usuario = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'usuario',
        'polymorphic_on': tipo_usuario
    }

    def __init__(
            self,
            nome: str,
            cpf: str,
            email: str,
            senha: str,
            id: int = None,
            data_cadastro: Optional[date] = None,
            data_nascimento: Optional[date] = None,
            **kwargs
    ):
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.senha = senha
        self.data_cadastro = data_cadastro or date.today()
        self.data_nascimento = data_nascimento
        
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, nome='{self.nome}', tipo='{self.tipo_usuario}')>"
