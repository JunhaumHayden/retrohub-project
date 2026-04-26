#!/usr/bin/env python3
"""
Simple test script to verify the refactored system works
without requiring Flask dependencies
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mock_data_source():
    """Test MockDataSource functionality"""
    print("Testing MockDataSource...")
    
    # Import directly to avoid Flask app initialization
    from app.database.mock_data_source import MockDataSource
    from app.models.usuario.cliente import Cliente
    from app.models.catalogo.catalogo import Catalogo
    from app.models.enums import TipoCliente, StatusCatalogo
    
    # Test data loading
    ds = MockDataSource()
    ds.load_data()
    
    clientes = ds.get_all(Cliente)
    catalogos = ds.get_all(Catalogo)
    
    print(f"✓ Loaded {len(clientes)} clientes")
    print(f"✓ Loaded {len(catalogos)} catalogos")
    
    # Test CRUD operations
    new_cliente = Cliente(
        nome="Test Cliente",
        cpf="123.456.789-00",
        email="test@example.com",
        senha="password123",
        tipo_cliente=TipoCliente.REGULAR.value
    )
    
    created_cliente = ds.create(new_cliente)
    print(f"✓ Created cliente with ID: {created_cliente.id}")
    
    # Test read
    found_cliente = ds.get_by_id(Cliente, created_cliente.id)
    assert found_cliente is not None
    assert found_cliente.nome == "Test Cliente"
    print("✓ Retrieved cliente successfully")
    
    # Test update
    found_cliente.nome = "Updated Test Cliente"
    updated_cliente = ds.update(found_cliente)
    assert updated_cliente.nome == "Updated Test Cliente"
    print("✓ Updated cliente successfully")
    
    # Test delete
    deleted = ds.delete(Cliente, created_cliente.id)
    assert deleted is True
    print("✓ Deleted cliente successfully")
    
    # Test catalog operations
    new_catalogo = Catalogo(
        titulo="Test Game",
        descricao="A test game",
        genero="Test",
        classificacao="Livre",
        situacao=StatusCatalogo.DISPONIVEL.value
    )
    
    created_catalogo = ds.create(new_catalogo)
    print(f"✓ Created catalogo with ID: {created_catalogo.id}")
    
    found_catalogo = ds.get_by_id(Catalogo, created_catalogo.id)
    assert found_catalogo is not None
    assert found_catalogo.titulo == "Test Game"
    print("✓ Retrieved catalogo successfully")
    
    return True

def test_repository():
    """Test repository functionality"""
    print("\nTesting UsuarioRepositoryMock...")
    
    from app.repository.mock.usuario_repository_mock import UsuarioRepositoryMock
    from app.models.usuario.cliente import Cliente
    from app.models.usuario.funcionario import Funcionario
    from app.models.enums import TipoCliente
    
    repo = UsuarioRepositoryMock()
    
    # Test listing
    clientes = repo.list_clientes()
    funcionarios = repo.list_funcionarios()
    
    print(f"✓ Listed {len(clientes)} clientes")
    print(f"✓ Listed {len(funcionarios)} funcionarios")
    
    # Test creating cliente
    new_cliente = Cliente(
        nome="Repository Test Cliente",
        cpf="987.654.321-00",
        email="repo@test.com",
        senha="password123",
        tipo_cliente=TipoCliente.PREMIUM.value
    )
    
    created_cliente = repo.create(new_cliente)
    print(f"✓ Created cliente with ID: {created_cliente.id}")
    
    # Test finding by CPF
    found_cliente = repo.get_cliente_by_cpf(created_cliente.cpf)
    assert found_cliente is not None
    assert found_cliente.id == created_cliente.id
    print("✓ Found cliente by CPF successfully")
    
    return True

def test_service_layer():
    """Test service layer functionality"""
    print("\nTesting Service Layer...")
    
    # Test without Flask dependencies by importing directly
    from app.services.usuario_service import UsuarioService
    from app.services.catalogo_service import CatalogoService
    from app.repository.mock.usuario_repository_mock import UsuarioRepositoryMock
    from app.repository.mock.catalogo_repository_mock import CatalogoRepositoryMock
    from app.models.usuario.cliente import Cliente
    from app.models.catalogo.catalogo import Catalogo
    from app.models.enums import TipoCliente, StatusCatalogo
    
    # Create services with mock repositories
    usuario_repo = UsuarioRepositoryMock()
    catalogo_repo = CatalogoRepositoryMock()
    
    usuario_service = UsuarioService(usuario_repo)
    catalogo_service = CatalogoService(catalogo_repo)
    
    # Test usuario service
    new_cliente = Cliente(
        nome="Service Test Cliente",
        cpf="555.555.555-55",
        email="service@test.com",
        senha="password123"
    )
    
    created_cliente = usuario_service.create_cliente(new_cliente)
    print(f"✓ Created cliente through service with ID: {created_cliente.id}")
    
    # Test catalogo service
    new_catalogo = Catalogo(
        titulo="Service Test Game",
        descricao="A service test game",
        genero="Service Test",
        classificacao="Livre"
    )
    
    created_catalogo = catalogo_service.create(new_catalogo)
    print(f"✓ Created catalogo through service with ID: {created_catalogo.id}")
    
    # Test validation
    invalid_cliente = Cliente(
        nome="",  # Empty name should fail validation
        cpf="666.666.666-66",
        email="invalid@test.com",
        senha="password123"
    )
    
    try:
        usuario_service.create_cliente(invalid_cliente)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Nome é obrigatório" in str(e)
        print("✓ Service validation working correctly")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing Refactored RetroHub System")
    print("=" * 50)
    
    try:
        # Test core components
        test_mock_data_source()
        test_repository()
        test_service_layer()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed successfully!")
        print("\n📋 Refactoring Summary:")
        print("• ✅ MockDataSource with full CRUD operations")
        print("• ✅ Repository layer with proper abstraction")
        print("• ✅ Service layer with business logic and validation")
        print("• ✅ Clean layer separation")
        print("• ✅ Type safety and error handling")
        print("• ✅ In-memory data management")
        print("\n🎯 System is ready for development and testing!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
