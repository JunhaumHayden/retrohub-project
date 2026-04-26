"""
Integration tests for the refactored system
"""

import pytest
from app.container.container import container
from app.models.usuario.cliente import Cliente
from app.models.usuario.funcionario import Funcionario
from app.models.catalogo.catalogo import Catalogo
from app.models.enums import TipoCliente, StatusCatalogo


class TestIntegration:
    """Integration tests for the complete system"""

    @pytest.fixture(autouse=True)
    def reset_container(self):
        """Reset container before each test"""
        container.reset()

    def test_complete_cliente_workflow(self):
        """Test complete cliente workflow: create, read, update, delete"""
        # Create
        new_cliente = Cliente(
            nome="Integration Test Cliente",
            cpf="123.456.789-00",
            email="integration@test.com",
            senha="password123",
            tipo_cliente=TipoCliente.PREMIUM.value
        )
        
        created_cliente = container.usuario_service.create_cliente(new_cliente)
        assert created_cliente is not None
        assert created_cliente.id is not None
        
        # Read
        found_cliente = container.usuario_service.get_cliente_by_id(created_cliente.id)
        assert found_cliente is not None
        assert found_cliente.nome == "Integration Test Cliente"
        assert found_cliente.tipo_cliente == TipoCliente.PREMIUM.value
        
        # Update
        update_data = {
            'nome': 'Updated Integration Cliente',
            'tipo_cliente': TipoCliente.REGULAR.value
        }
        updated_cliente = container.usuario_service.update_usuario(created_cliente.id, update_data)
        assert updated_cliente is not None
        assert updated_cliente.nome == 'Updated Integration Cliente'
        assert updated_cliente.tipo_cliente == TipoCliente.REGULAR.value
        
        # Verify update persisted
        found_updated = container.usuario_service.get_cliente_by_id(created_cliente.id)
        assert found_updated.nome == 'Updated Integration Cliente'
        
        # Delete
        delete_result = container.usuario_service.delete_usuario(created_cliente.id)
        assert delete_result is True
        
        # Verify deletion
        found_deleted = container.usuario_service.get_cliente_by_id(created_cliente.id)
        assert found_deleted is None

    def test_complete_catalogo_workflow(self):
        """Test complete catalogo workflow: create, read, update, delete"""
        # Create
        new_catalogo = Catalogo(
            titulo="Integration Test Game",
            descricao="A game for integration testing",
            genero="Integration",
            classificacao="Livre",
            situacao=StatusCatalogo.DISPONIVEL.value
        )
        
        created_catalogo = container.catalogo_service.create(new_catalogo)
        assert created_catalogo is not None
        assert created_catalogo.id is not None
        
        # Read
        found_catalogo = container.catalogo_service.get_by_id(created_catalogo.id)
        assert found_catalogo is not None
        assert found_catalogo.titulo == "Integration Test Game"
        assert found_catalogo.situacao == StatusCatalogo.DISPONIVEL.value
        
        # Update
        update_data = {
            'titulo': 'Updated Integration Game',
            'descricao': 'Updated description',
            'genero': 'Updated Genre'
        }
        updated_catalogo = container.catalogo_service.update(created_catalogo.id, update_data)
        assert updated_catalogo is not None
        assert updated_catalogo.titulo == 'Updated Integration Game'
        assert updated_catalogo.descricao == 'Updated description'
        
        # Verify update persisted
        found_updated = container.catalogo_service.get_by_id(created_catalogo.id)
        assert found_updated.titulo == 'Updated Integration Game'
        
        # Inactivate (soft delete)
        inactivated_catalogo = container.catalogo_service.inactivate(created_catalogo.id)
        assert inactivated_catalogo is not None
        assert inactivated_catalogo.situacao == StatusCatalogo.INDISPONIVEL.value
        
        # Reactivate
        reactivated_catalogo = container.catalogo_service.activate(created_catalogo.id)
        assert reactivated_catalogo is not None
        assert reactivated_catalogo.situacao == StatusCatalogo.DISPONIVEL.value
        
        # Delete
        delete_result = container.catalogo_service.delete(created_catalogo.id)
        assert delete_result is True
        
        # Verify deletion
        found_deleted = container.catalogo_service.get_by_id(created_catalogo.id)
        assert found_deleted is None

    def test_cross_entity_operations(self):
        """Test operations that involve multiple entity types"""
        # Create a funcionario
        new_funcionario = Funcionario(
            matricula="INT001",
            nome="Integration Funcionario",
            cpf="987.654.321-00",
            email="funcionario@integration.com",
            senha="password123",
            cargo="Integration Tester",
            setor="Quality Assurance"
        )
        
        created_funcionario = container.usuario_service.create_funcionario(new_funcionario)
        assert created_funcionario is not None
        
        # Create multiple catalog items
        catalogos = []
        for i in range(3):
            catalogo = Catalogo(
                title=f"Integration Game {i+1}",
                descricao=f"Game {i+1} for integration testing",
                genero="Test",
                situacao=StatusCatalogo.DISPONIVEL.value
            )
            created_catalogo = container.catalogo_service.create(catalogo)
            catalogos.append(created_catalogo)
        
        # Verify all catalogos were created
        all_catalogos = container.catalogo_service.list_all()
        assert len(all_catalogos) >= 3
        
        # Filter by genre
        test_genre_catalogos = container.catalogo_service.get_by_genero("Test")
        assert len(test_genre_catalogos) >= 3
        
        # Filter by situation
        available_catalogos = container.catalogo_service.get_by_situacao(StatusCatalogo.DISPONIVEL.value)
        assert len(available_catalogos) >= 3
        
        # Inactivate some catalogos
        for catalogo in catalogos[:2]:
            container.catalogo_service.inactivate(catalogo.id)
        
        # Verify filtering still works
        available_after = container.catalogo_service.get_by_situacao(StatusCatalogo.DISPONIVEL.value)
        assert len(available_after) == len(available_catalogos) - 2

    def test_data_consistency(self):
        """Test data consistency across operations"""
        # Get initial counts
        initial_clientes = len(container.usuario_service.list_clientes())
        initial_funcionarios = len(container.usuario_service.list_funcionarios())
        initial_catalogos = len(container.catalogo_service.list_all())
        
        # Create entities
        cliente = Cliente(
            nome="Consistency Cliente",
            cpf="555.555.555-55",
            email="consistency@test.com",
            senha="password123"
        )
        
        funcionario = Funcionario(
            matricula="CONS001",
            nome="Consistency Funcionario",
            cpf="666.666.666-66",
            email="consistency.func@test.com",
            senha="password123"
        )
        
        catalogo = Catalogo(
            titulo="Consistency Game",
            descricao="Game for consistency testing",
            genero="Test"
        )
        
        created_cliente = container.usuario_service.create_cliente(cliente)
        created_funcionario = container.usuario_service.create_funcionario(funcionario)
        created_catalogo = container.catalogo_service.create(catalogo)
        
        # Verify counts increased
        assert len(container.usuario_service.list_clientes()) == initial_clientes + 1
        assert len(container.usuario_service.list_funcionarios()) == initial_funcionarios + 1
        assert len(container.catalogo_service.list_all()) == initial_catalogos + 1
        
        # Verify entities can be found by different methods
        found_by_id = container.usuario_service.get_by_id(created_cliente.id)
        found_by_cpf = container.usuario_service.get_by_cpf(created_cliente.cpf)
        assert found_by_id is not None
        assert found_by_cpf is not None
        assert found_by_id.id == found_by_cpf.id
        
        # Verify catalogo can be found by title
        found_by_title = container.catalogo_service.get_by_title(created_catalogo.titulo)
        assert found_by_title is not None
        assert found_by_title.id == created_catalogo.id

    def test_error_handling_integration(self):
        """Test error handling across the system"""
        # Test creating entities with invalid data
        invalid_cliente = Cliente(
            nome="",  # Empty name
            cpf="123.456.789-00",
            email="invalid@test.com",
            senha="password123"
        )
        
        with pytest.raises(ValueError, match="Nome é obrigatório"):
            container.usuario_service.create_cliente(invalid_cliente)
        
        # Test creating duplicate entities
        existing_clientes = container.usuario_service.list_clientes()
        if existing_clientes:
            existing_cliente = existing_clientes[0]
            
            duplicate_cliente = Cliente(
                nome="Duplicate",
                cpf=existing_cliente.cpf,  # Same CPF
                email="duplicate@test.com",
                senha="password123"
            )
            
            with pytest.raises(ValueError, match="Cliente com CPF .* já existe"):
                container.usuario_service.create_cliente(duplicate_cliente)
        
        # Test updating non-existent entities
        result = container.usuario_service.update_usuario(99999, {'nome': 'Updated'})
        assert result is None
        
        result = container.catalogo_service.update(99999, {'titulo': 'Updated'})
        assert result is None
        
        # Test deleting non-existent entities
        result = container.usuario_service.delete_usuario(99999)
        assert result is False
        
        result = container.catalogo_service.delete(99999)
        assert result is False

    def test_service_layer_isolation(self):
        """Test that service layers are properly isolated"""
        # Create entities through different services
        cliente = Cliente(
            nome="Isolation Cliente",
            cpf="777.777.777-77",
            email="isolation@test.com",
            senha="password123"
        )
        
        catalogo = Catalogo(
            titulo="Isolation Game",
            descricao="Game for isolation testing",
            genero="Test"
        )
        
        created_cliente = container.usuario_service.create_cliente(cliente)
        created_catalogo = container.catalogo_service.create(catalogo)
        
        # Verify each service only sees its own entities
        found_cliente = container.usuario_service.get_cliente_by_id(created_cliente.id)
        assert found_cliente is not None
        assert isinstance(found_cliente, Cliente)
        
        found_catalogo = container.catalogo_service.get_by_id(created_catalogo.id)
        assert found_catalogo is not None
        assert isinstance(found_catalogo, Catalogo)
        
        # Verify services don't interfere with each other
        all_clientes = container.usuario_service.list_clientes()
        all_catalogos = container.catalogo_service.list_all()
        
        assert all(isinstance(c, Cliente) for c in all_clientes)
        assert all(isinstance(c, Catalogo) for c in all_catalogos)
