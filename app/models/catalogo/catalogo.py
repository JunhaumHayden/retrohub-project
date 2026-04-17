from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Text, Boolean, Numeric, Integer, UniqueConstraint, func, case
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.database.database_config import Base
from app.models.estoque.exemplar import Exemplar


class Catalogo(Base):
    __tablename__ = 'catalogo'

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text)
    ativo: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    genero: Mapped[Optional[str]] = mapped_column(String(100))
    classificacao: Mapped[Optional[str]] = mapped_column(String(50))
    valor_venda: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    valor_diaria_aluguel: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    exemplares: Mapped[list["Exemplar"]] = relationship(back_populates="catalogo", cascade="all, delete-orphan")


    @hybrid_property
    def estoque_disponivel(self) -> int:
        """Calcula o estoque disponível em memória (para um objeto já carregado)."""
        return sum(1 for ex in self.exemplares if ex.situacao == 'DISPONIVEL')

    @estoque_disponivel.expression
    def estoque_disponivel(cls):
        """Gera a expressão SQL para ser usada em queries."""
        return func.coalesce(func.sum(case((Exemplar.situacao == 'DISPONIVEL', 1), else_=0)).filter(Exemplar.id_catalogo == cls.id), 0)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, titulo='{self.titulo}')>"