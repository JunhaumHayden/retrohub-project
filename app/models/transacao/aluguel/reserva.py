from __future__ import annotations
from datetime import date
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database.base_model import Base
from app.models.enums import StatusReserva

if TYPE_CHECKING:
    from app.models.usuario.cliente import Cliente
    from app.models.catalogo.catalogo import Catalogo

class Reserva(Base):
    __tablename__ = 'reservas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_cliente = Column(Integer, ForeignKey('clientes.id'))
    id_catalogo = Column(Integer, ForeignKey('catalogo.id'))
    data_reserva = Column(Date, default=date.today)
    status = Column(String(50), default=StatusReserva.ATIVA.value)
    data_expiracao = Column(Date)

    cliente = relationship("Cliente")
    catalogo = relationship("Catalogo")

    def __init__(
        self,
        id: int = None,
        cliente: Optional[Cliente] = None,
        catalogo: Optional[Catalogo] = None,
        data_reserva: Optional[date] = None,
        status: Optional[str] = None,
        data_expiracao: Optional[date] = None,
    ):
        self.id = id
        self.cliente = cliente
        self.catalogo = catalogo
        self.data_reserva = data_reserva or date.today()
        self.status = status or StatusReserva.ATIVA.value
        self.data_expiracao = data_expiracao
