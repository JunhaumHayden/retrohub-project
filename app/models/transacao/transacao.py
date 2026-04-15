from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database_config import Base
from app.models.enums import StatusTransacao
from app.models.enums import StatusPagamento

class Transacao(Base):
    __tablename__ = 'transacao'

    id: Mapped[int] = mapped_column(primary_key=True)
    data_transacao: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow)
    valor_total: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    pagamento: Mapped[Optional[str]] = mapped_column(String, default=StatusPagamento.PENDENTE.value)
    status: Mapped[Optional[str]] = mapped_column(String, default=StatusTransacao.PENDENTE.value)
    id_cliente: Mapped[Optional[int]] = mapped_column(ForeignKey('cliente.id_usuario'))
    id_funcionario: Mapped[Optional[int]] = mapped_column(ForeignKey('funcionario.id_usuario'))

    def __repr__(self) -> str:
        return f"<Transacao(id={self.id}, valor_total={self.valor_total})>"
