from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from app.models import Cliente, Funcionario, Comprovante, ItemTransacao
from app.models.transacao.transacao import Transacao
from app.models.enums import StatusVenda


class Venda(Transacao):
    def __init__(
            self,
            id_transacao: int,
            status: Optional[str] = None,
            data_confirmacao: Optional[date] = None,
            valor_total: Optional[Decimal] = None,
            data_transacao: Optional[datetime] = None,
            status_pagamento: Optional[str] = None,
            cliente: Optional[Cliente] = None,
            funcionario: Optional[Funcionario] = None,
            comprovantes: Optional[list[Comprovante]] = None,
            itens_transacao: Optional[list[ItemTransacao]] = None,
            **kwargs
    ):
        super().__init__(
            id=id_transacao,
            valor_total=valor_total,
            data_transacao=data_transacao,
            status_pagamento=status_pagamento,
            cliente=cliente,
            funcionario=funcionario,
            comprovantes=comprovantes,
            itens_transacao=itens_transacao,
            tipo="venda",
            **kwargs
        )
        self.status = status or StatusVenda.PENDENTE.value
        self.data_confirmacao = data_confirmacao
