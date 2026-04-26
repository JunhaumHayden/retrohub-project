from datetime import date
from typing import Optional

from app.models.usuario.usuario import Usuario

class Funcionario(Usuario):
    def __init__(
            self,
            matricula: str = None,
            id_usuario: int = None,
            nome: str = None,
            cpf: str = None,
            email: str = None,
            senha: str = None,
            data_nascimento: date = None,
            cargo: Optional[str] = None,
            setor: Optional[str] = None,
            data_admissao: Optional[date] = None,
            **kwargs,
    ):
        # Aceita tanto `id_usuario=` quanto `id=` para compatibilidade.
        if "id" in kwargs:
            id_usuario = kwargs.pop("id") if id_usuario is None else id_usuario
        super().__init__(
            id=id_usuario,
            nome=nome,
            cpf=cpf,
            email=email,
            senha=senha,
            data_nascimento=data_nascimento,
            **kwargs,
        )
        self.matricula = matricula
        self.cargo = cargo
        self.setor = setor
        self.data_admissao = data_admissao

    @property
    def id_usuario(self) -> Optional[int]:
        """Compat alias para código que ainda referencia ``id_usuario``."""
        return self.id

    @id_usuario.setter
    def id_usuario(self, value: Optional[int]) -> None:
        self.id = value

    def __repr__(self):
        return (
            f"<Funcionario(id={self.id}, nome='{self.nome}', "
            f"matricula='{self.matricula}', tipo='funcionario')>"
        )

    def __str__(self):
        return f"Funcionario(id={self.id}, nome={self.nome}, matricula={self.matricula})"

