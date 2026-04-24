from datetime import date, datetime
from typing import Optional
from decimal import Decimal

from app.models.transacao.transacao import Transacao
from app.models.enums import StatusAluguel

class Aluguel(Transacao):
    def __init__(self, id_transacao: int, periodo: Optional[int] = None, 
                 data_devolucao: Optional[date] = None, status: Optional[str] = None, 
                 id_reserva: Optional[int] = None, data_inicio: Optional[date] = None, 
                 data_prevista_devolucao: Optional[date] = None, data_retirada: Optional[datetime] = None, 
                 data_devolucao_real: Optional[datetime] = None, condicao_item: Optional[str] = None, 
                 id_funcionario_recebimento: Optional[int] = None, multa_aplicada: Optional[Decimal] = None, 
                 multa_paga: Optional[bool] = None, dias_atraso: Optional[int] = None, **kwargs):
        super().__init__(id=id_transacao, tipo="aluguel", **kwargs)
        self.id_transacao = id_transacao
        self.periodo = periodo
        self.data_devolucao = data_devolucao
        self.status = status or StatusAluguel.PENDENTE.value
        self.id_reserva = id_reserva
        self.data_inicio = data_inicio
        self.data_prevista_devolucao = data_prevista_devolucao
        self.data_retirada = data_retirada
        self.data_devolucao_real = data_devolucao_real
        self.condicao_item = condicao_item
        self.id_funcionario_recebimento = id_funcionario_recebimento
        self.multa_aplicada = multa_aplicada
        self.multa_paga = multa_paga or False
        self.dias_atraso = dias_atraso
