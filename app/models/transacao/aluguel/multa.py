from datetime import date
from typing import Optional
from decimal import Decimal
from app.models.enums import StatusPagamento


class Multa:
    def __init__(
            self,
            id: int = None,
            dias_atraso: Optional[int] = None,
            valor: Optional[Decimal] = None,
            status: Optional[str] = None,
            data_calculo: Optional[date] = None
    ):
        self.id = id
        self.dias_atraso = dias_atraso
        self.valor = valor
        self.status = status or StatusPagamento.PENDENTE.value
        self.data_calculo = data_calculo
