from typing import Any, List, Optional

from app.database.mock_data_source import MockDataSource
from app.database.interfaces.data_source_interface import DataSourceInterface
from app.models import Aluguel, ItemTransacao, Exemplar, Catalogo, Multa, Comprovante


class AluguelRepositoryMock:
    """Mock repository for Aluguel operations using MockDataSource in-memory lists."""

    def __init__(self, data_source: Optional[DataSourceInterface] = None):
        # Accept any DataSourceInterface implementation
        self.data_source = data_source or MockDataSource()
        # Ensure data is loaded
        if hasattr(self.data_source, 'load_data'):
            self.data_source.load_data()

    def get_by_id(self, id: int) -> Optional[Aluguel]:
        return self.data_source.get_by_id(Aluguel, id)

    def update(self, entity: Any) -> Optional[Any]:
        return self.data_source.update(entity)

    def get_items_by_transacao(self, transacao_id: int) -> List[ItemTransacao]:
        items = self.data_source.get_all(ItemTransacao)
        return [i for i in items if i.id_transacao == transacao_id]

    def get_exemplar_by_id(self, exemplar_id: int) -> Optional[Exemplar]:
        return self.data_source.get_by_id(Exemplar, exemplar_id)

    def get_catalogo_by_id(self, catalogo_id: int) -> Optional[Catalogo]:
        return self.data_source.get_by_id(Catalogo, catalogo_id)

    def create_multa(self, multa: Multa) -> Multa:
        return self.data_source.create(multa)

    def create_comprovante(self, comprovante: Comprovante) -> Comprovante:
        return self.data_source.create(comprovante)
