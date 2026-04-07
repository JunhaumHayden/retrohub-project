from datetime import date
from typing import Optional
from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.jogo.jogo import Jogo

class MidiaDigital(Jogo):
    __tablename__ = 'midia_digital'

    id_jogo: Mapped[int] = mapped_column(ForeignKey('jogo.id', ondelete='CASCADE'), primary_key=True)
    chave_ativacao: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    data_expiracao: Mapped[Optional[date]] = mapped_column(Date)

    __mapper_args__ = {
        "polymorphic_identity": "midia_digital",
    }
