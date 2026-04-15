from datetime import date
from typing import Optional
from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database_config import Base

class Usuario(Base):
    __tablename__ = 'usuario'

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    cpf: Mapped[str] = mapped_column(String(14), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    senha: Mapped[str] = mapped_column(String(255), nullable=False)
    data_cadastro: Mapped[Optional[date]] = mapped_column(Date, default=date.today)
    data_nascimento: Mapped[Optional[date]] = mapped_column(Date)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)

    __mapper_args__ = {
        "polymorphic_on": tipo,
        "polymorphic_identity": "transacao",
    }

    def __init__(self, *args, **kwargs):
        if type(self) is Usuario:
            raise TypeError("Erro: Operação Não permitida")
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, nome='{self.nome},tipo='{self.tipo}')>"

    def __str__(self):
        return f"{self.__class__.__name__} id={self.id}, nome={self.nome}, cpf={self.cpf}, email={self.email}, data_cadastro={self.data_cadastro}, data_nascimento={self.data_nascimento}"
