from datetime import date
from typing import Optional
from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database_config import Base

class Usuario(Base):
    __tablename__ = 'usuario'

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    cpf: Mapped[str] = mapped_column(String(14), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    senha: Mapped[str] = mapped_column(String(255), nullable=False)
    data_cadastro: Mapped[Optional[date]] = mapped_column(Date, default=date.today)
    data_nascimento: Mapped[Optional[date]] = mapped_column(Date)

    def __repr__(self) -> str:
        return f"<Usuario(id={self.id}, nome='{self.nome}')>"
