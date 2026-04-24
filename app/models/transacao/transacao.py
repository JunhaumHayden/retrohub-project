from datetime import datetime
from typing import Optional
from decimal import Decimal

from app.models.enums import StatusTransacao
from app.models.enums import StatusPagamento

class Transacao:
    def __init__(self, id: int = None, valor_total: Optional[Decimal] = None,
                 pagamento: Optional[str] = None, status: Optional[str] = None, 
                 id_cliente: Optional[int] = None, id_funcionario: Optional[int] = None, 
                 tipo: str = "transacao", data_transacao: Optional[datetime] = None):
        # Removed protection to allow instantiation for data factory
        self.id = id
        self.data_transacao = data_transacao or datetime.utcnow()
        self.valor_total = valor_total
        self.pagamento = pagamento or StatusPagamento.PENDENTE.value
        self.status = status or StatusTransacao.PENDENTE.value
        self.id_cliente = id_cliente
        self.id_funcionario = id_funcionario
        self.tipo = tipo

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

    def __str__(self):
        return f"{self.__class__.__name__} id={self.id}, status={self.status}, valor={self.valor_total}, cliente={self.id_cliente}, funcionario={self.id_funcionario}"
