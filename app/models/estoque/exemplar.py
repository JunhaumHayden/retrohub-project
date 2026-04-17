from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database_config import Base
from app.models.enums import StatusCatalogo


class Exemplar(Base):
    __tablename__ = 'exemplar'

    id: Mapped[int] = mapped_column(primary_key=True)
    id_catalogo: Mapped[int] = mapped_column(ForeignKey('catalogo.id', ondelete='CASCADE'))
    catalogo: Mapped["Catalogo"] = relationship(back_populates="exemplares")
    tipo_midia: Mapped[str] = mapped_column(String(50), nullable=False)
    plataforma: Mapped[Optional[str]] = mapped_column(String(100))
    situacao: Mapped[Optional[str]] = mapped_column(String(50), default=StatusCatalogo.DISPONIVEL.value)

    __mapper_args__ = {
        "polymorphic_on": "tipo_midia",
        "polymorphic_identity": "exemplar"
    }

    def __init__(self, *args, **kwargs):
        if type(self) is Exemplar:
            raise TypeError("Erro: Operação Não permitida")
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, id_catalogo={self.id_catalogo}, tipo={self.tipo_midia})>"

    def __str__(self):
        return f"{self.__class__.__name__} exemplar (ID: {self.id})"
