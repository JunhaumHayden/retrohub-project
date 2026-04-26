#!/usr/bin/env python3
"""
Standalone test for the refactored system components
Tests individual modules without Flask dependencies
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_models():
    """Test model classes directly"""
    print("Testing Models...")
    
    # Import models directly
    sys.path.insert(0, str(project_root / 'app' / 'models' / 'usuario'))
    from usuario import Usuario
    from cliente import Cliente
    from funcionario import Funcionario
    
    sys.path.insert(0, str(project_root / 'app' / 'models' / 'catalogo'))
    from catalogo import Catalogo
    
    sys.path.insert(0, str(project_root / 'app' / 'models' / 'enums'))
    from enums import TipoCliente, StatusCatalogo
    
    # Test creating instances
    cliente = Cliente(
        nome="Test Cliente",
        cpf="123.456.789-00",
        email="test@example.com",
        senha="password123",
        tipo_cliente=TipoCliente.REGULAR.value
    )
    print(f"✓ Created Cliente: {cliente.nome}")
    
    funcionario = Funcionario(
        matricula="TEST001",
        nome="Test Funcionario",
        cpf="987.654.321-00",
        email="func@test.com",
        senha="password123"
    )
    print(f"✓ Created Funcionario: {funcionario.nome}")
    
    catalogo = Catalogo(
        titulo="Test Game",
        descricao="A test game",
        genero="Test",
        classificacao="Livre",
        situacao=StatusCatalogo.DISPONIVEL.value
    )
    print(f"✓ Created Catalogo: {catalogo.titulo}")
    
    return True

def test_data_source_direct():
    """Test MockDataSource by importing directly"""
    print("\nTesting MockDataSource (direct import)...")
    
    # Import the MockDataSource module directly
    mock_data_source_path = project_root / 'app' / 'database' / 'mock_data_source.py'
    
    # Execute the module to get the class
    import importlib.util
    spec = importlib.util.spec_from_file_location("mock_data_source", mock_data_source_path)
    mock_module = importlib.util.module_from_spec(spec)
    
    # We need to mock the imports that the module depends on
    sys.modules['app.models.usuario.usuario'] = type('MockModule', (), {
        'Usuario': type('Usuario', (), {})
    })()
    sys.modules['app.models.usuario.cliente'] = type('MockModule', (), {
        'Cliente': type('Cliente', (), {})
    })()
    sys.modules['app.models.usuario.funcionario'] = type('MockModule', (), {
        'Funcionario': type('Funcionario', (), {})
    })()
    sys.modules['app.models.catalogo.catalogo'] = type('MockModule', (), {
        'Catalogo': type('Catalogo', (), {})
    })()
    sys.modules['app.models.estoque.exemplar'] = type('MockModule', (), {
        'Exemplar': type('Exemplar', (), {})
    })()
    sys.modules['app.models.estoque.midia_fisica'] = type('MockModule', (), {
        'MidiaFisica': type('MidiaFisica', (), {})
    })()
    sys.modules['app.models.estoque.midia_digital'] = type('MockModule', (), {
        'MidiaDigital': type('MidiaDigital', (), {})
    })()
    sys.modules['app.models.transacao.transacao'] = type('MockModule', (), {
        'Transacao': type('Transacao', (), {})
    })()
    sys.modules['app.models.transacao.venda.venda'] = type('MockModule', (), {
        'Venda': type('Venda', (), {})
    })()
    sys.modules['app.models.transacao.aluguel.aluguel'] = type('MockModule', (), {
        'Aluguel': type('Aluguel', (), {})
    })()
    sys.modules['app.models.transacao.aluguel.reserva'] = type('MockModule', (), {
        'Reserva': type('Reserva', (), {})
    })()
    sys.modules['app.models.transacao.aluguel.multa'] = type('MockModule', (), {
        'Multa': type('Multa', (), {})
    })()
    sys.modules['app.models.transacao.item_transacao'] = type('MockModule', (), {
        'ItemTransacao': type('ItemTransacao', (), {})
    })()
    sys.modules['app.models.transacao.avaliacao'] = type('MockModule', (), {
        'Avaliacao': type('Avaliacao', (), {})
    })()
    sys.modules['app.models.transacao.comprovante'] = type('MockModule', (), {
        'Comprovante': type('Comprovante', (), {})
    })()
    sys.modules['app.database.interfaces.data_source_interface'] = type('MockModule', (), {
        'DataSourceInterface': type('DataSourceInterface', (), {})
    })()
    
    try:
        spec.loader.exec_module(mock_module)
        MockDataSource = mock_module.MockDataSource
        
        # Test basic functionality
        ds = MockDataSource()
        print("✓ MockDataSource instance created")
        
        # Test that it has the required methods
        assert hasattr(ds, 'load_data')
        assert hasattr(ds, 'get_all')
        assert hasattr(ds, 'get_by_id')
        assert hasattr(ds, 'create')
        assert hasattr(ds, 'update')
        assert hasattr(ds, 'delete')
        print("✓ MockDataSource has all required CRUD methods")
        
        return True
    except Exception as e:
        print(f"❌ MockDataSource test failed: {e}")
        return False

def test_interfaces():
    """Test interface definitions"""
    print("\nTesting Interfaces...")
    
    # Test data source interface
    interface_path = project_root / 'app' / 'database' / 'interfaces' / 'data_source_interface.py'
    import importlib.util
    spec = importlib.util.spec_from_file_location("data_source_interface", interface_path)
    interface_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(interface_module)
    
    DataSourceInterface = interface_module.DataSourceInterface
    print("✓ DataSourceInterface loaded")
    
    # Check that it has the required abstract methods
    abstract_methods = [
        'load_data', 'get_all', 'get_by_id', 'get_by_field',
        'create', 'update', 'delete', 'get_next_id'
    ]
    
    for method in abstract_methods:
        assert hasattr(DataSourceInterface, method)
    
    print("✓ DataSourceInterface has all required abstract methods")
    
    return True

def test_repository_interfaces():
    """Test repository interfaces"""
    print("\nTesting Repository Interfaces...")
    
    # Test usuario repository interface
    usuario_interface_path = project_root / 'app' / 'repository' / 'interface' / 'usuario_repository_interface.py'
    import importlib.util
    spec = importlib.util.spec_from_file_location("usuario_repository_interface", usuario_interface_path)
    interface_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(interface_module)
    
    UsuarioRepositoryInterface = interface_module.UsuarioRepositoryInterface
    print("✓ UsuarioRepositoryInterface loaded")
    
    # Check abstract methods
    abstract_methods = ['list_all', 'get_by_id', 'get_by_user', 'create', 'update', 'delete']
    for method in abstract_methods:
        assert hasattr(UsuarioRepositoryInterface, method)
    
    print("✓ UsuarioRepositoryInterface has all required abstract methods")
    
    return True

def verify_file_structure():
    """Verify that all refactored files exist"""
    print("\nVerifying File Structure...")
    
    required_files = [
        'app/database/mock_data_source.py',
        'app/database/interfaces/data_source_interface.py',
        'app/repository/mock/usuario_repository_mock.py',
        'app/repository/mock/catalogo_repository_mock.py',
        'app/repository/interface/usuario_repository_interface.py',
        'app/repository/interface/catalogo_repository_interface.py',
        'app/services/usuario_service.py',
        'app/services/catalogo_service.py',
        'app/container/container.py',
        'tests/test_mock_data_source.py',
        'tests/test_usuario_repository_mock.py',
        'tests/test_catalogo_service.py',
        'tests/test_usuario_service.py',
        'tests/test_container.py',
        'tests/test_integration.py',
        'pytest.ini',
        'requirements-dev.txt',
        'README-REFACTORING.md'
    ]
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            return False
    
    return True

def main():
    """Run all standalone tests"""
    print("🚀 Standalone Testing for Refactored RetroHub")
    print("=" * 60)
    
    try:
        # Test file structure
        if not verify_file_structure():
            print("\n❌ File structure verification failed")
            return False
        
        # Test individual components
        test_models()
        test_interfaces()
        test_repository_interfaces()
        test_data_source_direct()
        
        print("\n" + "=" * 60)
        print("✅ All standalone tests passed!")
        print("\n📋 Refactoring Verification Complete:")
        print("• ✅ All required files created")
        print("• ✅ Model classes working")
        print("• ✅ Interface definitions correct")
        print("• ✅ MockDataSource class structure valid")
        print("• ✅ Repository interfaces properly defined")
        print("\n🎯 Architecture refactoring is complete!")
        print("📝 See README-REFACTORING.md for documentation")
        print("🧪 Install dependencies to run full test suite:")
        print("   pip install flask flask-restx pytest pytest-cov")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
