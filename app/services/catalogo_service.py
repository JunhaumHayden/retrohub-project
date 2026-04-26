from typing import List, Optional
from decimal import Decimal

from app.models.catalogo.catalogo import Catalogo
from app.repository.interface.catalogo_repository_interface import CatalogoRepositoryInterface
from app.models.enums import StatusCatalogo


class CatalogoService:
    """
    Service layer for Catalogo operations
    Handles business logic and validation
    """

    def __init__(self, repository: CatalogoRepositoryInterface):
        self.repository = repository

    def list_all(self, ativo: Optional[bool] = None) -> List[Catalogo]:
        """List all catalog items, optionally filtered by active status"""
        catalogos = self.repository.list_all()
        
        if ativo is not None:
            # Convert ativo boolean to situacao string
            situacao_filtro = StatusCatalogo.DISPONIVEL.value if ativo else StatusCatalogo.INDISPONIVEL.value
            catalogos = [c for c in catalogos if c.situacao == situacao_filtro]
        
        return catalogos

    def get_by_id(self, id: int) -> Optional[Catalogo]:
        """Get catalog item by ID"""
        return self.repository.get_by_id(id)

    def get_by_title(self, title: str) -> Optional[Catalogo]:
        """Get catalog item by title"""
        return self.repository.get_by_title(title)

    def create(self, catalogo: Catalogo) -> Optional[Catalogo]:
        """Create a new catalog item with validation"""
        # Validate required fields
        if not catalogo.titulo:
            raise ValueError("Título é obrigatório")
        
        # Check for duplicates by title
        existing = self.repository.get_by_title(catalogo.titulo)
        if existing:
            raise ValueError(f"Jogo com título '{catalogo.titulo}' já existe")
        
        # Set default situacao if not provided
        if not catalogo.situacao:
            catalogo.situacao = StatusCatalogo.DISPONIVEL.value
        
        return self.repository.create(catalogo)

    def update(self, id: int, catalogo_data: dict) -> Optional[Catalogo]:
        """Update an existing catalog item"""
        catalogo = self.repository.get_by_id(id)
        if not catalogo:
            return None
        
        # Update fields
        if 'titulo' in catalogo_data:
            new_title = catalogo_data['titulo']
            # Check if title is being changed and if new title already exists
            if new_title != catalogo.titulo:
                existing = self.repository.get_by_title(new_title)
                if existing and existing.id != id:
                    raise ValueError(f"Jogo com título '{new_title}' já existe")
            catalogo.titulo = new_title
        
        if 'descricao' in catalogo_data:
            catalogo.descricao = catalogo_data['descricao']
        
        if 'genero' in catalogo_data:
            catalogo.genero = catalogo_data['genero']
        
        if 'classificacao' in catalogo_data:
            catalogo.classificacao = catalogo_data['classificacao']
        
        if 'situacao' in catalogo_data:
            catalogo.situacao = catalogo_data['situacao']
        
        return self.repository.update(catalogo)

    def delete(self, id: int) -> bool:
        """Delete a catalog item"""
        catalogo = self.repository.get_by_id(id)
        if not catalogo:
            return False
        
        return self.repository.delete(id)

    def get_by_genero(self, genero: str) -> List[Catalogo]:
        """Get catalog items by genre"""
        return self.repository.get_by_genero(genero)

    def get_by_situacao(self, situacao: str) -> List[Catalogo]:
        """Get catalog items by situation"""
        return self.repository.get_by_situacao(situacao)

    def inactivate(self, id: int) -> Optional[Catalogo]:
        """Inactivate a catalog item"""
        catalogo = self.repository.get_by_id(id)
        if not catalogo:
            return None
        
        catalogo.situacao = StatusCatalogo.INDISPONIVEL.value
        return self.repository.update(catalogo)

    def activate(self, id: int) -> Optional[Catalogo]:
        """Activate a catalog item"""
        catalogo = self.repository.get_by_id(id)
        if not catalogo:
            return None
        
        catalogo.situacao = StatusCatalogo.DISPONIVEL.value
        return self.repository.update(catalogo)
