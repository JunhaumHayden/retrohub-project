from typing import List, Optional

from app.models import Usuario, Funcionario
from app.repository.interface.usuario_repository_interface import UsuarioRepositoryInterface
from app.models.usuario.cliente import Cliente


class UsuarioRepositoryDB(UsuarioRepositoryInterface):

    def __init__(self, session):
        self.session = session

    def list_all(self) -> List[Usuario]:
        return self.session.query(Usuario).all()

    def get_by_id(self, id: int) -> Optional[Usuario]:
        return self.session.query(Usuario).filter(Usuario.id == id).first()

    def get_by_user(self, usuario: Usuario) -> Optional[Usuario]:
        return self.session.query(Usuario).filter(Usuario.cpf == usuario.cpf).first()

    def create(self, usuario: Usuario) -> Optional[Usuario]:
        self.session.add(usuario)
        return usuario

    def create_client(self, cliente: Cliente) -> Optional[Cliente]:
        self.session.add(cliente)
        return cliente

    def create_employee(self, funcionario: Funcionario) -> Optional[Funcionario]:
        self.session.add(funcionario)
        return funcionario

    def update(self, usuario: Usuario) -> Optional[Usuario]:
        self.session.add(usuario)
        return usuario

    def delete(self, id: int) -> bool:
        usuario = self.get_by_id(id)
        if usuario:
            self.session.delete(usuario)
            return True
        return False