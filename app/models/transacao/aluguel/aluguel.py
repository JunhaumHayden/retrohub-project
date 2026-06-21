from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.models.transacao.transacao import Transacao
from app.models.transacao.aluguel.multa import Multa
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

if TYPE_CHECKING:
    from app.models.usuario.cliente import Cliente
    from app.models.usuario.funcionario import Funcionario
    from app.models.transacao.comprovante import Comprovante
    from app.models.transacao.item_transacao import ItemTransacao
    from app.models.transacao.aluguel.reserva import Reserva


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
        # Allow passing id_transacao for backwards compatibility
        if id_transacao is not None and "id" not in kwargs:
            kwargs["id"] = id_transacao

        super().__init__(
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
        if multa_aplicada:
            self.multa_aplicada = multa_aplicada
        self.multa_paga = multa_paga if multa_paga is not None else False
        self._dias_atraso = dias_atraso

        if dias_atraso is not None and self.multa_aplicada:
            try:
                self.multa_aplicada.dias_atraso = dias_atraso
            except Exception:
                pass

    def get_multa(self) -> Multa:
        """Diagrama de classes — getMulta()."""
        return self.multa_aplicada or Multa()

    def set_multa(self, multa: Multa) -> bool:
        """sd Devolucao — setMulta(m) no Aluguel."""
        self.multa_aplicada = multa
        return True

    def set_comprovante(self, tipo_comprovante: str) -> bool:
        """sd Devolucao / act finalizarAluguel — setComprovante + emitir."""
        from app.models.transacao.comprovante import Comprovante

        comprovante = Comprovante.emitir(
            tipo_comprovante=tipo_comprovante,
            transacao=self,
        )
        self.adicionar_comprovante(comprovante)
        return True

    @property
    def dias_atraso(self) -> Optional[int]:
        if getattr(self, 'multa_aplicada', None) is not None:
            val = getattr(self.multa_aplicada, 'dias_atraso', None)
            if val is not None:
                return val
        return getattr(self, '_dias_atraso', None)

    @dias_atraso.setter
    def dias_atraso(self, value: Optional[int]) -> None:
        self._dias_atraso = value
        if getattr(self, 'multa_aplicada', None) is not None:
            try:
                self.multa_aplicada.dias_atraso = value
            except Exception:
                pass
