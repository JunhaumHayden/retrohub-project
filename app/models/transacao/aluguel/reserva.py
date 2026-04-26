from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional

from app.models.enums import StatusReserva

if TYPE_CHECKING:
    from app.models.catalogo.catalogo import Catalogo
    from app.models.usuario.cliente import Cliente


class Reserva:
    def __init__(
            self,
            id: int,
            cliente: Optional["Cliente"] = None,
            catalogo: Optional["Catalogo"] = None,
            status: Optional[str] = None,
            data_reserva: Optional[date] = None,
            data_expiracao: Optional[date] = None,
    ):
        self.id = id
        self.cliente = cliente
        self.catalogo = catalogo
        self.data_reserva = data_reserva or date.today()
        self.status = status or StatusReserva.ATIVA.value
        self.data_expiracao = data_expiracao
