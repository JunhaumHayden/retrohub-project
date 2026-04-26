from types import SimpleNamespace
from typing import List, Optional

from app.models.usuario.usuario import Usuario
from app.models.usuario.cliente import Cliente
from app.models.usuario.funcionario import Funcionario
from app.repository.interface.usuario_repository_interface import UsuarioRepositoryInterface
from app.models.enums import TipoCliente


def _user_lookup(*, cpf: Optional[str] = None, email: Optional[str] = None) -> SimpleNamespace:
    """Cria um objeto duck-typed para passar ao ``repository.get_by_user``.

    `Usuario` é abstrato e não pode ser instanciado, então usamos um
    ``SimpleNamespace`` que expõe apenas os campos que o repositório lê
    (``cpf`` e/ou ``email``).
    """
    return SimpleNamespace(cpf=cpf, email=email)


class UsuarioService:
    """
    Service layer for Usuario operations
    Handles business logic and validation
    """

    def __init__(self, repository: UsuarioRepositoryInterface):
        self.repository = repository

    def list_all(self) -> List[Usuario]:
        """List all users (clientes and funcionarios)"""
        return self.repository.list_all()

    def list_clientes(self) -> List[Cliente]:
        """List all clientes"""
        return self.repository.list_clientes()

    def list_funcionarios(self) -> List[Funcionario]:
        """List all funcionarios"""
        return self.repository.list_funcionarios()

    def get_by_id(self, id: int) -> Optional[Usuario]:
        """Get user by ID"""
        return self.repository.get_by_id(id)

    def get_cliente_by_id(self, id: int) -> Optional[Cliente]:
        """Get cliente by ID"""
        return self.repository.get_cliente_by_id(id)

    def get_funcionario_by_id(self, id: int) -> Optional[Funcionario]:
        """Get funcionario by ID"""
        return self.repository.get_funcionario_by_id(id)

    def get_by_cpf(self, cpf: str) -> Optional[Usuario]:
        """Get user by CPF"""
        # Try cliente first
        cliente = self.repository.get_cliente_by_cpf(cpf)
        if cliente:
            return cliente
        
        # Try funcionario by CPF through get_by_user
        return self.repository.get_by_user(_user_lookup(cpf=cpf))

    def get_funcionario_by_matricula(self, matricula: str) -> Optional[Funcionario]:
        """Get funcionario by matricula"""
        return self.repository.get_funcionario_by_matricula(matricula)

    def create_cliente(self, cliente: Cliente) -> Optional[Cliente]:
        """Create a new cliente with validation"""
        # Validate required fields
        if not cliente.nome:
            raise ValueError("Nome é obrigatório")
        if not cliente.cpf:
            raise ValueError("CPF é obrigatório")
        if not cliente.email:
            raise ValueError("Email é obrigatório")
        if not cliente.senha:
            raise ValueError("Senha é obrigatória")
        
        # Check if CPF already exists
        existing = self.repository.get_cliente_by_cpf(cliente.cpf)
        if existing:
            raise ValueError(f"Cliente com CPF '{cliente.cpf}' já existe")
        
        # Check if email already exists
        existing_email = self.repository.get_by_user(_user_lookup(email=cliente.email))
        if existing_email:
            raise ValueError(f"Email '{cliente.email}' já está em uso")
        
        # Set default tipo_cliente if not provided
        if not cliente.tipo_cliente:
            cliente.tipo_cliente = TipoCliente.REGULAR.value
        
        return self.repository.create(cliente)

    def create_funcionario(self, funcionario: Funcionario) -> Optional[Funcionario]:
        """Create a new funcionario with validation"""
        # Validate required fields
        if not funcionario.nome:
            raise ValueError("Nome é obrigatório")
        if not funcionario.cpf:
            raise ValueError("CPF é obrigatório")
        if not funcionario.email:
            raise ValueError("Email é obrigatório")
        if not funcionario.senha:
            raise ValueError("Senha é obrigatória")
        if not funcionario.matricula:
            raise ValueError("Matrícula é obrigatória")
        
        # Check if CPF already exists
        existing = self.repository.get_by_user(_user_lookup(cpf=funcionario.cpf))
        if existing:
            raise ValueError(f"Funcionário com CPF '{funcionario.cpf}' já existe")
        
        # Check if email already exists
        existing_email = self.repository.get_by_user(_user_lookup(email=funcionario.email))
        if existing_email:
            raise ValueError(f"Email '{funcionario.email}' já está em uso")
        
        # Check if matricula already exists
        existing_matricula = self.repository.get_funcionario_by_matricula(funcionario.matricula)
        if existing_matricula:
            raise ValueError(f"Matrícula '{funcionario.matricula}' já existe")
        
        return self.repository.create(funcionario)

    def update_usuario(self, id: int, usuario_data: dict) -> Optional[Usuario]:
        """Update an existing user"""
        usuario = self.repository.get_by_id(id)
        if not usuario:
            return None
        
        # Update common fields
        if 'nome' in usuario_data:
            usuario.nome = usuario_data['nome']
        if 'email' in usuario_data:
            new_email = usuario_data['email']
            # Check if email is being changed and if new email already exists
            if new_email != usuario.email:
                existing = self.repository.get_by_user(_user_lookup(email=new_email))
                if existing and existing.id != id:
                    raise ValueError(f"Email '{new_email}' já está em uso")
            usuario.email = new_email
        if 'senha' in usuario_data:
            usuario.senha = usuario_data['senha']
        if 'data_nascimento' in usuario_data:
            usuario.data_nascimento = usuario_data['data_nascimento']

        # Update cliente-specific fields
        if isinstance(usuario, Cliente):
            if 'dados_pagamento' in usuario_data:
                usuario.dados_pagamento = usuario_data['dados_pagamento']
            if 'tipo_cliente' in usuario_data:
                usuario.tipo_cliente = usuario_data['tipo_cliente']
        
        # Update funcionario-specific fields
        elif isinstance(usuario, Funcionario):
            if 'cargo' in usuario_data:
                usuario.cargo = usuario_data['cargo']
            if 'setor' in usuario_data:
                usuario.setor = usuario_data['setor']
            if 'data_admissao' in usuario_data:
                usuario.data_admissao = usuario_data['data_admissao']
            if 'matricula' in usuario_data:
                new_matricula = usuario_data['matricula']
                # Check if matricula is being changed and if new matricula already exists
                if new_matricula != usuario.matricula:
                    existing = self.repository.get_funcionario_by_matricula(new_matricula)
                    if existing and existing.id != id:
                        raise ValueError(f"Matrícula '{new_matricula}' já existe")
                usuario.matricula = new_matricula
        
        return self.repository.update(usuario)

    def delete_usuario(self, id: int) -> bool:
        """Delete a user"""
        usuario = self.repository.get_by_id(id)
        if not usuario:
            return False
        
        return self.repository.delete(usuario)
