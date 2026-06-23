from typing import List, Optional

from app.models.transacao.venda.venda import Venda
from app.models.transacao.item_transacao import ItemTransacao
from app.repository.interface.venda_repository_interface import VendaRepositoryInterface
from app.database.interfaces.data_source_interface import DataSourceInterface


class VendaRepositoryMock(VendaRepositoryInterface):
    """Mock implementation of VendaRepository for testing"""

    def __init__(self, data_source: DataSourceInterface):
        self.data_source = data_source

    def get_by_id(self, id: int) -> Optional[Venda]:
        return self.data_source.get_by_id(Venda, id)

    def get_by_cliente(self, cliente_id: int) -> List[Venda]:
        vendas = self.data_source.get_all(Venda)
        return [v for v in vendas if v.id_cliente == cliente_id]

    def create(self, venda: Venda) -> Optional[Venda]:
        return self.data_source.create(venda)

    def update(self, venda: Venda) -> Optional[Venda]:
        return self.data_source.update(venda)

    def create_item_transacao(self, item: ItemTransacao) -> Optional[ItemTransacao]:
        return self.data_source.create(item)

    def get_item_by_transacao(self, transacao_id: int) -> Optional[ItemTransacao]:
        items = self.data_source.get_all(ItemTransacao)
        return next((i for i in items if i.id_transacao == transacao_id), None)
