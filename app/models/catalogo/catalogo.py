from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Text, Boolean, Numeric, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database_config import Base

class Catalogo(Base):
    __tablename__ = 'catalogo'

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text)
    plataforma: Mapped[Optional[str]] = mapped_column(String(100))
    ativo: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    genero: Mapped[Optional[str]] = mapped_column(String(100))
    classificacao: Mapped[Optional[str]] = mapped_column(String(50))
    valor_venda: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    valor_diaria_aluguel: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    estoque_disponivel: Mapped[Optional[int]] = mapped_column(Integer)
    exemplares: Mapped[list["Exemplar"]] = relationship(back_populates="catalogo", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('titulo', 'plataforma', name='uq_jogo_titulo_plataforma'),
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, titulo='{self.titulo}')>"