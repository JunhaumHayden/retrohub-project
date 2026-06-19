from abc import ABC, abstractmethod
from typing import List, Optional

from app.models import Aluguel, ItemTransacao, Multa, Comprovante, Exemplar

class AluguelRepositoryInterface(ABC):
    """
    Interface for Aluguel repository.
    """

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Aluguel]:
        pass

    @abstractmethod
    def get_items_by_transacao(self, transacao_id: int) -> List[ItemTransacao]:
        pass

    @abstractmethod
    def get_exemplar_by_id(self, exemplar_id: int) -> Optional[Exemplar]:
        pass
    
    @abstractmethod
    def find_exemplar_disponivel(self, id_catalogo: int, tipo_midia: str) -> Optional[Exemplar]:
        pass

    @abstractmethod
    def create_aluguel(self, aluguel: Aluguel) -> Aluguel:
        pass

    @abstractmethod
    def create_item_transacao(self, item_transacao: ItemTransacao) -> ItemTransacao:
        pass

    @abstractmethod
    def create_multa(self, multa: Multa) -> Multa:
        pass

    @abstractmethod
    def create_comprovante(self, comprovante: Comprovante) -> Comprovante:
        pass

    @abstractmethod
    def update(self, entity) -> Optional[any]:
        pass
