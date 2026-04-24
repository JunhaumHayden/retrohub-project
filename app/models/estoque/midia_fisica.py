from typing import Optional

from app.models.estoque.exemplar import Exemplar

class MidiaFisica(Exemplar):
    def __init__(self, id_exemplar: int, codigo_barras: str, estado_conservacao: Optional[str] = None, **kwargs):
        super().__init__(id=id_exemplar, tipo_midia="FISICA", **kwargs)
        self.id_exemplar = id_exemplar
        self.codigo_barras = codigo_barras
        self.estado_conservacao = estado_conservacao
