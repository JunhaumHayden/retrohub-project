from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Integer, Date, DateTime, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, reconstructor

from app.models.transacao.transacao import Transacao
from app.models.enums import StatusAluguel
from app.models.transacao.aluguel.aluguel_states import (
    EstadoSolicitado,
    EstadoProcessandoPagamento,
    EstadoPagamentoConfirmado,
    EstadoAtivo,
    EstadoAtrasado,
    EstadoFinalizado,
    EstadoCancelado,
)

class Aluguel(Transacao):
    __tablename__ = 'aluguel'

    id_transacao: Mapped[int] = mapped_column(ForeignKey('transacao.id', ondelete='CASCADE'), primary_key=True)
    periodo: Mapped[Optional[int]] = mapped_column(Integer)
    data_devolucao: Mapped[Optional[date]] = mapped_column(Date)
    id_reserva: Mapped[Optional[int]] = mapped_column(ForeignKey('reserva.id'))
    data_inicio: Mapped[Optional[date]] = mapped_column(Date)
    data_prevista_devolucao: Mapped[Optional[date]] = mapped_column(Date)
    data_retirada: Mapped[Optional[datetime]] = mapped_column(DateTime)
    data_devolucao_real: Mapped[Optional[datetime]] = mapped_column(DateTime)
    condicao_item: Mapped[Optional[str]] = mapped_column(String(50))
    id_funcionario_recebimento: Mapped[Optional[int]] = mapped_column(ForeignKey('funcionario.id_usuario'))
    multa_aplicada: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    multa_paga: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    dias_atraso: Mapped[Optional[int]] = mapped_column(Integer)

    def __init__(self, *args, status: Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.status = status if status is not None else StatusAluguel.SOLICITADO.value
        self._set_state(self.status)

    @reconstructor
    def init_on_load(self):
        self._set_state(self.status)

    def _set_state(self, status: Optional[str] = None):
        status = status or self.status
        if status == StatusAluguel.SOLICITADO.value:
            self.state = EstadoSolicitado(self)
        elif status == StatusAluguel.APROVADO.value:
            self.state = EstadoPagamentoConfirmado(self)
        elif status == StatusAluguel.ATIVO.value:
            self.state = EstadoAtivo(self)
        elif status == StatusAluguel.PENDENTE.value:
            self.state = EstadoSolicitado(self)
        elif status == StatusAluguel.ATRASADO.value:
            self.state = EstadoAtrasado(self)
        elif status == StatusAluguel.FINALIZADO.value:
            self.state = EstadoFinalizado(self)
        elif status == StatusAluguel.CANCELADO.value:
            self.state = EstadoCancelado(self)
        else:
            raise ValueError(f"Status de aluguel desconhecido: {status}")
        self.status = status

    def processar_pagamento(self, sucesso: bool):
        self.state.processar_pagamento(sucesso)
        self._set_state(self.status)

    def registrar_retirada(self):
        self.state.registrar_retirada()
        self._set_state(self.status)

    def finalizar_aluguel(self):
        self.state.finalizar_aluguel()
        self._set_state(self.status)

    def renovar_aluguel(self, dias_adicionais: int):
        self.state.renovar_aluguel(dias_adicionais)
        self._set_state(self.status)

    def cancelar_aluguel(self):
        self.state.cancelar_aluguel()
        self._set_state(self.status)

    __mapper_args__ = {
        "polymorphic_identity": "aluguel",
    }
