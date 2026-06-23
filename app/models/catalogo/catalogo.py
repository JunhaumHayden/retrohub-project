from typing import Optional
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
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
    
    exemplares = relationship(
        "Exemplar", 
        back_populates="catalogo",
        collection_class=ExemplarCollection
    )

    def __init__(
            self,
            titulo: str,
            situacao: Optional[StatusSituacao] = StatusSituacao.DISPONIVEL,
            descricao: Optional[str] = None,
            classificacao: Optional[str] = None,
            genero: Optional[str] = None,
            id: int = None,
    ):
        self.id = id
        self.titulo = titulo
        self.situacao = situacao
        self.descricao = descricao
        self.classificacao = classificacao
        self.genero = genero
        # A coleção 'exemplares' é gerenciada pelo SQLAlchemy via 'relationship'
        # e não deve ser inicializada manualmente no construtor.

    def add_exemplar(self, exemplar) -> None:
        """Adiciona um exemplar à coleção."""
        self.exemplares.add_exemplar(exemplar)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, titulo='{self.titulo}')>"
