from datetime import date
from typing import Optional

from app.models import Catalogo, Cliente
from app.models.enums import StatusReserva

class Reserva:
    def __init__(
            self,
            id: int,
            cliente: Cliente,
            catalogo: Catalogo,
            status: Optional[str],
            data_reserva: Optional[date],
            data_expiracao: Optional[date] = None
    ):
        self.id = id
        self.cliente = cliente
        self.catalogo = catalogo
        self.data_reserva = data_reserva or date.today()
        self.status = status or StatusReserva.ATIVA.value
        self.data_expiracao = data_expiracao
