from datetime import date, datetime
from typing import Optional
from decimal import Decimal

from app.models import Multa
from app.models.transacao.transacao import Transacao
from app.models.transacao.aluguel.reserva import Reserva
from app.models.enums import StatusAluguel
from app.models.usuario.funcionario import Funcionario

class Aluguel(Transacao):
    def __init__(
            self,
            id_transacao: Optional[int] = None,
            periodo: Optional[int] = None,
            data_devolucao: Optional[date] = None,
            status: Optional[str] = None,
            reserva: Reserva,
            data_inicio: Optional[date] = None,
            data_prevista_devolucao: Optional[date] = None,
            data_retirada: Optional[datetime] = None,
            data_devolucao_real: Optional[datetime] = None,
            condicao_item: Optional[str] = None,
            funcionario_recebimento: Funcionario,
            multa_aplicada = Multa(),
            multa_paga: Optional[bool] = None,
            dias_atraso: Optional[int] = None,
            **kwargs):
        super().__init__(id=id_transacao, tipo="aluguel", **kwargs)
        self.id_transacao = id_transacao
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
        self.multa_aplicada = multa_aplicada
        self.multa_paga = multa_paga or False
        self.multa_aplicada.dias_atraso = dias_atraso
