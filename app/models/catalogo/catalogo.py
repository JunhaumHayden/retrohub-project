from typing import Optional
from decimal import Decimal

from app.models.enums import StatusCatalogo
from app.models.base import BaseModel, ExemplarCollection


class Catalogo(BaseModel):
    def __init__(
            self,
            id: int,
            titulo: str,
            situacao: Optional[str],
            descricao: Optional[str] = None,
            genero: Optional[str] = None,
            classificacao: Optional[str] = None,
            exemplares: Optional[ExemplarCollection] = None
    ):
        super().__init__(id)
        self.titulo = titulo
        self.descricao = descricao
        self.situacao = situacao or StatusCatalogo.INDISPONIVEL.value
        self.genero = genero
        self.classificacao = classificacao
        self.exemplares = exemplares or ExemplarCollection()

    @property
    def estoque_disponivel(self) -> int:
        """Calcula o estoque disponível em memória."""
        return self.exemplares.get_available_count()

    def add_exemplar(self, exemplar) -> None:
        """Add an exemplar to the catalogo"""
        self.exemplares.add_exemplar(exemplar)


    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, titulo='{self.titulo}')>"