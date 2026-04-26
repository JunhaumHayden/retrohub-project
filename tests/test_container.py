"""
Tests for Dependency Injection Container
"""

import pytest
from app.container.container import Container
from app.database.mock_data_source import MockDataSource
from app.repository.mock.usuario_repository_mock import UsuarioRepositoryMock
from app.repository.mock.catalogo_repository_mock import CatalogoRepositoryMock
from app.services.usuario_service import UsuarioService
from app.services.catalogo_service import CatalogoService
from app.models.usuario.cliente import Cliente
from app.models.catalogo.catalogo import Catalogo


class TestContainer:
    """Test cases for Dependency Injection Container"""

    @pytest.fixture
    def container(self):
        """Create a fresh container for each test"""
        return Container()

    def test_data_source_singleton(self, container):
        """Test that data source is singleton"""
        ds1 = container.data_source
        ds2 = container.data_source
        assert ds1 is ds2
        assert isinstance(ds1, MockDataSource)
        assert ds1._loaded is True

    def test_usuario_repository_singleton(self, container):
        """Test that usuario repository is singleton"""
        repo1 = container.usuario_repository
        repo2 = container.usuario_repository
        assert repo1 is repo2
        assert isinstance(repo1, UsuarioRepositoryMock)

    def test_catalogo_repository_singleton(self, container):
        """Test that catalogo repository is singleton"""
        repo1 = container.catalogo_repository
        repo2 = container.catalogo_repository
        assert repo1 is repo2
        assert isinstance(repo1, CatalogoRepositoryMock)

    def test_usuario_service_singleton(self, container):
        """Test that usuario service is singleton"""
        service1 = container.usuario_service
        service2 = container.usuario_service
        assert service1 is service2
        assert isinstance(service1, UsuarioService)

    def test_catalogo_service_singleton(self, container):
        """Test that catalogo service is singleton"""
        service1 = container.catalogo_service
        service2 = container.catalogo_service
        assert service1 is service2
        assert isinstance(service1, CatalogoService)

    def test_dependencies_injected(self, container):
        """Test that dependencies are properly injected"""
        # Check that repository uses the data source
        repo = container.usuario_repository
        assert repo.data_source is container.data_source

        # Check that service uses the repository
        service = container.usuario_service
        assert service.repository is container.usuario_repository

        catalogo_service = container.catalogo_service
        assert catalogo_service.repository is container.catalogo_repository

    def test_data_is_loaded(self, container):
        """Test that data is loaded when accessed"""
        clientes = container.usuario_service.list_clientes()
        assert isinstance(clientes, list)
        assert len(clientes) > 0

        catalogos = container.catalogo_service.list_all()
        assert isinstance(catalogos, list)
        assert len(catalogos) > 0

    def test_reset(self, container):
        """Test that reset clears all instances"""
        # Access all services to create instances
        old_ds = container.data_source
        _ = container.usuario_repository
        _ = container.catalogo_repository
        _ = container.usuario_service
        _ = container.catalogo_service

        # Reset
        container.reset()

        # Verify that a new instance is created after reset
        new_ds = container.data_source
        ds_again = container.data_source
        assert new_ds is ds_again  # singleton after reset
        assert new_ds is not old_ds  # different from pre-reset instance

    def test_container_integration(self, container):
        """Test full integration through container"""
        # Create a cliente through service
        new_cliente = Cliente(
            nome="Container Test",
            cpf="111.222.333-44",
            email="container@test.com",
            senha="password123"
        )
        
        created_cliente = container.usuario_service.create_cliente(new_cliente)
        assert created_cliente is not None
        assert created_cliente.id is not None

        # Retrieve through service
        found_cliente = container.usuario_service.get_cliente_by_id(created_cliente.id)
        assert found_cliente is not None
        assert found_cliente.nome == "Container Test"

        # Create a catalog item through service
        new_catalogo = Catalogo(
            titulo="Container Test Game",
            descricao="Test game for container",
            genero="Test"
        )
        
        created_catalogo = container.catalogo_service.create(new_catalogo)
        assert created_catalogo is not None
        assert created_catalogo.id is not None

        # Retrieve through service
        found_catalogo = container.catalogo_service.get_by_id(created_catalogo.id)
        assert found_catalogo is not None
        assert found_catalogo.titulo == "Container Test Game"
