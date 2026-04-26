from abc import ABC
from typing import Optional

from app.models.base import BaseModel, CatalogoReference


class Exemplar(BaseModel):
    def __init__(
            self,
            id: int,
            catalogo,
            tipo_midia: str,
            situacao: str = "DISPONIVEL"
    ):
        super().__init__(id)
        if type(self) is Exemplar:
            raise TypeError("Erro: Operação Não permitida")

        # Use CatalogoReference to avoid circular imports
        if isinstance(catalogo, CatalogoReference):
            self.catalogo_ref = catalogo
        else:
            # If a Catalogo object is passed, create a reference
            self.catalogo_ref = CatalogoReference(catalogo.id if hasattr(catalogo, 'id') else catalogo)
            self.catalogo_ref.set_catalogo(catalogo)
        
        self.tipo_midia = tipo_midia
        self.situacao = situacao
        
        # Add exemplar to catalogo if we have access to it
        catalogo_obj = self.catalogo_ref.get_catalogo()
        if catalogo_obj is not None:
            catalogo_obj.add_exemplar(self)
    
    @property
    def catalogo(self):
        """Get the catalogo object"""
        return self.catalogo_ref.get_catalogo()
    
    @property
    def id_catalogo(self):
        """Get the catalogo ID"""
        return self.catalogo_ref.id

    def __repr__(self):
        catalogo_id = self.catalogo_ref.id if self.catalogo_ref else "unknown"
        return f"<{self.__class__.__name__}(id={self.id}, id_catalogo={catalogo_id}, tipo={self.tipo_midia})>"

    def __str__(self):
        return f"{self.__class__.__name__} exemplar (ID: {self.id})"
