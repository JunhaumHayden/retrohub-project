from typing import List, Optional

from app.models import Usuario, Cliente, Funcionario
from app.repository.interface.usuario_repository_interface import UsuarioRepositoryInterface


class UsuarioRepositoryDB(UsuarioRepositoryInterface):
    """
    Implementação concreta do repositório de Usuário para banco de dados real (via SQLAlchemy).
    """

    def __init__(self, session):
        self.session = session

    def list_all(self) -> List[Usuario]:
        return self.session.query(Usuario).all()

    def list_clientes(self) -> List[Cliente]:
        return self.session.query(Cliente).all()

    def list_funcionarios(self) -> List[Funcionario]:
        return self.session.query(Funcionario).all()

    def get_by_id(self, id: int) -> Optional[Usuario]:
        # Tenta buscar em Cliente e depois em Funcionario para abranger todos os usuários
        usuario = self.session.query(Cliente).filter(Cliente.id == id).first()
        if usuario:
            return usuario
        return self.session.query(Funcionario).filter(Funcionario.id == id).first()

    def get_cliente_by_id(self, id: int) -> Optional[Cliente]:
        return self.session.query(Cliente).filter(Cliente.id == id).first()

    def get_funcionario_by_id(self, id: int) -> Optional[Funcionario]:
        return self.session.query(Funcionario).filter(Funcionario.id == id).first()

    def get_by_user(self, usuario: Usuario) -> Optional[Usuario]:
        if hasattr(usuario, 'cpf') and usuario.cpf:
            return self.session.query(Usuario).filter(Usuario.cpf == usuario.cpf).first()
        if hasattr(usuario, 'email') and usuario.email:
            return self.session.query(Usuario).filter(Usuario.email == usuario.email).first()
        return None
    
    def get_cliente_by_cpf(self, cpf: str) -> Optional[Cliente]:
        return self.session.query(Cliente).filter(Cliente.cpf == cpf).first()

    def get_funcionario_by_matricula(self, matricula: str) -> Optional[Funcionario]:
        return self.session.query(Funcionario).filter(Funcionario.matricula == matricula).first()

    def create(self, usuario: Usuario) -> Optional[Usuario]:
        self.session.add(usuario)
        self.session.commit()
        return usuario

    def update(self, usuario: Usuario) -> Optional[Usuario]:
        self.session.add(usuario)
        self.session.commit()
        return usuario

    def delete(self, usuario: Usuario) -> bool:
        if usuario:
            self.session.delete(usuario)
            self.session.commit()
            return True
        return False
