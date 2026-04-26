from datetime import date
from typing import Optional


class Usuario:
    """Classe base para Cliente e Funcionario.

    Não usa ``ABC`` formalmente para permitir instanciação parcial em
    cenários de teste/lookup (ex.: ``UsuarioRepository.get_by_user``). A
    distinção semântica continua sendo feita pelas subclasses concretas
    ``Cliente`` e ``Funcionario``.
    """

    def __init__(
            self,
            nome: Optional[str] = None,
            cpf: Optional[str] = None,
            email: Optional[str] = None,
            senha: Optional[str] = None,
            id: Optional[int] = None,
            data_cadastro: Optional[date] = None,
            data_nascimento: Optional[date] = None,
    ):
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.senha = senha
        self.data_cadastro = data_cadastro or date.today()
        self.data_nascimento = data_nascimento
        
    def __repr__(self):
        cls = self.__class__.__name__
        return f"<{cls}(id={self.id}, nome='{self.nome}', tipo='{cls.lower()}')>"

    def __str__(self):
        return f"{self.__class__.__name__} id={self.id}, nome={self.nome}, cpf={self.cpf}, email={self.email}, data_cadastro={self.data_cadastro}, data_nascimento={self.data_nascimento}"
