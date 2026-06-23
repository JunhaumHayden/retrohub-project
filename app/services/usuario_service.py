from typing import List, Optional
import re
from datetime import datetime

from app.models.usuario.usuario import Usuario
from app.models.usuario.cliente import Cliente
from app.models.usuario.funcionario import Funcionario
from app.repository.interface.usuario_repository_interface import UsuarioRepositoryInterface
from app.models.enums import TipoCliente


class UsuarioService:
    """
    Service layer for Usuario operations
    Handles business logic and validation
    """

    def __init__(self, repository: UsuarioRepositoryInterface):
        self.repository = repository

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    @staticmethod
    def _calculate_age(birthdate) -> int:
        """Calculate age from birthdate"""
        today = datetime.today().date()
        return (
            today.year
            - birthdate.year
            - ((today.month, today.day) < (birthdate.month, birthdate.day))
        )

    def _validate_common_fields(self, usuario: Usuario) -> None:
        """Validate common fields for any Usuario (nome, cpf, email, senha)"""
        if not usuario.nome:
            raise ValueError("Nome é obrigatório")
        if not usuario.cpf:
            raise ValueError("CPF é obrigatório")
        if not usuario.email:
            raise ValueError("Email é obrigatório")
        if not usuario.senha:
            raise ValueError("Senha é obrigatória")

    def _check_existing_cpf(self, cpf: str, exclude_id: Optional[int] = None) -> None:
        """Check if CPF already exists (optionally excluding a specific ID)"""
        existing_cliente = self.repository.get_cliente_by_cpf(cpf)
        if existing_cliente and (exclude_id is None or existing_cliente.id != exclude_id):
            raise ValueError(f"Cliente com CPF '{cpf}' já existe")

        existing_funcionario = self.repository.get_by_cpf(cpf)
        if existing_funcionario and (exclude_id is None or existing_funcionario.id != exclude_id):
            raise ValueError(f"Funcionário com CPF '{cpf}' já existe")

    def _check_existing_email(self, email: str, exclude_id: Optional[int] = None) -> None:
        """Check if email already exists (optionally excluding a specific ID)"""
        existing = self.repository.get_by_email(email)
        if existing and (exclude_id is None or existing.id != exclude_id):
            raise ValueError(f"Email '{email}' já está em uso")

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

        # Try funcionario by CPF through get_by_cpf
        return self.repository.get_by_cpf(cpf)

    def get_funcionario_by_matricula(self, matricula: str) -> Optional[Funcionario]:
        """Get funcionario by matricula"""
        return self.repository.get_funcionario_by_matricula(matricula)

    def create_cliente(self, cliente: Cliente) -> Optional[Cliente]:
        """Create a new cliente with validation"""
        self._validate_common_fields(cliente)

        # Validate email format
        if not self._is_valid_email(cliente.email):
            raise ValueError("Formato de e-mail inválido")

        # Validate age if birthdate is provided
        if cliente.data_nascimento and self._calculate_age(cliente.data_nascimento) < 18:
            raise ValueError("O cliente deve ter pelo menos 18 anos")

        # Check if CPF already exists
        self._check_existing_cpf(cliente.cpf)

        # Check if email already exists
        self._check_existing_email(cliente.email)

        # Set default tipo_cliente if not provided
        if not cliente.tipo_cliente:
            cliente.tipo_cliente = TipoCliente.BASICO.value

        return self.repository.create(cliente)

    def create_funcionario(self, funcionario: Funcionario) -> Optional[Funcionario]:
        """Create a new funcionario with validation"""
        self._validate_common_fields(funcionario)

        if not funcionario.matricula:
            raise ValueError("Matrícula é obrigatória")

        # Validate email format
        if not self._is_valid_email(funcionario.email):
            raise ValueError("Formato de e-mail inválido")

        # Validate age if birthdate is provided
        if funcionario.data_nascimento and self._calculate_age(funcionario.data_nascimento) < 18:
            raise ValueError("O funcionário deve ter pelo menos 18 anos")

        # Check if CPF already exists
        self._check_existing_cpf(funcionario.cpf)

        # Check if email already exists
        self._check_existing_email(funcionario.email)

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
            # Validate email format
            if not self._is_valid_email(new_email):
                raise ValueError("Formato de e-mail inválido")
            # Check if email is being changed and if new email already exists
            if new_email != usuario.email:
                self._check_existing_email(new_email, exclude_id=id)
            usuario.email = new_email
        if 'senha' in usuario_data:
            usuario.senha = usuario_data['senha']

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
            if 'matricula' in usuario_data:
                new_matricula = usuario_data['matricula']
                # Check if matricula is being changed and if new matricula already exists
                if new_matricula != usuario.matricula:
                    existing = self.repository.get_funcionario_by_matricula(new_matricula)
                    if existing and existing.id != id:
                        raise ValueError(f"Matrícula '{new_matricula}' já existe")
                usuario.matricula = new_matricula
            if 'data_nascimento' in usuario_data:
                new_birthdate = usuario_data['data_nascimento']
                # Validate age if birthdate is being changed
                if new_birthdate and self._calculate_age(new_birthdate) < 18:
                    raise ValueError("O funcionário deve ter pelo menos 18 anos")
                usuario.data_nascimento = new_birthdate

        return self.repository.update(usuario)

    def update_cliente(self, id: int, cliente_data: dict) -> Optional[Cliente]:
        """Update an existing cliente"""
        cliente = self.repository.get_cliente_by_id(id)
        if not cliente:
            return None

        # Update common fields
        if 'nome' in cliente_data:
            cliente.nome = cliente_data['nome']
        if 'email' in cliente_data:
            new_email = cliente_data['email']
            # Validate email format
            if not self._is_valid_email(new_email):
                raise ValueError("Formato de e-mail inválido")
            # Check if email is being changed and if new email already exists
            if new_email != cliente.email:
                self._check_existing_email(new_email, exclude_id=id)
            cliente.email = new_email
        if 'senha' in cliente_data:
            cliente.senha = cliente_data['senha']
        if 'data_nascimento' in cliente_data:
            new_birthdate = cliente_data['data_nascimento']
            # Validate age if birthdate is being changed
            if new_birthdate and self._calculate_age(new_birthdate) < 18:
                raise ValueError("O cliente deve ter pelo menos 18 anos")
            cliente.data_nascimento = new_birthdate
        if 'dados_pagamento' in cliente_data:
            cliente.dados_pagamento = cliente_data['dados_pagamento']
        if 'tipo_cliente' in cliente_data:
            cliente.tipo_cliente = cliente_data['tipo_cliente']

        return self.repository.update(cliente)

    def delete_usuario(self, id: int) -> bool:
        """Delete a user"""
        usuario = self.repository.get_by_id(id)
        if not usuario:
            return False
        return self.repository.delete(usuario)

    def delete_cliente(self, id: int) -> bool:
        """Delete a cliente"""
        cliente = self.repository.get_cliente_by_id(id)
        if not cliente:
            return False
        return self.repository.delete(cliente)
