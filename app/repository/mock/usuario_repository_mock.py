from typing import List, Optional

from app.models import Usuario, Cliente, Funcionario
from app.repository.interface.usuario_repository_interface import UsuarioRepositoryInterface
from app.database.mock_data_source import MockDataSource


class UsuarioRepositoryMock(UsuarioRepositoryInterface):
    """
    Mock implementation of Usuario repository using in-memory data source
    """

    def __init__(self, data_source: Optional[MockDataSource] = None):
        self.data_source = data_source or MockDataSource()
        self.data_source.load_data()

    def list_all(self) -> List[Usuario]:
        """List all users (clientes and funcionarios)"""
        clientes = self.data_source.get_all(Cliente)
        funcionarios = self.data_source.get_all(Funcionario)
        return clientes + funcionarios

    def get_by_id(self, id: int) -> Optional[Usuario]:
        """Get user by ID"""
        # Try Cliente first
        usuario = self.data_source.get_by_id(Cliente, id)
        if usuario:
            return usuario
        
        # Try Funcionario
        return self.data_source.get_by_id(Funcionario, id)

    def get_by_user(self, usuario: Usuario) -> Optional[Usuario]:
        """Get user by CPF or email"""
        # Try by CPF
        if hasattr(usuario, 'cpf') and usuario.cpf:
            result = self.data_source.get_by_field(Cliente, 'cpf', usuario.cpf)
            if result:
                return result
            result = self.data_source.get_by_field(Funcionario, 'cpf', usuario.cpf)
            if result:
                return result
        
        # Try by email
        if hasattr(usuario, 'email') and usuario.email:
            result = self.data_source.get_by_field(Cliente, 'email', usuario.email)
            if result:
                return result
            result = self.data_source.get_by_field(Funcionario, 'email', usuario.email)
            if result:
                return result
        
        return None

    def create(self, usuario: Usuario) -> Optional[Usuario]:
        """Create a new user"""
        if isinstance(usuario, Cliente):
            return self.data_source.create(usuario)
        elif isinstance(usuario, Funcionario):
            return self.data_source.create(usuario)
        return None

    def update(self, usuario: Usuario) -> Optional[Usuario]:
        """Update an existing user"""
        return self.data_source.update(usuario)

    def delete(self, usuario: Usuario) -> bool:
        """Delete a user"""
        if not hasattr(usuario, 'id'):
            return False
            
        if isinstance(usuario, Cliente):
            return self.data_source.delete(Cliente, usuario.id)
        elif isinstance(usuario, Funcionario):
            return self.data_source.delete(Funcionario, usuario.id)
        return False

    # Additional methods for specific types
    def list_clientes(self) -> List[Cliente]:
        """List all clientes"""
        return self.data_source.get_all(Cliente)

    def list_funcionarios(self) -> List[Funcionario]:
        """List all funcionarios"""
        return self.data_source.get_all(Funcionario)

    def get_cliente_by_id(self, id: int) -> Optional[Cliente]:
        """Get cliente by ID"""
        return self.data_source.get_by_id(Cliente, id)

    def get_funcionario_by_id(self, id: int) -> Optional[Funcionario]:
        """Get funcionario by ID"""
        return self.data_source.get_by_id(Funcionario, id)

    def get_cliente_by_cpf(self, cpf: str) -> Optional[Cliente]:
        """Get cliente by CPF"""
        return self.data_source.get_by_field(Cliente, 'cpf', cpf)

    def get_funcionario_by_matricula(self, matricula: str) -> Optional[Funcionario]:
        """Get funcionario by matricula"""
        return self.data_source.get_by_field(Funcionario, 'matricula', matricula)