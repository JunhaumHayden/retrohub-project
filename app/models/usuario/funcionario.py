from datetime import date
from typing import Optional
from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.usuario.usuario import Usuario

class Funcionario(Usuario):
    __tablename__ = 'funcionario'

    id_usuario: Mapped[int] = mapped_column(ForeignKey('usuario.id', ondelete='CASCADE'), primary_key=True)
    matricula: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    cargo: Mapped[Optional[str]] = mapped_column(String(100))
    setor: Mapped[Optional[str]] = mapped_column(String(100))
    data_admissao: Mapped[Optional[date]] = mapped_column(Date)

    __mapper_args__ = {
        "polymorphic_identity": "funcionario",
    }
