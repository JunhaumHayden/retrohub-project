from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.catalogo.catalogo import Catalogo


class CatalogoRepositoryInterface(ABC):
    """
    Interface for Catalogo repository
    """

    @abstractmethod
    def list_all(self) -> List[Catalogo]:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Catalogo]:
        pass

    @abstractmethod
    def get_by_title(self, title: str) -> Optional[Catalogo]:
        pass

    @abstractmethod
    def create(self, catalogo: Catalogo) -> Optional[Catalogo]:
        pass

    @abstractmethod
    def update(self, catalogo: Catalogo) -> Optional[Catalogo]:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass

    @abstractmethod
    def get_by_genero(self, genero: str) -> List[Catalogo]:
        pass

    @abstractmethod
    def get_by_situacao(self, situacao: str) -> List[Catalogo]:
        pass
