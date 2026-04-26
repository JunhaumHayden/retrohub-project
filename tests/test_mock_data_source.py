"""
Tests for MockDataSource
"""

import pytest
from app.database.mock_data_source import MockDataSource
from app.models.usuario.cliente import Cliente
from app.models.usuario.funcionario import Funcionario
from app.models.catalogo.catalogo import Catalogo
from app.models.enums import StatusCatalogo, TipoCliente


class TestMockDataSource:
    """Test cases for MockDataSource"""

    @pytest.fixture
    def data_source(self):
        """Create a fresh data source for each test"""
        ds = MockDataSource()
        ds.load_data()
        return ds

    def test_load_data(self, data_source):
        """Test that data loads correctly"""
        assert data_source._loaded is True
        assert len(data_source.get_all(Cliente)) > 0
        assert len(data_source.get_all(Funcionario)) > 0
        assert len(data_source.get_all(Catalogo)) > 0

    def test_get_all_clientes(self, data_source):
        """Test getting all clientes"""
        clientes = data_source.get_all(Cliente)
        assert isinstance(clientes, list)
        assert len(clientes) > 0
        assert all(isinstance(c, Cliente) for c in clientes)

    def test_get_all_funcionarios(self, data_source):
        """Test getting all funcionarios"""
        funcionarios = data_source.get_all(Funcionario)
        assert isinstance(funcionarios, list)
        assert len(funcionarios) > 0
        assert all(isinstance(f, Funcionario) for f in funcionarios)

    def test_get_all_catalogo(self, data_source):
        """Test getting all catalog items"""
        catalogos = data_source.get_all(Catalogo)
        assert isinstance(catalogos, list)
        assert len(catalogos) > 0
        assert all(isinstance(c, Catalogo) for c in catalogos)

    def test_get_by_id_cliente(self, data_source):
        """Test getting cliente by ID"""
        # Get first cliente to test with
        clientes = data_source.get_all(Cliente)
        if clientes:
            first_cliente = clientes[0]
            found_cliente = data_source.get_by_id(Cliente, first_cliente.id)
            assert found_cliente is not None
            assert found_cliente.id == first_cliente.id
            assert found_cliente.nome == first_cliente.nome

    def test_get_by_id_not_found(self, data_source):
        """Test getting non-existent entity by ID"""
        result = data_source.get_by_id(Cliente, 99999)
        assert result is None

    def test_get_by_field(self, data_source):
        """Test getting entity by field value"""
        # Test by CPF
        clientes = data_source.get_all(Cliente)
        if clientes:
            first_cliente = clientes[0]
            found_cliente = data_source.get_by_field(Cliente, 'cpf', first_cliente.cpf)
            assert found_cliente is not None
            assert found_cliente.cpf == first_cliente.cpf

    def test_create_cliente(self, data_source):
        """Test creating a new cliente"""
        initial_count = len(data_source.get_all(Cliente))
        
        new_cliente = Cliente(
            nome="Test Cliente",
            cpf="123.456.789-00",
            email="test@example.com",
            senha="password123",
            tipo_cliente=TipoCliente.REGULAR.value
        )
        
        created_cliente = data_source.create(new_cliente)
        assert created_cliente is not None
        assert created_cliente.id is not None
        assert created_cliente.nome == "Test Cliente"
        
        # Verify it was added
        final_count = len(data_source.get_all(Cliente))
        assert final_count == initial_count + 1

    def test_create_catalogo(self, data_source):
        """Test creating a new catalog item"""
        initial_count = len(data_source.get_all(Catalogo))
        
        new_catalogo = Catalogo(
            titulo="Test Game",
            descricao="A test game",
            genero="Test",
            classificacao="Livre",
            situacao=StatusCatalogo.DISPONIVEL.value
        )
        
        created_catalogo = data_source.create(new_catalogo)
        assert created_catalogo is not None
        assert created_catalogo.id is not None
        assert created_catalogo.titulo == "Test Game"
        
        # Verify it was added
        final_count = len(data_source.get_all(Catalogo))
        assert final_count == initial_count + 1

    def test_update_cliente(self, data_source):
        """Test updating a cliente"""
        clientes = data_source.get_all(Cliente)
        if clientes:
            cliente = clientes[0]
            original_name = cliente.nome
            cliente.nome = "Updated Name"
            
            updated_cliente = data_source.update(cliente)
            assert updated_cliente is not None
            assert updated_cliente.nome == "Updated Name"
            
            # Verify the change persisted
            found_cliente = data_source.get_by_id(Cliente, cliente.id)
            assert found_cliente.nome == "Updated Name"

    def test_update_nonexistent(self, data_source):
        """Test updating non-existent entity"""
        fake_cliente = Cliente(id=99999, nome="Fake", cpf="000", email="fake@test.com")
        result = data_source.update(fake_cliente)
        assert result is None

    def test_delete_cliente(self, data_source):
        """Test deleting a cliente"""
        # First create a cliente to delete
        new_cliente = Cliente(
            nome="To Delete",
            cpf="999.999.999-99", 
            email="delete@test.com",
            senha="password"
        )
        created_cliente = data_source.create(new_cliente)
        
        initial_count = len(data_source.get_all(Cliente))
        
        # Delete it
        result = data_source.delete(Cliente, created_cliente.id)
        assert result is True
        
        # Verify it was deleted
        final_count = len(data_source.get_all(Cliente))
        assert final_count == initial_count - 1
        
        # Verify it can't be found
        found_cliente = data_source.get_by_id(Cliente, created_cliente.id)
        assert found_cliente is None

    def test_delete_nonexistent(self, data_source):
        """Test deleting non-existent entity"""
        result = data_source.delete(Cliente, 99999)
        assert result is False

    def test_get_next_id(self, data_source):
        """Test getting next available ID"""
        # Get current max ID
        clientes = data_source.get_all(Cliente)
        if clientes:
            max_id = max(c.id for c in clientes)
            next_id = data_source.get_next_id(Cliente)
            assert next_id > max_id

    def test_ensure_loaded(self, data_source):
        """Test that ensure_loaded works"""
        # Create new data source without loading
        new_ds = MockDataSource()
        assert new_ds._loaded is False
        
        # Call ensure_loaded through get_all
        clientes = new_ds.get_all(Cliente)
        assert new_ds._loaded is True
        assert isinstance(clientes, list)
