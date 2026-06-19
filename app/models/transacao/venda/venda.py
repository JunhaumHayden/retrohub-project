from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from sqlalchemy import Column, String, Date, Integer, ForeignKey

from app.models.transacao.transacao import Transacao
from app.models.enums import StatusVenda

class Venda(Transacao):
    __tablename__ = 'vendas'
    
    id = Column(Integer, ForeignKey('transacoes.id'), primary_key=True)
    status = Column(String(50), default=StatusVenda.PENDENTE.value)
    data_confirmacao = Column(Date)

    __mapper_args__ = {
        'polymorphic_identity': 'VENDA',
    }

    def __init__(
            self,
            id_transacao: int = None,
            status: Optional[str] = None,
            data_confirmacao: Optional[date] = None,
            **kwargs
    ):
        # Allow passing id_transacao for backwards compatibility
        if id_transacao is not None and "id" not in kwargs:
            kwargs["id"] = id_transacao
            
        super().__init__(
            tipo="VENDA",
            **kwargs
        )
        self.status = status or StatusVenda.PENDENTE.value
        self.data_confirmacao = data_confirmacao
