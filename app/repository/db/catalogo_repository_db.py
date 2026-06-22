from typing import List, Optional

from app.models import Exemplar
from app.models.catalogo.catalogo import Catalogo
from app.repository.interface.catalogo_repository_interface import CatalogoRepositoryInterface
from app.database.interfaces.data_source_interface import DataSourceInterface

class CatalogoRepositoryDB(CatalogoRepositoryInterface):
    """
    Implementação concreta do repositório de Catálogo para banco de dados real (via DataSourceInterface).
    """

    def __init__(self, data_source: DataSourceInterface):
        self.data_source = data_source

    def list_all(self) -> List[Catalogo]:
        return self.data_source.get_all(Catalogo)

    def get_by_id(self, id: int) -> Optional[Catalogo]:
        return self.data_source.get_by_id(Catalogo, id)

    def get_by_title(self, title: str) -> Optional[Catalogo]:
        return self.data_source.get_by_field(Catalogo, 'titulo', title)

    def create(self, catalogo: Catalogo) -> Optional[Catalogo]:
        return self.data_source.create(catalogo)

    def update(self, catalogo: Catalogo) -> Optional[Catalogo]:
        return self.data_source.update(catalogo)

    def delete(self, id: int) -> bool:
        return self.data_source.delete(Catalogo, id)

    def get_by_genero(self, genero: str) -> List[Catalogo]:
        return [c for c in self.data_source.get_all(Catalogo) if c.genero == genero]

    def get_by_situacao(self, situacao: str) -> List[Catalogo]:
        return [c for c in self.data_source.get_all(Catalogo) if c.situacao == situacao]

    def add_exemplar(self, exemplar: Exemplar) -> Optional[Exemplar]:
        return self.data_source.add_exemplar(exemplar)
