from datetime import date
from typing import Optional
from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.transacao.transacao import Transacao
from app.models.enums import StatusVenda


class Venda(Transacao):
    __tablename__ = 'venda'

    id_transacao: Mapped[int] = mapped_column(ForeignKey('transacao.id', ondelete='CASCADE'), primary_key=True)
    status: Mapped[Optional[str]] = mapped_column(String, default=StatusVenda.PENDENTE.value)
    data_confirmacao: Mapped[Optional[date]] = mapped_column(Date)

    __mapper_args__ = {
        "polymorphic_identity": "venda",
    }
