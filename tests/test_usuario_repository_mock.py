"""
Tests for UsuarioRepositoryMock
"""

import pytest
from app.repository.mock.usuario_repository_mock import UsuarioRepositoryMock
from app.database.mock_data_source import MockDataSource
from app.models.usuario.cliente import Cliente
from app.models.usuario.funcionario import Funcionario
from app.models.usuario.usuario import Usuario
from app.models.enums import TipoCliente


class TestUsuarioRepositoryMock:
    """Test cases for UsuarioRepositoryMock"""

    @pytest.fixture
    def repository(self):
        """Create a fresh repository for each test"""
        return UsuarioRepositoryMock()

    def test_list_all(self, repository):
        """Test listing all users"""
        usuarios = repository.list_all()
        assert isinstance(usuarios, list)
        assert len(usuarios) > 0
        assert all(isinstance(u, Usuario) for u in usuarios)

    def test_list_clientes(self, repository):
        """Test listing all clientes"""
        clientes = repository.list_clientes()
        assert isinstance(clientes, list)
        assert len(clientes) > 0
        assert all(isinstance(c, Cliente) for c in clientes)

    def test_list_funcionarios(self, repository):
        """Test listing all funcionarios"""
        funcionarios = repository.list_funcionarios()
        assert isinstance(funcionarios, list)
        assert len(funcionarios) > 0
        assert all(isinstance(f, Funcionario) for f in funcionarios)

    def test_get_by_id_cliente(self, repository):
        """Test getting cliente by ID"""
        clientes = repository.list_clientes()
        if clientes:
            first_cliente = clientes[0]
            found_usuario = repository.get_by_id(first_cliente.id)
            assert found_usuario is not None
            assert isinstance(found_usuario, Cliente)
            assert found_usuario.id == first_cliente.id

    def test_get_by_id_funcionario(self, repository):
        """Test getting funcionario by ID"""
        funcionarios = repository.list_funcionarios()
        if funcionarios:
            first_funcionario = funcionarios[0]
            found_usuario = repository.get_by_id(first_funcionario.id)
            assert found_usuario is not None
            assert isinstance(found_usuario, Funcionario)
            assert found_usuario.id == first_funcionario.id

    def test_get_by_id_not_found(self, repository):
        """Test getting non-existent user by ID"""
        result = repository.get_by_id(99999)
        assert result is None

    def test_get_cliente_by_id(self, repository):
        """Test getting cliente by ID with specific method"""
        clientes = repository.list_clientes()
        if clientes:
            first_cliente = clientes[0]
            found_cliente = repository.get_cliente_by_id(first_cliente.id)
            assert found_cliente is not None
            assert isinstance(found_cliente, Cliente)
            assert found_cliente.id == first_cliente.id

    def test_get_funcionario_by_id(self, repository):
        """Test getting funcionario by ID with specific method"""
        funcionarios = repository.list_funcionarios()
        if funcionarios:
            first_funcionario = funcionarios[0]
            found_funcionario = repository.get_funcionario_by_id(first_funcionario.id)
            assert found_funcionario is not None
            assert isinstance(found_funcionario, Funcionario)
            assert found_funcionario.id == first_funcionario.id

    def test_get_by_user_cpf(self, repository):
        """Test getting user by CPF"""
        clientes = repository.list_clientes()
        if clientes:
            first_cliente = clientes[0]
            search_usuario = Usuario(cpf=first_cliente.cpf)
            found_usuario = repository.get_by_user(search_usuario)
            assert found_usuario is not None
            assert found_usuario.cpf == first_cliente.cpf

    def test_get_by_user_email(self, repository):
        """Test getting user by email"""
        clientes = repository.list_clientes()
        if clientes:
            first_cliente = clientes[0]
            search_usuario = Usuario(email=first_cliente.email)
            found_usuario = repository.get_by_user(search_usuario)
            assert found_usuario is not None
            assert found_usuario.email == first_cliente.email

    def test_get_cliente_by_cpf(self, repository):
        """Test getting cliente by CPF"""
        clientes = repository.list_clientes()
        if clientes:
            first_cliente = clientes[0]
            found_cliente = repository.get_cliente_by_cpf(first_cliente.cpf)
            assert found_cliente is not None
            assert isinstance(found_cliente, Cliente)
            assert found_cliente.cpf == first_cliente.cpf

    def test_get_funcionario_by_matricula(self, repository):
        """Test getting funcionario by matricula"""
        funcionarios = repository.list_funcionarios()
        if funcionarios:
            first_funcionario = funcionarios[0]
            found_funcionario = repository.get_funcionario_by_matricula(first_funcionario.matricula)
            assert found_funcionario is not None
            assert isinstance(found_funcionario, Funcionario)
            assert found_funcionario.matricula == first_funcionario.matricula

    def test_create_cliente(self, repository):
        """Test creating a new cliente"""
        initial_count = len(repository.list_clientes())
        
        new_cliente = Cliente(
            nome="Test Cliente",
            cpf="123.456.789-00",
            email="test@example.com",
            senha="password123",
            tipo_cliente=TipoCliente.REGULAR.value
        )
        
        created_cliente = repository.create(new_cliente)
        assert created_cliente is not None
        assert created_cliente.id is not None
        assert created_cliente.nome == "Test Cliente"
        
        # Verify it was added
        final_count = len(repository.list_clientes())
        assert final_count == initial_count + 1

    def test_create_funcionario(self, repository):
        """Test creating a new funcionario"""
        initial_count = len(repository.list_funcionarios())
        
        new_funcionario = Funcionario(
            matricula="TEST001",
            nome="Test Funcionario",
            cpf="987.654.321-00",
            email="func@test.com",
            senha="password123",
            cargo="Test Cargo",
            setor="Test Setor"
        )
        
        created_funcionario = repository.create(new_funcionario)
        assert created_funcionario is not None
        assert created_funcionario.id is not None
        assert created_funcionario.nome == "Test Funcionario"
        
        # Verify it was added
        final_count = len(repository.list_funcionarios())
        assert final_count == initial_count + 1

    def test_create_invalid_type(self, repository):
        """Test creating invalid user type"""
        invalid_usuario = Usuario(nome="Invalid")
        result = repository.create(invalid_usuario)
        assert result is None

    def test_update_cliente(self, repository):
        """Test updating a cliente"""
        clientes = repository.list_clientes()
        if clientes:
            cliente = clientes[0]
            original_name = cliente.nome
            cliente.nome = "Updated Name"
            
            updated_cliente = repository.update(cliente)
            assert updated_cliente is not None
            assert updated_cliente.nome == "Updated Name"
            
            # Verify the change persisted
            found_cliente = repository.get_cliente_by_id(cliente.id)
            assert found_cliente.nome == "Updated Name"

    def test_update_funcionario(self, repository):
        """Test updating a funcionario"""
        funcionarios = repository.list_funcionarios()
        if funcionarios:
            funcionario = funcionarios[0]
            original_cargo = funcionario.cargo
            funcionario.cargo = "Updated Cargo"
            
            updated_funcionario = repository.update(funcionario)
            assert updated_funcionario is not None
            assert updated_funcionario.cargo == "Updated Cargo"
            
            # Verify the change persisted
            found_funcionario = repository.get_funcionario_by_id(funcionario.id)
            assert found_funcionario.cargo == "Updated Cargo"

    def test_delete_cliente(self, repository):
        """Test deleting a cliente"""
        # First create a cliente to delete
        new_cliente = Cliente(
            nome="To Delete",
            cpf="999.999.999-99",
            email="delete@test.com",
            senha="password"
        )
        created_cliente = repository.create(new_cliente)
        
        initial_count = len(repository.list_clientes())
        
        # Delete it
        result = repository.delete(created_cliente)
        assert result is True
        
        # Verify it was deleted
        final_count = len(repository.list_clientes())
        assert final_count == initial_count - 1
        
        # Verify it can't be found
        found_cliente = repository.get_cliente_by_id(created_cliente.id)
        assert found_cliente is None

    def test_delete_funcionario(self, repository):
        """Test deleting a funcionario"""
        # First create a funcionario to delete
        new_funcionario = Funcionario(
            matricula="DEL001",
            nome="To Delete",
            cpf="888.888.888-88",
            email="del@test.com",
            senha="password"
        )
        created_funcionario = repository.create(new_funcionario)
        
        initial_count = len(repository.list_funcionarios())
        
        # Delete it
        result = repository.delete(created_funcionario)
        assert result is True
        
        # Verify it was deleted
        final_count = len(repository.list_funcionarios())
        assert final_count == initial_count - 1
        
        # Verify it can't be found
        found_funcionario = repository.get_funcionario_by_id(created_funcionario.id)
        assert found_funcionario is None

    def test_delete_without_id(self, repository):
        """Test deleting entity without ID"""
        cliente = Cliente(nome="No ID")
        result = repository.delete(cliente)
        assert result is False
