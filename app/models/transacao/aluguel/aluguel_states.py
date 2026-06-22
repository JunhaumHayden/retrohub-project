from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from app.models.enums import StatusAluguel

if TYPE_CHECKING:
    from app.models.transacao.aluguel.aluguel import Aluguel


class AluguelState:
    def __init__(self, aluguel: "Aluguel"):
        self.aluguel = aluguel

    def processar_pagamento(self, sucesso: bool):
        raise ValueError("Transição de estado inválida")

    def pagamento_com_sucesso(self):
        raise ValueError("Transição de estado inválida")

    def pagamento_recusado(self):
        raise ValueError("Transição de estado inválida")

    def registrar_retirada(self):
        raise ValueError("Transição de estado inválida")

    def finalizar_aluguel(self):
        raise ValueError("Transição de estado inválida")

    def renovar_aluguel(self, dias_adicionais: int):
        raise ValueError("Transição de estado inválida")

    def cancelar_aluguel(self):
        raise ValueError("Transição de estado inválida")

    def verificar_atraso(self):
        pass


class EstadoSolicitado(AluguelState):
    def processar_pagamento(self, sucesso: bool):
        self.aluguel._contexto_pagamento = "SOLICITADO"
        self.aluguel.status = StatusAluguel.PROCESSANDO_PAGAMENTO.value
        self.aluguel._set_state(self.aluguel.status)
        self.aluguel.state.processar_pagamento(sucesso)

    def cancelar_aluguel(self):
        if self.aluguel.data_inicio and self.aluguel.data_inicio <= date.today():
            raise ValueError("Não é possível cancelar um aluguel que já iniciou ou está no dia de retirada.")

        self.aluguel.status = StatusAluguel.CANCELADO.value
        self.aluguel._set_state(self.aluguel.status)

    def renovar_aluguel(self, dias_adicionais: int):
        if dias_adicionais <= 0:
            raise ValueError("O período de renovação deve ser maior que zero.")
        dias_atraso = getattr(self.aluguel, "dias_atraso", 0) or 0
        if dias_atraso > 0:
            raise ValueError("Não é possível renovar um aluguel em atraso.")


class EstadoProcessandoPagamento(AluguelState):
    def processar_pagamento(self, sucesso: bool):
        if sucesso:
            self.pagamento_com_sucesso()
        else:
            self.aluguel.status = StatusAluguel.PROCESSANDO_PAGAMENTO.value

    def pagamento_com_sucesso(self):
        contexto = getattr(self.aluguel, "_contexto_pagamento", "SOLICITADO")
        if contexto == "ATRASADO":
            self.aluguel.status = StatusAluguel.ATIVO.value
        else:
            self.aluguel.status = StatusAluguel.APROVADO.value
        self.aluguel._set_state(self.aluguel.status)

    def pagamento_recusado(self):
        contexto = getattr(self.aluguel, "_contexto_pagamento", "SOLICITADO")
        if contexto == "ATRASADO":
            self.aluguel.status = StatusAluguel.ATRASADO.value
        else:
            self.aluguel.status = StatusAluguel.CANCELADO.value
        self.aluguel._set_state(self.aluguel.status)


class EstadoPagamentoConfirmado(AluguelState):
    def registrar_retirada(self):
        self.aluguel.status = StatusAluguel.ATIVO.value
        self.aluguel._set_state(self.aluguel.status)

    def cancelar_aluguel(self):
        raise ValueError("Não é possível cancelar um aluguel com pagamento confirmado.")


class EstadoAtivo(AluguelState):
    def verificar_atraso(self):
        if (
            self.aluguel.data_prevista_devolucao
            and self.aluguel.data_prevista_devolucao < date.today()
        ):
            self.aluguel.status = StatusAluguel.ATRASADO.value
            self.aluguel._set_state(self.aluguel.status)

    def finalizar_aluguel(self):
        self.aluguel.status = StatusAluguel.FINALIZADO.value
        self.aluguel._set_state(self.aluguel.status)

    def renovar_aluguel(self, dias_adicionais: int):
        if dias_adicionais <= 0:
            raise ValueError("O período de renovação deve ser maior que zero.")
        self.verificar_atraso()
        if self.aluguel.status == StatusAluguel.ATRASADO.value:
            raise ValueError("Não é possível renovar um aluguel em atraso.")
        dias_atraso = getattr(self.aluguel, "dias_atraso", 0) or 0
        if dias_atraso > 0:
            self.aluguel.status = StatusAluguel.ATRASADO.value
            self.aluguel._set_state(self.aluguel.status)
            raise ValueError("Não é possível renovar um aluguel em atraso.")

    def cancelar_aluguel(self):
        raise ValueError("Não é possível cancelar um aluguel ativo.")


class EstadoAtrasado(AluguelState):
    def processar_pagamento(self, sucesso: bool):
        self.aluguel._contexto_pagamento = "ATRASADO"
        self.aluguel.status = StatusAluguel.PROCESSANDO_PAGAMENTO.value
        self.aluguel._set_state(self.aluguel.status)
        self.aluguel.state.processar_pagamento(sucesso)

    def finalizar_aluguel(self):
        self.aluguel.status = StatusAluguel.FINALIZADO.value
        self.aluguel._set_state(self.aluguel.status)

    def renovar_aluguel(self, dias_adicionais: int):
        raise ValueError("Não é possível renovar um aluguel atrasado.")

    def cancelar_aluguel(self):
        raise ValueError("Não é possível cancelar um aluguel atrasado.")


class EstadoFinalizado(AluguelState):
    pass


class EstadoCancelado(AluguelState):
    pass
