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
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)

    __mapper_args__ = {
        "polymorphic_on": tipo,
        "polymorphic_identity": "transacao",
    }

    def __init__(self, *args, **kwargs):
        if type(self) is Transacao:
            raise TypeError("Erro: Operação Não permitida")
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

    def __str__(self):
        return f"{self.__class__.__name__} id={self.id}, status={self.status}, valor={self.valor_total}, cliente={self.id_cliente}, funcionario={self.id_funcionario}"
