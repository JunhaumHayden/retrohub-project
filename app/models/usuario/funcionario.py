from datetime import date
from typing import Optional

from app.models.usuario.usuario import Usuario

class Funcionario(Usuario):
    def __init__(self, matricula: str, id_usuario: int = None, nome: str = None, cpf: str = None, 
                 email: str = None, senha: str = None, data_nascimento: date = None,
                 cargo: Optional[str] = None, setor: Optional[str] = None, 
                 data_admissao: Optional[date] = None, **kwargs):
        super().__init__(id=id_usuario, nome=nome, cpf=cpf, email=email, senha=senha, 
                        data_nascimento=data_nascimento, tipo="funcionario", **kwargs)
        self.matricula = matricula
        self.cargo = cargo
        self.setor = setor
        self.data_admissao = data_admissao
