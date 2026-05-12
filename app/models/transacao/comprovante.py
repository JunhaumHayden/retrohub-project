from datetime import datetime
from typing import Optional

from app.models.enums import TipoComprovante

class Comprovante:
    def __init__(
            self,
            id: int,
            data: Optional[datetime] = None,
            tipo_comprovante: Optional[str] = None,
    ):
        self.id = id
        self.data_envio = data or datetime.now()
        self.tipo_comprovante = tipo_comprovante or TipoComprovante.RESERVA.value
