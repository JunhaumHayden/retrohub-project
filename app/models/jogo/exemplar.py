from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database_config import Base

class Exemplar(Base):
    __tablename__ = 'exemplar'

    id: Mapped[int] = mapped_column(primary_key=True)
    id_jogo: Mapped[int] = mapped_column(ForeignKey('jogo.id', ondelete='CASCADE'))
    tipo_midia: Mapped[str] = mapped_column(String(50), nullable=False)
    situacao: Mapped[Optional[str]] = mapped_column(String(50), default='DISPONIVEL')

    __mapper_args__ = {
        "polymorphic_on": "tipo_midia",
        "polymorphic_identity": "exemplar"
    }

    def __repr__(self) -> str:
        return f"<Exemplar(id={self.id}, id_jogo={self.id_jogo}, tipo={self.tipo_midia})>"
