"""
Tests for CatalogoService
"""

import pytest
from app.services.catalogo_service import CatalogoService
from app.repository.mock.catalogo_repository_mock import CatalogoRepositoryMock
from app.models.catalogo.catalogo import Catalogo
from app.models.enums import StatusCatalogo


class TestCatalogoService:
    """Test cases for CatalogoService"""

    @pytest.fixture
    def service(self):
        """Create a fresh service for each test"""
        repository = CatalogoRepositoryMock()
        return CatalogoService(repository)

    def test_list_all(self, service):
        """Test listing all catalog items"""
        catalogos = service.list_all()
        assert isinstance(catalogos, list)
        assert len(catalogos) > 0
        assert all(isinstance(c, Catalogo) for c in catalogos)

    def test_list_all_filtered_ativo(self, service):
        """Test listing catalog items filtered by active status"""
        # Test with ativo=True
        catalogos_ativos = service.list_all(ativo=True)
        assert isinstance(catalogos_ativos, list)
        assert all(c.situacao == StatusCatalogo.DISPONIVEL.value for c in catalogos_ativos)

    def test_list_all_filtered_inativo(self, service):
        """Test listing catalog items filtered by inactive status"""
        # Test with ativo=False
        catalogos_inativos = service.list_all(ativo=False)
        assert isinstance(catalogos_inativos, list)
        assert all(c.situacao == StatusCatalogo.INDISPONIVEL.value for c in catalogos_inativos)

    def test_get_by_id(self, service):
        """Test getting catalog item by ID"""
        catalogos = service.list_all()
        if catalogos:
            first_catalogo = catalogos[0]
            found_catalogo = service.get_by_id(first_catalogo.id)
            assert found_catalogo is not None
            assert isinstance(found_catalogo, Catalogo)
            assert found_catalogo.id == first_catalogo.id
            assert found_catalogo.titulo == first_catalogo.titulo

    def test_get_by_id_not_found(self, service):
        """Test getting non-existent catalog item by ID"""
        result = service.get_by_id(99999)
        assert result is None

    def test_get_by_title(self, service):
        """Test getting catalog item by title"""
        catalogos = service.list_all()
        if catalogos:
            first_catalogo = catalogos[0]
            found_catalogo = service.get_by_title(first_catalogo.titulo)
            assert found_catalogo is not None
            assert isinstance(found_catalogo, Catalogo)
            assert found_catalogo.titulo == first_catalogo.titulo

    def test_get_by_title_not_found(self, service):
        """Test getting non-existent catalog item by title"""
        result = service.get_by_title("Non-existent Game")
        assert result is None

    def test_create_catalogo_success(self, service):
        """Test successful catalog item creation"""
        initial_count = len(service.list_all())
        
        new_catalogo = Catalogo(
            titulo="New Test Game",
            descricao="A test game for testing",
            genero="Test",
            classificacao="Livre"
        )
        
        created_catalogo = service.create(new_catalogo)
        assert created_catalogo is not None
        assert created_catalogo.id is not None
        assert created_catalogo.titulo == "New Test Game"
        assert created_catalogo.situacao == StatusCatalogo.DISPONIVEL.value
        
        # Verify it was added
        final_count = len(service.list_all())
        assert final_count == initial_count + 1

    def test_create_catalogo_no_title(self, service):
        """Test creating catalog item without title"""
        new_catalogo = Catalogo(descricao="No title game")
        
        with pytest.raises(ValueError, match="Título é obrigatório"):
            service.create(new_catalogo)

    def test_create_catalogo_duplicate_title(self, service):
        """Test creating catalog item with duplicate title"""
        catalogos = service.list_all()
        if catalogos:
            existing_catalogo = catalogos[0]
            
            duplicate_catalogo = Catalogo(titulo=existing_catalogo.titulo)
            
            with pytest.raises(ValueError, match="Jogo com título .* já existe"):
                service.create(duplicate_catalogo)

    def test_update_catalogo_success(self, service):
        """Test successful catalog item update"""
        catalogos = service.list_all()
        if catalogos:
            first_catalogo = catalogos[0]
            original_title = first_catalogo.titulo
            
            update_data = {
                'titulo': 'Updated Title',
                'descricao': 'Updated description',
                'genero': 'Updated Genre'
            }
            
            updated_catalogo = service.update(first_catalogo.id, update_data)
            assert updated_catalogo is not None
            assert updated_catalogo.titulo == 'Updated Title'
            assert updated_catalogo.descricao == 'Updated description'
            assert updated_catalogo.genero == 'Updated Genre'

    def test_update_catalogo_not_found(self, service):
        """Test updating non-existent catalog item"""
        update_data = {'titulo': 'Updated Title'}
        
        result = service.update(99999, update_data)
        assert result is None

    def test_update_catalogo_duplicate_title(self, service):
        """Test updating catalog item with duplicate title"""
        catalogos = service.list_all()
        if len(catalogos) >= 2:
            first_catalogo = catalogos[0]
            second_catalogo = catalogos[1]
            
            update_data = {'titulo': second_catalogo.titulo}
            
            with pytest.raises(ValueError, match="Email .* já está em uso"):
                service.update(first_catalogo.id, update_data)

    def test_delete_catalogo_success(self, service):
        """Test successful catalog item deletion"""
        # First create a catalog item to delete
        new_catalogo = Catalogo(
            titulo="To Delete",
            descricao="Game to be deleted",
            genero="Test"
        )
        created_catalogo = service.create(new_catalogo)
        
        initial_count = len(service.list_all())
        
        # Delete it
        result = service.delete(created_catalogo.id)
        assert result is True
        
        # Verify it was deleted
        final_count = len(service.list_all())
        assert final_count == initial_count - 1
        
        # Verify it can't be found
        found_catalogo = service.get_by_id(created_catalogo.id)
        assert found_catalogo is None

    def test_delete_catalogo_not_found(self, service):
        """Test deleting non-existent catalog item"""
        result = service.delete(99999)
        assert result is False

    def test_get_by_genero(self, service):
        """Test getting catalog items by genre"""
        catalogos = service.list_all()
        if catalogos:
            first_catalogo = catalogos[0]
            if first_catalogo.genero:
                genre_catalogos = service.get_by_genero(first_catalogo.genero)
                assert isinstance(genre_catalogos, list)
                assert all(c.genero == first_catalogo.genero for c in genre_catalogos)

    def test_get_by_situacao(self, service):
        """Test getting catalog items by situation"""
        # Test by DISPONIVEL
        disponiveis = service.get_by_situacao(StatusCatalogo.DISPONIVEL.value)
        assert isinstance(disponiveis, list)
        assert all(c.situacao == StatusCatalogo.DISPONIVEL.value for c in disponiveis)

    def test_inactivate_catalogo(self, service):
        """Test inactivating a catalog item"""
        catalogos = service.list_all()
        if catalogos:
            first_catalogo = catalogos[0]
            
            inactivated_catalogo = service.inactivate(first_catalogo.id)
            assert inactivated_catalogo is not None
            assert inactivated_catalogo.situacao == StatusCatalogo.INDISPONIVEL.value

    def test_inactivate_not_found(self, service):
        """Test inactivating non-existent catalog item"""
        result = service.inactivate(99999)
        assert result is None

    def test_activate_catalogo(self, service):
        """Test activating a catalog item"""
        # First create and inactivate a catalog item
        new_catalogo = Catalogo(
            titulo="To Activate",
            descricao="Game to be activated",
            genero="Test",
            situacao=StatusCatalogo.INDISPONIVEL.value
        )
        created_catalogo = service.create(new_catalogo)
        
        # Inactivate it first
        service.inactivate(created_catalogo.id)
        
        # Now activate it
        activated_catalogo = service.activate(created_catalogo.id)
        assert activated_catalogo is not None
        assert activated_catalogo.situacao == StatusCatalogo.DISPONIVEL.value

    def test_activate_not_found(self, service):
        """Test activating non-existent catalog item"""
        result = service.activate(99999)
        assert result is None
