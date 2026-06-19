from datetime import date
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, Numeric, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database.base_model import Base

class Multa(Base):
    __tablename__ = 'multas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    dias_atraso = Column(Integer)
    valor = Column(Numeric(10, 2))
    status = Column(String(50))
    data_calculo = Column(Date)
    
    id_aluguel = Column(Integer, ForeignKey('alugueis.id'))
    aluguel = relationship("Aluguel", back_populates="multa_aplicada")

    def __init__(
            self,
            id: Optional[int] = None,
            dias_atraso: int = 0,
            valor: Decimal = Decimal("0"),
            status: Optional[str] = None,
            data_calculo: Optional[date] = None,
            aluguel=None
    ):
        self.id = id
        self.dias_atraso = dias_atraso
        self.valor = valor
        self.status = status or "PENDENTE"
        self.data_calculo = data_calculo or date.today()
        self.aluguel = aluguel

    def set_multa(
            self,
            dias_atraso: int,
            valor: Decimal,
            status: str,
            data_calculo: date
    ) -> bool:
        self.dias_atraso = dias_atraso
        self.valor = valor
        self.status = status
        self.data_calculo = data_calculo
        return True
