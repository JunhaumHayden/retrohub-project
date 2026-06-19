from typing import Optional
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Enum
from app.database.base_model import Base
from app.models.enums import StatusSituacao
from app.models.base import ExemplarCollection

class Catalogo(Base):
    __tablename__ = 'catalogo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(255), nullable=False, unique=True)
    situacao = Column(Enum(StatusSituacao), default=StatusSituacao.DISPONIVEL)
    descricao = Column(String)
    classificacao = Column(String(50))
    genero = Column(String(100))
    
    # O relacionamento com exemplares será definido no modelo Exemplar
    # usando back_populates para manter a consistência.

    def __init__(
            self,
            titulo: str,
            situacao: Optional[StatusSituacao] = StatusSituacao.INDISPONIVEL.value,
            descricao: Optional[str] = None,
            classificacao: Optional[str] = None,
            genero: Optional[str] = None,
            exemplares: Optional[ExemplarCollection] = None,
            id: int = 0,
    ):
        # O super().__init__(id) foi removido pois a Base do SQLAlchemy não tem __init__
        self.id = id
        self.titulo = titulo
        self.situacao = situacao
        self.descricao = descricao
        self.classificacao = classificacao
        self.genero = genero
        self.exemplares = exemplares or ExemplarCollection()


    def add_exemplar(self, exemplar) -> None:
        """Add an exemplar to the catalogo"""
        self.exemplares.add_exemplar(exemplar)


    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, titulo='{self.titulo}')>"
