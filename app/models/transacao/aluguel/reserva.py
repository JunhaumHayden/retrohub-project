from datetime import date
from typing import Optional
from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database_config import Base
from app.models.enums import StatusReserva

class Reserva(Base):
    __tablename__ = 'reserva'

    id: Mapped[int] = mapped_column(primary_key=True)
    id_cliente: Mapped[Optional[int]] = mapped_column(ForeignKey('cliente.id_usuario'))
    id_jogo: Mapped[Optional[int]] = mapped_column(ForeignKey('jogo.id'))
    data_reserva: Mapped[Optional[date]] = mapped_column(Date, default=date.today)
    status: Mapped[Optional[str]] = mapped_column(String, default=StatusReserva.ATIVA.value)
    data_expiracao: Mapped[Optional[date]] = mapped_column(Date)
