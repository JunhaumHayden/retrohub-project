from datetime import date
from typing import Optional
from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.usuario.usuario import Usuario

class Cliente(Usuario):
    __tablename__ = 'cliente'

    id_usuario: Mapped[int] = mapped_column(ForeignKey('usuario.id', ondelete='CASCADE'), primary_key=True)
    dados_pagamento: Mapped[Optional[str]] = mapped_column(String(255))
    data_cadastro: Mapped[Optional[date]] = mapped_column(Date, default=date.today)
    tipo_cliente: Mapped[Optional[str]] = mapped_column(String(50), default='regular')

    __mapper_args__ = {
        "polymorphic_identity": "cliente",
    }

    def __repr__(self) -> str:
        return f"<Cliente(id={self.id_usuario}, nome='{self.nome}')>"
