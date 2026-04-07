from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.transacao.transacao import Transacao

class Venda(Transacao):
    __tablename__ = 'venda'

    id_transacao: Mapped[int] = mapped_column(ForeignKey('transacao.id', ondelete='CASCADE'), primary_key=True)
    status: Mapped[Optional[str]] = mapped_column(String, default='FINALIZADA')

    __mapper_args__ = {
        "polymorphic_identity": "venda",
    }
