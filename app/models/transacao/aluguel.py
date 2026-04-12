from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Integer, Date, DateTime, Numeric, Boolean, ForeignKey
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
    data_devolucao_real: Mapped[Optional[datetime]] = mapped_column(DateTime)
    condicao_item: Mapped[Optional[str]] = mapped_column(String(50))
    id_funcionario_recebimento: Mapped[Optional[int]] = mapped_column(ForeignKey('funcionario.id_usuario'))
    multa_aplicada: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    multa_paga: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    dias_atraso: Mapped[Optional[int]] = mapped_column(Integer)

    __mapper_args__ = {
        "polymorphic_identity": "aluguel",
    }
