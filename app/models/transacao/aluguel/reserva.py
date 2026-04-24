from datetime import date
from typing import Optional

from app.models.enums import StatusReserva

class Reserva:
    def __init__(self, id: int, id_cliente: Optional[int] = None, id_jogo: Optional[int] = None, 
                 data_reserva: Optional[date] = None, status: Optional[str] = None, 
                 data_expiracao: Optional[date] = None):
        self.id = id
        self.id_cliente = id_cliente
        self.id_jogo = id_jogo
        self.data_reserva = data_reserva or date.today()
        self.status = status or StatusReserva.ATIVA.value
        self.data_expiracao = data_expiracao
