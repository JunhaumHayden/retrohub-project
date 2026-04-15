from datetime import date
from typing import Optional
from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.jogo.exemplar import Exemplar

class MidiaDigital(Exemplar):
    __tablename__ = 'midia_digital'

    id_exemplar: Mapped[int] = mapped_column(ForeignKey('exemplar.id', ondelete='CASCADE'), primary_key=True)
    chave_ativacao: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    data_expiracao: Mapped[Optional[date]] = mapped_column(Date)

    __mapper_args__ = {
        "polymorphic_identity": "DIGITAL",
    }
