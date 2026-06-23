from typing import List, Optional

from app.models import Aluguel, ItemTransacao, Multa, Comprovante, Exemplar
from app.repository.interface.aluguel_repository_interface import AluguelRepositoryInterface
from app.database.data_source.MockDataSource import MockDataSource
from app.database.interfaces.data_source_interface import DataSourceInterface


class AluguelRepositoryMock(AluguelRepositoryInterface):
    """
    Mock implementation of Aluguel repository using in-memory data source
    """

    def __init__(self, data_source: Optional[DataSourceInterface] = None):
        # accept any DataSourceInterface implementation (MockDataSource or other)
        self.data_source = data_source or MockDataSource()
        self.data_source.load_data()

    def get_by_id(self, id: int) -> Optional[Aluguel]:
        """Get aluguel by ID"""
        return self.data_source.get_by_id(Aluguel, id)

    def get_items_by_transacao(self, transacao_id: int) -> List[ItemTransacao]:
        """Get items by transaction ID"""
        items = self.data_source.get_all(ItemTransacao)
        return [item for item in items if item.transacao_id == transacao_id]

    def get_exemplar_by_id(self, exemplar_id: int) -> Optional[Exemplar]:
        """Get exemplar by ID"""
        return self.data_source.get_by_id(Exemplar, exemplar_id)
    
    def find_exemplar_disponivel(self, id_catalogo: int, tipo_midia: str) -> Optional[Exemplar]:
        """Find available exemplar by catalog ID and media type"""
        exemplares = self.data_source.get_all(Exemplar)
        for exemplar in exemplares:
            if (exemplar.id_catalogo == id_catalogo and 
                exemplar.tipo_midia == tipo_midia and 
                exemplar.situacao == 'disponivel'):
                return exemplar
        return None

    def create_aluguel(self, aluguel: Aluguel) -> Aluguel:
        """Create a new aluguel"""
        return self.data_source.create(aluguel)

    def create_item_transacao(self, item_transacao: ItemTransacao) -> ItemTransacao:
        """Create a new item transacao"""
        return self.data_source.create(item_transacao)

    def create_multa(self, multa: Multa) -> Multa:
        """Create a new multa"""
        return self.data_source.create(multa)

    def create_comprovante(self, comprovante: Comprovante) -> Comprovante:
        """Create a new comprovante"""
        return self.data_source.create(comprovante)

    def update(self, entity) -> Optional[any]:
        """Update an entity"""
        return self.data_source.update(entity)
