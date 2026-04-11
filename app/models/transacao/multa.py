from datetime import date
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database_config import Base

class Multa(Base):
    __tablename__ = 'multa'

    id: Mapped[int] = mapped_column(primary_key=True)
    id_aluguel: Mapped[Optional[int]] = mapped_column(ForeignKey('aluguel.id_transacao'))
    dias_atraso: Mapped[Optional[int]] = mapped_column(Integer)
    valor: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    status: Mapped[Optional[str]] = mapped_column(String, default='PENDENTE')
    data_calculo: Mapped[Optional[date]] = mapped_column(Date)
