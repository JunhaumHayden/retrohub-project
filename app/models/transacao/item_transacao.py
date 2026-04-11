from typing import Optional
from decimal import Decimal
from sqlalchemy import Integer, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database_config import Base

class ItemTransacao(Base):
    __tablename__ = 'item_transacao'

    id: Mapped[int] = mapped_column(primary_key=True)
    id_transacao: Mapped[Optional[int]] = mapped_column(ForeignKey('transacao.id', ondelete='CASCADE'))
    id_exemplar: Mapped[Optional[int]] = mapped_column(ForeignKey('exemplar.id'))
    valor_unitario: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
