from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.transacao.transacao import Transacao

class Aluguel(Transacao):
    __tablename__ = 'aluguel'

    id_transacao: Mapped[int] = mapped_column(ForeignKey('transacao.id', ondelete='CASCADE'), primary_key=True)
    periodo: Mapped[Optional[int]] = mapped_column(Integer)
    data_devolucao: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[Optional[str]] = mapped_column(String, default='ATIVO')
    id_reserva: Mapped[Optional[int]] = mapped_column(ForeignKey('reserva.id'))
    data_inicio: Mapped[Optional[date]] = mapped_column(Date)
    data_prevista_devolucao: Mapped[Optional[date]] = mapped_column(Date)
    data_retirada: Mapped[Optional[datetime]] = mapped_column(DateTime)

    __mapper_args__ = {
        "polymorphic_identity": "aluguel",
    }
