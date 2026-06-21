from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.estoque.exemplar import Exemplar
from app.models.estoque.midia_fisica import MidiaFisica
from app.models.estoque.midia_digital import MidiaDigital
from app.models.catalogo.catalogo import Catalogo


class EstoqueRepositoryInterface(ABC):
    """
    Repository interface for Estoque operations
    Responsible for database operations related to inventory
    """

    @abstractmethod
    def get_exemplar_by_id(self, id: int) -> Optional[Exemplar]:
        pass

    @abstractmethod
    def get_exemplares_by_catalogo(self, catalogo_id: int) -> List[Exemplar]:
        pass

    @abstractmethod
    def get_midia_fisica_by_codigo_barras(self, codigo_barras: str) -> Optional[MidiaFisica]:
        pass

    @abstractmethod
    def get_midia_digital_by_chave(self, chave: str) -> Optional[MidiaDigital]:
        pass

    @abstractmethod
    def create_midia_fisica(self, midia: MidiaFisica) -> Optional[MidiaFisica]:
        pass

    @abstractmethod
    def create_midia_digital(self, midia: MidiaDigital) -> Optional[MidiaDigital]:
        pass

    @abstractmethod
    def update_midia_fisica(self, midia: MidiaFisica) -> Optional[MidiaFisica]:
        pass

    @abstractmethod
    def delete_exemplar(self, exemplar: Exemplar) -> bool:
        pass

    @abstractmethod
    def get_catalogo_by_id(self, id: int) -> Optional[Catalogo]:
        pass
