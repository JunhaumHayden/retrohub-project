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

    def registrar_retirada(self):
        raise ValueError("Transição de estado inválida")

    def finalizar_aluguel(self):
        raise ValueError("Transição de estado inválida")

    def renovar_aluguel(self, dias_adicionais: int):
        raise ValueError("Transição de estado inválida")

    def cancelar_aluguel(self):
        raise ValueError("Transição de estado inválida")


class EstadoSolicitado(AluguelState):
    def processar_pagamento(self, sucesso: bool):
        self.aluguel.state = EstadoProcessandoPagamento(self.aluguel)
        self.aluguel.state.processar_pagamento(sucesso)

    def cancelar_aluguel(self):
        if self.aluguel.data_inicio and self.aluguel.data_inicio <= date.today():
            raise ValueError("Não é possível cancelar um aluguel que já iniciou ou está no dia de retirada.")

        self.aluguel.status = StatusAluguel.CANCELADO.value
        self.aluguel._set_state(self.aluguel.status)

    def renovar_aluguel(self, dias_adicionais: int):
        if dias_adicionais <= 0:
            raise ValueError("O período de renovação deve ser maior que zero.")
        dias_atraso = getattr(self.aluguel, 'dias_atraso', 0) or 0
        if dias_atraso > 0:
            raise ValueError("Não é possível renovar um aluguel em atraso.")
        # Permite apenas estender o período no estado SOLICITADO sem alterar o status.
        return


class EstadoProcessandoPagamento(AluguelState):
    def processar_pagamento(self, sucesso: bool):
        if sucesso:
            self.aluguel.status = StatusAluguel.APROVADO.value
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
    def finalizar_aluguel(self):
        self.aluguel.status = StatusAluguel.FINALIZADO.value
        self.aluguel._set_state(self.aluguel.status)

    def renovar_aluguel(self, dias_adicionais: int):
        if dias_adicionais <= 0:
            raise ValueError("O período de renovação deve ser maior que zero.")
        dias_atraso = getattr(self.aluguel, 'dias_atraso', 0) or 0
        if dias_atraso > 0:
            self.aluguel.status = StatusAluguel.ATRASADO.value
            self.aluguel._set_state(self.aluguel.status)
            raise ValueError("Não é possível renovar um aluguel em atraso.")

    def cancelar_aluguel(self):
        raise ValueError("Não é possível cancelar um aluguel ativo.")


class EstadoAtrasado(AluguelState):
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
