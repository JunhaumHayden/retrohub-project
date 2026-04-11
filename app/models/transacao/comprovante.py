from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database_config import Base

class Comprovante(Base):
    __tablename__ = 'comprovante'

    id: Mapped[int] = mapped_column(primary_key=True)
    id_transacao: Mapped[Optional[int]] = mapped_column(ForeignKey('transacao.id', ondelete='CASCADE'))
    tipo: Mapped[Optional[str]] = mapped_column(String)
    data_envio: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow)
    codigo_rastreio: Mapped[Optional[str]] = mapped_column(String(255))
