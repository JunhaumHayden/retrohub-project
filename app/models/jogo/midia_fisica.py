from typing import Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.jogo.jogo import Jogo

class MidiaFisica(Jogo):
    __tablename__ = 'midia_fisica'

    id_jogo: Mapped[int] = mapped_column(ForeignKey('jogo.id', ondelete='CASCADE'), primary_key=True)
    codigo_barras: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    estado_conservacao: Mapped[Optional[str]] = mapped_column(String(100))
    quantidade: Mapped[Optional[int]] = mapped_column(Integer, default=1)

    __mapper_args__ = {
        "polymorphic_identity": "midia_fisica",
    }
