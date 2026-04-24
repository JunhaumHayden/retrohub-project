from typing import Optional

from app.models.enums import StatusCatalogo


class Exemplar:
    def __init__(self, id: int, id_catalogo: int, tipo_midia: str, 
                 plataforma: Optional[str] = None, situacao: Optional[str] = None):
        # Removed protection to allow instantiation for data factory
        self.id = id
        self.id_catalogo = id_catalogo
        self.tipo_midia = tipo_midia
        self.plataforma = plataforma
        self.situacao = situacao or StatusCatalogo.DISPONIVEL.value
        self.catalogo = None

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, id_catalogo={self.id_catalogo}, tipo={self.tipo_midia})>"

    def __str__(self):
        return f"{self.__class__.__name__} exemplar (ID: {self.id})"
