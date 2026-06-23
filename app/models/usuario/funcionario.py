from datetime import date
from typing import Optional
from sqlalchemy import Column, String, Date, Integer, ForeignKey

from app.models.usuario.usuario import Usuario

class Funcionario(Usuario):
    __tablename__ = 'funcionarios'

    id = Column(Integer, ForeignKey('usuarios.id'), primary_key=True)
    matricula = Column(String(50), unique=True, nullable=False)
    cargo = Column(String(100))
    setor = Column(String(100))
    data_admissao = Column(Date)

    __mapper_args__ = {
        'polymorphic_identity': 'funcionario',
    }

    def __init__(
            self,
            id_usuario: int = None,
            nome: str = None,
            cpf: str = None,
            email: str = None,
            senha: str = None,
            data_nascimento: date = None,
            matricula: str = None,
            cargo: Optional[str] = None,
            setor: Optional[str] = None,
            data_admissao: Optional[date] = None, **kwargs):
        super().__init__(
            id=id_usuario,
            nome=nome,
            cpf=cpf,
            email=email,
            senha=senha,
            data_nascimento=data_nascimento,
                         **kwargs)
        self.matricula = matricula
        self.cargo = cargo
        self.setor = setor
        self.data_admissao = data_admissao
        self.tipo_usuario = 'funcionario'

    def __repr__(self):
        return f"<Funcionario(id={self.id}, nome='{self.nome}', matricula='{self.matricula}')>"

    def __str__(self):
        return f"Funcionario(id={self.id}, nome={self.nome}, matricula={self.matricula})"
