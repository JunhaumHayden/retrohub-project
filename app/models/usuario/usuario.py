from abc import ABC
from datetime import date
from typing import Optional


class Usuario(ABC):
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
        return f"<{self.__class__.__name__}(id={self.id}, nome='{self.nome},tipo='{self.__class__.__name__}')>"

    def __str__(self):
        return f"{self.__class__.__name__} id={self.id}, nome={self.nome}, cpf={self.cpf}, email={self.email}, data_cadastro={self.data_cadastro}, data_nascimento={self.data_nascimento}"
