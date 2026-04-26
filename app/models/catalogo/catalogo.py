from typing import Optional
from decimal import Decimal

from app.models.enums import StatusCatalogo
from app.models.base import BaseModel, ExemplarCollection


class Catalogo(BaseModel):
    def __init__(
            self,
            id: Optional[int] = None,
            titulo: Optional[str] = None,
            situacao: Optional[str] = None,
            descricao: Optional[str] = None,
            genero: Optional[str] = None,
            classificacao: Optional[str] = None,
            exemplares: Optional[ExemplarCollection] = None,
            **kwargs,
    ):
        super().__init__(id)
        self.titulo = titulo
        self.descricao = descricao
        self.situacao = situacao or StatusCatalogo.DISPONIVEL.value
        self.genero = genero
        self.classificacao = classificacao
        self.exemplares = exemplares or ExemplarCollection()
        # Permite que a coleção mantenha a navegação reversa exemplar -> catálogo
        # quando exemplares são anexados após a criação do catálogo.
        self.exemplares._owner_catalogo = self

    @property
    def estoque_disponivel(self) -> int:
        """Calcula o estoque disponível em memória."""
        return self.exemplares.get_available_count()

    def add_exemplar(self, exemplar) -> None:
        """Add an exemplar to the catalogo"""
        self.exemplares.add_exemplar(exemplar)


    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, titulo='{self.titulo}')>"