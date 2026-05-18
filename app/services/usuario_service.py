from types import SimpleNamespace
from typing import List, Optional

from app.models.usuario.usuario import Usuario
from app.models.usuario.cliente import Cliente
from app.models.usuario.funcionario import Funcionario
from app.repository.interface.usuario_repository_interface import UsuarioRepositoryInterface
from app.models.enums import TipoCliente


def _user_lookup(*, cpf: Optional[str] = None, email: Optional[str] = None) -> SimpleNamespace:
    """Cria um objeto duck-typed para passar ao ``repository.get_by_user``."""
    return SimpleNamespace(cpf=cpf, email=email)


class UsuarioService:
    """
    Service layer for Usuario operations
    Handles business logic and validation
    """

    def __init__(self, repository: UsuarioRepositoryInterface):
        self.repository = repository

    def list_clientes(self) -> List[Cliente]:
        """List all clientes"""
        return self.repository.list_clientes()

    def list_funcionarios(self) -> List[Funcionario]:
        """List all funcionarios"""
        return self.repository.list_funcionarios()

    def get_by_id(self, id: int) -> Optional[Usuario]:
        """Get user by ID"""
        return self.repository.get_by_id(id)

    def get_by_cpf(self, cpf: str) -> Optional[Usuario]:
        """Get user by CPF"""
        return self.repository.get_by_user(_user_lookup(cpf=cpf))

    def get_cliente_by_id(self, id: int) -> Optional[Cliente]:
        """Get cliente by ID"""
        return self.repository.get_cliente_by_id(id)

    def get_funcionario_by_id(self, id: int) -> Optional[Funcionario]:
        """Get funcionario by ID"""
        return self.repository.get_funcionario_by_id(id)

    def create_cliente(self, cliente: Cliente) -> Optional[Cliente]:
        """Create a new cliente with validation"""
        if not all([cliente.nome, cliente.cpf, cliente.email, cliente.senha]):
            raise ValueError("Campos essenciais (nome, cpf, email, senha) são obrigatórios.")
        
        if self.repository.get_by_user(_user_lookup(cpf=cliente.cpf)):
            raise ValueError(f"Usuário com CPF '{cliente.cpf}' já existe.")
        if self.repository.get_by_user(_user_lookup(email=cliente.email)):
            raise ValueError(f"Email '{cliente.email}' já está em uso.")
        
        if not cliente.tipo_cliente:
            cliente.tipo_cliente = TipoCliente.REGULAR.value
        
        return self.repository.create(cliente)

    def create_funcionario(self, funcionario: Funcionario) -> Optional[Funcionario]:
        """Create a new funcionario with validation"""
        if not all([funcionario.nome, funcionario.cpf, funcionario.email, funcionario.senha, funcionario.matricula]):
            raise ValueError("Campos essenciais (nome, cpf, email, senha, matricula) são obrigatórios.")
        
        if self.repository.get_by_user(_user_lookup(cpf=funcionario.cpf)):
            raise ValueError(f"Usuário com CPF '{funcionario.cpf}' já existe.")
        if self.repository.get_by_user(_user_lookup(email=funcionario.email)):
            raise ValueError(f"Email '{funcionario.email}' já está em uso.")
        if self.repository.get_funcionario_by_matricula(funcionario.matricula):
            raise ValueError(f"Matrícula '{funcionario.matricula}' já existe.")
        
        return self.repository.create(funcionario)

    def update_cliente(self, cliente_id: int, data: dict) -> Optional[Cliente]:
        """Update an existing cliente."""
        cliente = self.repository.get_cliente_by_id(cliente_id)
        if not cliente:
            return None
        
        self._apply_common_updates(cliente, data)

        if 'dados_pagamento' in data:
            cliente.dados_pagamento = data['dados_pagamento']
        if 'tipo_cliente' in data:
            cliente.tipo_cliente = data['tipo_cliente']
        
        return self.repository.update(cliente)

    def update_funcionario(self, funcionario_id: int, data: dict) -> Optional[Funcionario]:
        """Update an existing funcionario."""
        funcionario = self.repository.get_funcionario_by_id(funcionario_id)
        if not funcionario:
            return None

        self._apply_common_updates(funcionario, data)

        if 'cargo' in data:
            funcionario.cargo = data['cargo']
        if 'setor' in data:
            funcionario.setor = data['setor']
        if 'data_admissao' in data:
            funcionario.data_admissao = data['data_admissao']
        if 'matricula' in data and data['matricula'] != funcionario.matricula:
            existing = self.repository.get_funcionario_by_matricula(data['matricula'])
            if existing and existing.id != funcionario_id:
                raise ValueError(f"Matrícula '{data['matricula']}' já está em uso.")
            funcionario.matricula = data['matricula']
        
        return self.repository.update(funcionario)

    def _apply_common_updates(self, usuario: Usuario, data: dict):
        """Helper to apply updates common to all user types."""
        if 'nome' in data:
            usuario.nome = data['nome']
        if 'email' in data and data['email'] != usuario.email:
            existing = self.repository.get_by_user(_user_lookup(email=data['email']))
            if existing and existing.id != usuario.id:
                raise ValueError(f"Email '{data['email']}' já está em uso.")
            usuario.email = data['email']
        if 'senha' in data:
            usuario.senha = data['senha'] # Assuming already hashed
        if 'data_nascimento' in data:
            usuario.data_nascimento = data['data_nascimento']

    def delete_cliente(self, id: int) -> bool:
        """Delete a cliente by ID."""
        cliente = self.repository.get_cliente_by_id(id)
        if not cliente:
            return False
        return self.repository.delete(cliente)

    def delete_funcionario(self, id: int) -> bool:
        """Delete a funcionario by ID."""
        funcionario = self.repository.get_funcionario_by_id(id)
        if not funcionario:
            return False
        return self.repository.delete(funcionario)
