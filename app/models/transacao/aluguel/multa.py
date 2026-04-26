from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from app.models.enums import StatusPagamento

if TYPE_CHECKING:
    from app.models.transacao.aluguel.aluguel import Aluguel


class Multa:
    """Penalidade financeira ligada a um Aluguel.

    Possui referência reversa para o Aluguel, permitindo navegar
    bidirecionalmente. ``id_aluguel`` é exposto como property para
    serialização.
    """

    def __init__(
            self,
            id: Optional[int] = None,
            aluguel: Optional["Aluguel"] = None,
            dias_atraso: Optional[int] = None,
            valor: Optional[Decimal] = None,
            status: Optional[str] = None,
            data_calculo: Optional[date] = None,
    ):
        self.id = id
        self.aluguel = aluguel
        self.dias_atraso = dias_atraso
        self.valor = valor
        self.status = status or StatusPagamento.PENDENTE.value
        self.data_calculo = data_calculo

    @property
    def id_aluguel(self) -> Optional[int]:
        return getattr(self.aluguel, "id", None)

    def marcar_paga(self) -> None:
        self.status = StatusPagamento.PAGO.value

    def __repr__(self) -> str:
        return (
            f"<Multa(id={self.id}, aluguel={self.id_aluguel}, "
            f"dias_atraso={self.dias_atraso}, valor={self.valor}, "
            f"status={self.status})>"
        )
