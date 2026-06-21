from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.transacao.venda.venda import Venda
from app.models.transacao.item_transacao import ItemTransacao


class VendaRepositoryInterface(ABC):
    """
    Repository interface for Venda operations
    Responsible for database operations related to sales
    """

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Venda]:
        pass

    @abstractmethod
    def get_by_cliente(self, cliente_id: int) -> List[Venda]:
        pass

    @abstractmethod
    def create(self, venda: Venda) -> Optional[Venda]:
        pass

    @abstractmethod
    def update(self, venda: Venda) -> Optional[Venda]:
        pass

    @abstractmethod
    def create_item_transacao(self, item: ItemTransacao) -> Optional[ItemTransacao]:
        pass

    @abstractmethod
    def get_item_by_transacao(self, transacao_id: int) -> Optional[ItemTransacao]:
        pass
