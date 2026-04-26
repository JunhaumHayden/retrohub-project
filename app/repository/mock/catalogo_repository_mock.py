from typing import List, Optional

from app.models.catalogo.catalogo import Catalogo
from app.repository.interface.catalogo_repository_interface import CatalogoRepositoryInterface
from app.database.mock_data_source import MockDataSource


class CatalogoRepositoryMock(CatalogoRepositoryInterface):
    """
    Mock implementation of Catalogo repository using in-memory data source
    """

    def __init__(self, data_source: Optional[MockDataSource] = None):
        self.data_source = data_source or MockDataSource()
        self.data_source.load_data()

    def list_all(self) -> List[Catalogo]:
        """List all catalog items"""
        return self.data_source.get_all(Catalogo)

    def get_by_id(self, id: int) -> Optional[Catalogo]:
        """Get catalog item by ID"""
        return self.data_source.get_by_id(Catalogo, id)

    def get_by_title(self, title: str) -> Optional[Catalogo]:
        """Get catalog item by title"""
        catalogos = self.list_all()
        for catalogo in catalogos:
            if catalogo.titulo.lower() == title.lower():
                return catalogo
        return None

    def create(self, catalogo: Catalogo) -> Optional[Catalogo]:
        """Create a new catalog item"""
        return self.data_source.create(catalogo)

    def update(self, catalogo: Catalogo) -> Optional[Catalogo]:
        """Update an existing catalog item"""
        return self.data_source.update(catalogo)

    def delete(self, id: int) -> bool:
        """Delete a catalog item"""
        return self.data_source.delete(Catalogo, id)

    def get_by_genero(self, genero: str) -> List[Catalogo]:
        """Get catalog items by genre"""
        catalogos = self.list_all()
        return [c for c in catalogos if c.genero and c.genero.lower() == genero.lower()]

    def get_by_situacao(self, situacao: str) -> List[Catalogo]:
        """Get catalog items by situation"""
        catalogos = self.list_all()
        return [c for c in catalogos if c.situacao and c.situacao.lower() == situacao.lower()]
