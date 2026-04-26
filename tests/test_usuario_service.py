"""
Tests for UsuarioService
"""

import pytest
from app.services.usuario_service import UsuarioService
from app.repository.mock.usuario_repository_mock import UsuarioRepositoryMock
from app.models.usuario.cliente import Cliente
from app.models.usuario.funcionario import Funcionario
from app.models.usuario.usuario import Usuario
from app.models.enums import TipoCliente


class TestUsuarioService:
    """Test cases for UsuarioService"""

    @pytest.fixture
    def service(self):
        """Create a fresh service for each test"""
        repository = UsuarioRepositoryMock()
        return UsuarioService(repository)

    def test_list_all(self, service):
        """Test listing all users"""
        usuarios = service.list_all()
        assert isinstance(usuarios, list)
        assert len(usuarios) > 0
        assert all(isinstance(u, Usuario) for u in usuarios)

    def test_list_clientes(self, service):
        """Test listing all clientes"""
        clientes = service.list_clientes()
        assert isinstance(clientes, list)
        assert len(clientes) > 0
        assert all(isinstance(c, Cliente) for c in clientes)

    def test_list_funcionarios(self, service):
        """Test listing all funcionarios"""
        funcionarios = service.list_funcionarios()
        assert isinstance(funcionarios, list)
        assert len(funcionarios) > 0
        assert all(isinstance(f, Funcionario) for f in funcionarios)

    def test_get_by_id_cliente(self, service):
        """Test getting cliente by ID"""
        clientes = service.list_clientes()
        if clientes:
            first_cliente = clientes[0]
            found_usuario = service.get_by_id(first_cliente.id)
            assert found_usuario is not None
            assert isinstance(found_usuario, Cliente)
            assert found_usuario.id == first_cliente.id

    def test_get_by_id_funcionario(self, service):
        """Test getting funcionario by ID"""
        funcionarios = service.list_funcionarios()
        if funcionarios:
            first_funcionario = funcionarios[0]
            found_usuario = service.get_by_id(first_funcionario.id)
            assert found_usuario is not None
            assert isinstance(found_usuario, Funcionario)
            assert found_usuario.id == first_funcionario.id

    def test_get_by_id_not_found(self, service):
        """Test getting non-existent user by ID"""
        result = service.get_by_id(99999)
        assert result is None

    def test_get_cliente_by_id(self, service):
        """Test getting cliente by ID with specific method"""
        clientes = service.list_clientes()
        if clientes:
            first_cliente = clientes[0]
            found_cliente = service.get_cliente_by_id(first_cliente.id)
            assert found_cliente is not None
            assert isinstance(found_cliente, Cliente)
            assert found_cliente.id == first_cliente.id

    def test_get_funcionario_by_id(self, service):
        """Test getting funcionario by ID with specific method"""
        funcionarios = service.list_funcionarios()
        if funcionarios:
            first_funcionario = funcionarios[0]
            found_funcionario = service.get_funcionario_by_id(first_funcionario.id)
            assert found_funcionario is not None
            assert isinstance(found_funcionario, Funcionario)
            assert found_funcionario.id == first_funcionario.id

    def test_get_by_cpf(self, service):
        """Test getting user by CPF"""
        clientes = service.list_clientes()
        if clientes:
            first_cliente = clientes[0]
            found_usuario = service.get_by_cpf(first_cliente.cpf)
            assert found_usuario is not None
            assert found_usuario.cpf == first_cliente.cpf

    def test_get_funcionario_by_matricula(self, service):
        """Test getting funcionario by matricula"""
        funcionarios = service.list_funcionarios()
        if funcionarios:
            first_funcionario = funcionarios[0]
            found_funcionario = service.get_funcionario_by_matricula(first_funcionario.matricula)
            assert found_funcionario is not None
            assert isinstance(found_funcionario, Funcionario)
            assert found_funcionario.matricula == first_funcionario.matricula

    def test_create_cliente_success(self, service):
        """Test successful cliente creation"""
        initial_count = len(service.list_clientes())
        
        new_cliente = Cliente(
            nome="Test Cliente",
            cpf="123.456.789-00",
            email="test@example.com",
            senha="password123",
            tipo_cliente=TipoCliente.REGULAR.value
        )
        
        created_cliente = service.create_cliente(new_cliente)
        assert created_cliente is not None
        assert created_cliente.id is not None
        assert created_cliente.nome == "Test Cliente"
        assert created_cliente.tipo_cliente == TipoCliente.REGULAR.value
        
        # Verify it was added
        final_count = len(service.list_clientes())
        assert final_count == initial_count + 1

    def test_create_cliente_no_name(self, service):
        """Test creating cliente without name"""
        new_cliente = Cliente(
            cpf="123.456.789-00",
            email="test@example.com",
            senha="password123"
        )
        
        with pytest.raises(ValueError, match="Nome é obrigatório"):
            service.create_cliente(new_cliente)

    def test_create_cliente_no_cpf(self, service):
        """Test creating cliente without CPF"""
        new_cliente = Cliente(
            nome="Test Cliente",
            email="test@example.com",
            senha="password123"
        )
        
        with pytest.raises(ValueError, match="CPF é obrigatório"):
            service.create_cliente(new_cliente)

    def test_create_cliente_no_email(self, service):
        """Test creating cliente without email"""
        new_cliente = Cliente(
            nome="Test Cliente",
            cpf="123.456.789-00",
            senha="password123"
        )
        
        with pytest.raises(ValueError, match="Email é obrigatório"):
            service.create_cliente(new_cliente)

    def test_create_cliente_no_senha(self, service):
        """Test creating cliente without senha"""
        new_cliente = Cliente(
            nome="Test Cliente",
            cpf="123.456.789-00",
            email="test@example.com"
        )
        
        with pytest.raises(ValueError, match="Senha é obrigatória"):
            service.create_cliente(new_cliente)

    def test_create_cliente_duplicate_cpf(self, service):
        """Test creating cliente with duplicate CPF"""
        clientes = service.list_clientes()
        if clientes:
            existing_cliente = clientes[0]
            
            duplicate_cliente = Cliente(
                nome="Duplicate",
                cpf=existing_cliente.cpf,
                email="duplicate@example.com",
                senha="password123"
            )
            
            with pytest.raises(ValueError, match="Cliente com CPF .* já existe"):
                service.create_cliente(duplicate_cliente)

    def test_create_cliente_duplicate_email(self, service):
        """Test creating cliente with duplicate email"""
        clientes = service.list_clientes()
        if clientes:
            existing_cliente = clientes[0]
            
            duplicate_cliente = Cliente(
                nome="Duplicate",
                cpf="999.999.999-99",
                email=existing_cliente.email,
                senha="password123"
            )
            
            with pytest.raises(ValueError, match="Email .* já está em uso"):
                service.create_cliente(duplicate_cliente)

    def test_create_funcionario_success(self, service):
        """Test successful funcionario creation"""
        initial_count = len(service.list_funcionarios())
        
        new_funcionario = Funcionario(
            matricula="TEST001",
            nome="Test Funcionario",
            cpf="987.654.321-00",
            email="func@test.com",
            senha="password123",
            cargo="Test Cargo",
            setor="Test Setor"
        )
        
        created_funcionario = service.create_funcionario(new_funcionario)
        assert created_funcionario is not None
        assert created_funcionario.id is not None
        assert created_funcionario.nome == "Test Funcionario"
        assert created_funcionario.matricula == "TEST001"
        
        # Verify it was added
        final_count = len(service.list_funcionarios())
        assert final_count == initial_count + 1

    def test_create_funcionario_no_matricula(self, service):
        """Test creating funcionario without matricula"""
        new_funcionario = Funcionario(
            nome="Test Funcionario",
            cpf="987.654.321-00",
            email="func@test.com",
            senha="password123"
        )
        
        with pytest.raises(ValueError, match="Matrícula é obrigatória"):
            service.create_funcionario(new_funcionario)

    def test_create_funcionario_duplicate_matricula(self, service):
        """Test creating funcionario with duplicate matricula"""
        funcionarios = service.list_funcionarios()
        if funcionarios:
            existing_funcionario = funcionarios[0]
            
            duplicate_funcionario = Funcionario(
                matricula=existing_funcionario.matricula,
                nome="Duplicate",
                cpf="999.999.999-99",
                email="duplicate@example.com",
                senha="password123"
            )
            
            with pytest.raises(ValueError, match="Matrícula .* já existe"):
                service.create_funcionario(duplicate_funcionario)

    def test_update_usuario_success(self, service):
        """Test successful user update"""
        clientes = service.list_clientes()
        if clientes:
            first_cliente = clientes[0]
            original_name = first_cliente.nome
            
            update_data = {
                'nome': 'Updated Name',
                'email': 'updated@example.com',
                'tipo_cliente': TipoCliente.PREMIUM.value
            }
            
            updated_usuario = service.update_usuario(first_cliente.id, update_data)
            assert updated_usuario is not None
            assert updated_usuario.nome == 'Updated Name'
            assert updated_usuario.email == 'updated@example.com'
            assert updated_usuario.tipo_cliente == TipoCliente.PREMIUM.value

    def test_update_usuario_not_found(self, service):
        """Test updating non-existent user"""
        update_data = {'nome': 'Updated Name'}
        
        result = service.update_usuario(99999, update_data)
        assert result is None

    def test_update_usuario_duplicate_email(self, service):
        """Test updating user with duplicate email"""
        clientes = service.list_clientes()
        if len(clientes) >= 2:
            first_cliente = clientes[0]
            second_cliente = clientes[1]
            
            update_data = {'email': second_cliente.email}
            
            with pytest.raises(ValueError, match="Email .* já está em uso"):
                service.update_usuario(first_cliente.id, update_data)

    def test_update_funcionario_duplicate_matricula(self, service):
        """Test updating funcionario with duplicate matricula"""
        funcionarios = service.list_funcionarios()
        if len(funcionarios) >= 2:
            first_funcionario = funcionarios[0]
            second_funcionario = funcionarios[1]
            
            update_data = {'matricula': second_funcionario.matricula}
            
            with pytest.raises(ValueError, match="Matrícula .* já existe"):
                service.update_usuario(first_funcionario.id, update_data)

    def test_delete_usuario_success(self, service):
        """Test successful user deletion"""
        # First create a cliente to delete
        new_cliente = Cliente(
            nome="To Delete",
            cpf="999.999.999-99",
            email="delete@test.com",
            senha="password123"
        )
        created_cliente = service.create_cliente(new_cliente)
        
        initial_count = len(service.list_clientes())
        
        # Delete it
        result = service.delete_usuario(created_cliente.id)
        assert result is True
        
        # Verify it was deleted
        final_count = len(service.list_clientes())
        assert final_count == initial_count - 1
        
        # Verify it can't be found
        found_cliente = service.get_cliente_by_id(created_cliente.id)
        assert found_cliente is None

    def test_delete_usuario_not_found(self, service):
        """Test deleting non-existent user"""
        result = service.delete_usuario(99999)
        assert result is False
