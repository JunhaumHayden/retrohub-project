from datetime import date
from typing import Optional

from app.models.transacao.transacao import Transacao
from app.models.enums import StatusVenda


class Venda(Transacao):
    def __init__(self, id_transacao: int, status: Optional[str] = None, 
                 data_confirmacao: Optional[date] = None, **kwargs):
        super().__init__(id=id_transacao, tipo="venda", **kwargs)
        self.status = status or StatusVenda.PENDENTE.value
        self.data_confirmacao = data_confirmacao
