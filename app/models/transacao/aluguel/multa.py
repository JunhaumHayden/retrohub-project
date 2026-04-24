from datetime import date
from typing import Optional
from decimal import Decimal

class Multa:
    def __init__(self, id: int, id_aluguel: Optional[int] = None, dias_atraso: Optional[int] = None, 
                 valor: Optional[Decimal] = None, status: Optional[str] = None, 
                 data_calculo: Optional[date] = None):
        self.id = id
        self.id_aluguel = id_aluguel
        self.dias_atraso = dias_atraso
        self.valor = valor
        self.status = status or 'PENDENTE'
        self.data_calculo = data_calculo
