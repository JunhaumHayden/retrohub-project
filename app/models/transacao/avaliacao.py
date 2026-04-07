from typing import Optional
from sqlalchemy import Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database_config import Base

class Avaliacao(Base):
    __tablename__ = 'avaliacao'

    id: Mapped[int] = mapped_column(primary_key=True)
    id_transacao: Mapped[Optional[int]] = mapped_column(ForeignKey('transacao.id', ondelete='CASCADE'))
    nota: Mapped[Optional[int]] = mapped_column(Integer)
    comentario: Mapped[Optional[str]] = mapped_column(Text)
