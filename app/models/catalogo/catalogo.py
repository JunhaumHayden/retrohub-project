from typing import Optional
from decimal import Decimal

from app.models import Exemplar
from app.models.enums import StatusCatalogo


class Catalogo:
    def __init__(
            self,
            id: int,
            titulo: str,
            situacao: Optional[str],
            descricao: Optional[str] = None,
            genero: Optional[str] = None,
            classificacao: Optional[str] = None,
            exemplares: Optional[list[Exemplar]] = None
    ):
        self.id = id or None
        self.titulo = titulo
        self.descricao = descricao
        self.situacao = situacao or StatusCatalogo.INDISPONIVEL.value
        self.genero = genero
        self.classificacao = classificacao
        self.exemplares = exemplares or []

    @property
    def estoque_disponivel(self) -> int:
        """Calcula o estoque disponível em memória."""
        return sum(1 for ex in self.exemplares if ex.situacao == 'DISPONIVEL')

    def add_exemplar(self, exemplar: Exemplar) -> None:
        # todo: implementar metodo para buscar e adicionar exemplares
        self.exemplares.append(exemplar)


    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, titulo='{self.titulo}')>"