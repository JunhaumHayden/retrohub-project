from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from app.models.transacao.transacao import Transacao
from app.models.transacao.aluguel.multa import Multa
from app.models.transacao.aluguel.reserva import Reserva
from app.models.enums import StatusAluguel

if TYPE_CHECKING:
    from app.models.usuario.cliente import Cliente
    from app.models.usuario.funcionario import Funcionario
    from app.models.transacao.comprovante import Comprovante
    from app.models.transacao.item_transacao import ItemTransacao


class Aluguel(Transacao):
    def __init__(
            self,
            id_transacao: Optional[int] = None,
            valor_total: Optional[Decimal] = None,
            data_transacao: Optional[datetime] = None,
            status_pagamento: Optional[str] = None,
            cliente: Optional["Cliente"] = None,
            funcionario: Optional["Funcionario"] = None,
            comprovantes: Optional[list["Comprovante"]] = None,
            itens_transacao: Optional[list["ItemTransacao"]] = None,
            periodo: Optional[int] = None,
            data_devolucao: Optional[date] = None,
            status: Optional[str] = None,
            reserva: Optional[Reserva] = None,
            data_inicio: Optional[date] = None,
            data_prevista_devolucao: Optional[date] = None,
            data_retirada: Optional[datetime] = None,
            data_devolucao_real: Optional[datetime] = None,
            condicao_item: Optional[str] = None,
            funcionario_recebimento: Optional["Funcionario"] = None,
            multa_aplicada: Optional[Multa] = None,
            multa_paga: Optional[bool] = None,
            dias_atraso: Optional[int] = None,
            **kwargs,
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
            tipo="aluguel",
            **kwargs,
        )
        self.periodo = periodo
        self.data_devolucao = data_devolucao
        self.status = status or StatusAluguel.PENDENTE.value
        self.reserva = reserva
        self.data_inicio = data_inicio
        self.data_prevista_devolucao = data_prevista_devolucao
        self.data_retirada = data_retirada
        self.data_devolucao_real = data_devolucao_real
        self.condicao_item = condicao_item
        self.funcionario_recebimento = funcionario_recebimento
        self.multa_aplicada = multa_aplicada if multa_aplicada is not None else Multa()
        self.multa_paga = multa_paga if multa_paga is not None else False
        if dias_atraso is not None:
            self.multa_aplicada.dias_atraso = dias_atraso
