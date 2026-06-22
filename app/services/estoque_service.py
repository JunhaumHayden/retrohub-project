from typing import Optional
from app.models import Exemplar
from app.repository.interface.catalogo_repository_interface import CatalogoRepositoryInterface

class EstoqueService:
    """
    Service layer for Estoque (Exemplar) operations.
    """

    def __init__(self, repository: CatalogoRepositoryInterface):
        # Reutiliza o catalogo_repository, pois ele já tem acesso ao DataSource
        # Em um cenário maior, poderia ter seu próprio repositório.
        self.repository = repository

    def create_exemplar(self, exemplar: Exemplar) -> Exemplar:
        """
        Cria e persiste uma nova instância de Exemplar.
        """
        # Acessa o data_source através do repositório injetado
        return self.repository.data_source.create(exemplar)
