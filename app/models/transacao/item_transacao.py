from typing import Optional
from decimal import Decimal

class ItemTransacao:
    def __init__(self, id: int, id_transacao: Optional[int] = None, 
                 id_exemplar: Optional[int] = None, valor_unitario: Optional[Decimal] = None):
        self.id = id
        self.id_transacao = id_transacao
        self.id_exemplar = id_exemplar
        self.valor_unitario = valor_unitario
