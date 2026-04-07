from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Text, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database_config import Base

class Jogo(Base):
    __tablename__ = 'jogo'

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text)
    plataforma: Mapped[Optional[str]] = mapped_column(String(100))
    ativo: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    genero: Mapped[Optional[str]] = mapped_column(String(100))
    classificacao: Mapped[Optional[str]] = mapped_column(String(50))
    valor_venda: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    valor_diaria_aluguel: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))

    def __repr__(self) -> str:
        return f"<Jogo(id={self.id}, titulo='{self.titulo}')>"
