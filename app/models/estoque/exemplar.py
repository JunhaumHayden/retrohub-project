from abc import ABC
from typing import Optional

from app.models import Catalogo

class Exemplar(ABC):
    def __init__(
            self,
            id: int,
            catalogo: Catalogo,
            tipo_midia: str
    ):
        if type(self) is Exemplar:
            raise TypeError("Erro: Operação Não permitida")

        self.id = id
        self.catalogo = catalogo
        self.tipo_midia = tipo_midia
        #todo: implementar a insercao de um exemplar na lista do Catalogo
        self.catalogo.add_exemplar(self)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, id_catalogo={self.catalogo.id}, tipo={self.tipo_midia})>"

    def __str__(self):
        return f"{self.__class__.__name__} exemplar (ID: {self.id})"
