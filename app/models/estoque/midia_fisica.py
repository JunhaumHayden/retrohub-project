from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.estoque.exemplar import Exemplar

class MidiaFisica(Exemplar):
    __tablename__ = 'midia_fisica'

    id_exemplar: Mapped[int] = mapped_column(ForeignKey('exemplar.id', ondelete='CASCADE'), primary_key=True)
    codigo_barras: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    estado_conservacao: Mapped[Optional[str]] = mapped_column(String(100))

    __mapper_args__ = {
        "polymorphic_identity": "FISICA",
    }
