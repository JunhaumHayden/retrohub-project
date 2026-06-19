from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.models.transacao.transacao import Transacao
from app.models.transacao.aluguel.multa import Multa
from app.models.enums import StatusAluguel

if TYPE_CHECKING:
    from app.models.usuario.cliente import Cliente
    from app.models.usuario.funcionario import Funcionario
    from app.models.transacao.comprovante import Comprovante
    from app.models.transacao.item_transacao import ItemTransacao
    from app.models.transacao.aluguel.reserva import Reserva


class Aluguel(Transacao):
    __tablename__ = 'alugueis'

    id = Column(Integer, ForeignKey('transacoes.id'), primary_key=True)
    periodo = Column(Integer)
    data_devolucao = Column(Date)
    status = Column(String(50), default=StatusAluguel.PENDENTE.value)
    data_inicio = Column(Date)
    data_prevista_devolucao = Column(Date)
    data_retirada = Column(DateTime)
    data_devolucao_real = Column(DateTime)
    condicao_item = Column(String(255))
    id_funcionario_recebimento = Column(Integer, ForeignKey('funcionarios.id'))
    multa_paga = Column(Boolean, default=False)
    
    # id_reserva = Column(Integer, ForeignKey('reservas.id'), nullable=True) # Assuming Reserva model exists
    
    funcionario_recebimento = relationship("Funcionario", foreign_keys=[id_funcionario_recebimento])
    multa_aplicada = relationship("Multa", uselist=False, back_populates="aluguel")

    __mapper_args__ = {
        'polymorphic_identity': 'aluguel',
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
