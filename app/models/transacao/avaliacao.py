from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.models.transacao.transacao import Transacao


class Avaliacao:
    def __init__(
            self,
            id: int,
            transacao: Optional["Transacao"] = None,
            nota: Optional[int] = None,
            comentario: Optional[str] = None,
            data_avaliacao: Optional[date] = None,
    ):
        self.id = id
        self.transacao = transacao
        self.nota = nota
        self.comentario = comentario
        self.data_avaliacao = data_avaliacao or date.today()

    @property
    def id_transacao(self) -> Optional[int]:
        return getattr(self.transacao, "id", None)
