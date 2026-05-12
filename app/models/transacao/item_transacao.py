from typing import Optional
from decimal import Decimal

from app.models.estoque.exemplar import Exemplar

class ItemTransacao:
    def __init__(
            self,
            id: int,
            transacao: Optional["Transacao"] = None,
            exemplar: Optional[Exemplar] = None,
            valor_unitario: Optional[Decimal] = None
    ):
        self.id = id
        self.transacao = transacao
        self.exemplar = exemplar
        self.valor_item = valor_unitario
