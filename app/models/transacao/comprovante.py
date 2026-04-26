from datetime import datetime
from typing import Optional

from app.models.enums import TipoComprovante

class Comprovante:
    def __init__(
            self,
            id: int,
            tipo: Optional[str] = None,
            data_envio: Optional[datetime] = None,
            tipo_comprovante: Optional[str] = None,
            codigo_rastreio: Optional[str] = None):
        self.id = id
        self.tipo = tipo
        self.data_envio = data_envio or datetime.now()
        self.tipo_comprovante = tipo_comprovante or TipoComprovante.RESERVA.value
        self.codigo_rastreio = codigo_rastreio
