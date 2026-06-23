from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.base_model import Base
from app.models.enums import TipoComprovante

if TYPE_CHECKING:
    from app.models.transacao.transacao import Transacao

class Comprovante(Base):
    __tablename__ = 'comprovantes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String(50))
    data_envio = Column(DateTime, default=datetime.now)
    tipo_comprovante = Column(String(50), default=TipoComprovante.RESERVA.value)
    codigo_rastreio = Column(String(100))
    id_transacao = Column(Integer, ForeignKey('transacoes.id'))

    transacao = relationship("Transacao", back_populates="comprovantes")

    def __init__(
            self,
            id: int = None,
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

    @classmethod
    def emitir(
            cls,
            tipo_comprovante: str,
            transacao: Optional["Transacao"] = None,
            comprovante_id: Optional[int] = None,
    ) -> "Comprovante":
        """sd Devolucao — <<create>> emitir(dados) no Comprovante."""
        return cls(
            id=comprovante_id,
            tipo_comprovante=tipo_comprovante,
            transacao=transacao,
        )

    def __repr__(self):
        return (
            f"<Comprovante(id={self.id}, tipo={self.tipo_comprovante}, "
            f"transacao={self.id_transacao})>"
        )
