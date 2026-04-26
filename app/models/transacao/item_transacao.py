from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.models.transacao.transacao import Transacao
    from app.models.estoque.exemplar import Exemplar


class ItemTransacao:
    """
    Linha de itens de uma Transacao.

    A referência reversa para `Transacao` é configurada pelo construtor de
    Transacao (ou pelo método `adicionar_item`), evitando importação circular.
    """

    def __init__(
            self,
            id: int,
            transacao: Optional["Transacao"] = None,
            exemplar: Optional["Exemplar"] = None,
            valor_unitario: Optional[Decimal] = None,
            quantidade: int = 1,
    ):
        self.id = id
        self.transacao = transacao
        self.exemplar = exemplar
        self.valor_unitario = valor_unitario
        self.quantidade = quantidade

    @property
    def valor_item(self) -> Optional[Decimal]:
        if self.valor_unitario is None:
            return None
        return Decimal(self.valor_unitario) * Decimal(self.quantidade)

    @property
    def id_transacao(self) -> Optional[int]:
        return getattr(self.transacao, "id", None)

    @property
    def id_exemplar(self) -> Optional[int]:
        return getattr(self.exemplar, "id", None)

    def __repr__(self):
        return (
            f"<ItemTransacao(id={self.id}, transacao={self.id_transacao}, "
            f"exemplar={self.id_exemplar}, qtd={self.quantidade})>"
        )
