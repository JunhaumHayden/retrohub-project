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

    def set_multa(
            self,
            dias_atraso: Optional[int] = None,
            valor: Optional[Decimal] = None,
            status: Optional[str] = None,
            data_calculo: Optional[date] = None,
    ) -> bool:
        """sd Devolucao — setMulta(dados) na instância Multa."""
        if dias_atraso is not None:
            self.dias_atraso = dias_atraso
        if valor is not None:
            self.valor = valor
        if status is not None:
            self.status = status
        if data_calculo is not None:
            self.data_calculo = data_calculo
        return True
