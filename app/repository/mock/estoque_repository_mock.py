from typing import List, Optional

from app.models.estoque.exemplar import Exemplar
from app.models.estoque.midia_fisica import MidiaFisica
from app.models.estoque.midia_digital import MidiaDigital
from app.models.catalogo.catalogo import Catalogo
from app.repository.interface.estoque_repository_interface import EstoqueRepositoryInterface
from app.database.interfaces.data_source_interface import DataSourceInterface


class EstoqueRepositoryMock(EstoqueRepositoryInterface):
    """Mock implementation of EstoqueRepository for testing"""

    def __init__(self, data_source: DataSourceInterface):
        self.data_source = data_source

    def get_exemplar_by_id(self, id: int) -> Optional[Exemplar]:
        # Try both physical and digital media
        midia_fisica = self.data_source.get_by_id(MidiaFisica, id)
        if midia_fisica:
            return midia_fisica
        return self.data_source.get_by_id(MidiaDigital, id)

    def get_exemplares_by_catalogo(self, catalogo_id: int) -> List[Exemplar]:
        # Get both physical and digital media for the catalog
        fisicas = self.data_source.get_all(MidiaFisica)
        digitais = self.data_source.get_all(MidiaDigital)
        
        exemplares = []
        for f in fisicas:
            if hasattr(f, 'id_catalogo') and f.id_catalogo == catalogo_id:
                exemplares.append(f)
        for d in digitais:
            if hasattr(d, 'id_catalogo') and d.id_catalogo == catalogo_id:
                exemplares.append(d)
        
        return exemplares

    def get_midia_fisica_by_codigo_barras(self, codigo_barras: str) -> Optional[MidiaFisica]:
        fisicas = self.data_source.get_all(MidiaFisica)
        return next((f for f in fisicas if f.codigo_barras == codigo_barras), None)

    def get_midia_digital_by_chave(self, chave: str) -> Optional[MidiaDigital]:
        digitais = self.data_source.get_all(MidiaDigital)
        return next((d for d in digitais if d.chave_ativacao == chave), None)

    def create_midia_fisica(self, midia: MidiaFisica) -> Optional[MidiaFisica]:
        return self.data_source.create(midia)

    def create_midia_digital(self, midia: MidiaDigital) -> Optional[MidiaDigital]:
        return self.data_source.create(midia)

    def update_midia_fisica(self, midia: MidiaFisica) -> Optional[MidiaFisica]:
        return self.data_source.update(midia)

    def delete_exemplar(self, exemplar: Exemplar) -> bool:
        return self.data_source.delete(type(exemplar), exemplar.id)

    def get_catalogo_by_id(self, id: int) -> Optional[Catalogo]:
        return self.data_source.get_by_id(Catalogo, id)
