from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from app.database.base_model import Base

if TYPE_CHECKING:
    from app.models.transacao.transacao import Transacao
    from app.models.estoque.exemplar import Exemplar

class ItemTransacao(Base):
    __tablename__ = 'itens_transacao'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_transacao = Column(Integer, ForeignKey('transacoes.id'))
    id_exemplar = Column(Integer, ForeignKey('exemplares.id'))
    valor_unitario = Column(Numeric(10, 2))
    quantidade = Column(Integer, default=1)

    transacao = relationship("Transacao", back_populates="itens_transacao")
    exemplar = relationship("Exemplar")

    def __init__(
            self,
            id: int = None,
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

    def __repr__(self):
        return (
            f"<ItemTransacao(id={self.id}, transacao={self.id_transacao}, "
            f"exemplar={self.id_exemplar}, qtd={self.quantidade})>"
        )
