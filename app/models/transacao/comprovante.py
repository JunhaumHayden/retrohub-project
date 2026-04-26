from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from app.models.enums import TipoComprovante

if TYPE_CHECKING:
    from app.models.transacao.transacao import Transacao


class Comprovante:
    """
    Representa um comprovante emitido para uma Transacao (Venda ou Aluguel).

    A navegação para a transação é populada por `Transacao.__init__` /
    `Transacao.adicionar_comprovante`, evitando a importação circular.
    """

    def __init__(
            self,
            id: int,
            tipo: Optional[str] = None,
            data_envio: Optional[datetime] = None,
            tipo_comprovante: Optional[str] = None,
            codigo_rastreio: Optional[str] = None,
            transacao: Optional["Transacao"] = None,
    ):
        self.id = id
        self.tipo = tipo
        self.data_envio = data_envio or datetime.now()
        self.tipo_comprovante = tipo_comprovante or TipoComprovante.RESERVA.value
        self.codigo_rastreio = codigo_rastreio
        self.transacao = transacao

    @property
    def id_transacao(self) -> Optional[int]:
        return getattr(self.transacao, "id", None)

    def __repr__(self):
        return (
            f"<Comprovante(id={self.id}, tipo={self.tipo_comprovante}, "
            f"transacao={self.id_transacao})>"
        )
