from typing import Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.usuario.usuario import Usuario

class Cliente(Usuario):
    __tablename__ = 'cliente'

    id_usuario: Mapped[int] = mapped_column(ForeignKey('usuario.id', ondelete='CASCADE'), primary_key=True)
    dados_pagamento: Mapped[Optional[str]] = mapped_column(String(255))

    __mapper_args__ = {
        "polymorphic_identity": "cliente",
    }

    def __repr__(self) -> str:
        return f"<Cliente(id={self.id_usuario}, nome='{self.nome}')>"
