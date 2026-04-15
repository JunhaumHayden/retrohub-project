from datetime import date
from typing import Optional
from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.usuario.usuario import Usuario
from app.models.enums import TipoCliente

class Cliente(Usuario):
    __tablename__ = 'cliente'

    id_usuario: Mapped[int] = mapped_column(ForeignKey('usuario.id', ondelete='CASCADE'), primary_key=True)
    dados_pagamento: Mapped[Optional[str]] = mapped_column(String(255))
    tipo_cliente: Mapped[Optional[str]] = mapped_column(String(50), default=TipoCliente.REGULAR.value)

    __mapper_args__ = {
        "polymorphic_identity": "cliente",
    }
