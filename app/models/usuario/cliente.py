from datetime import date
from typing import Optional
from sqlalchemy import Column, String

from app.models.usuario.usuario import Usuario
from app.models.enums import TipoCliente

class Cliente(Usuario):
    __tablename__ = 'clientes'

    dados_pagamento = Column(String(255))
    tipo_cliente = Column(String(50), default=TipoCliente.REGULAR.value)

    def __init__(
            self,
            id_usuario: int = None,
            nome: str = None,
            cpf: str = None,
            email: str = None,
            senha: str = None,
            data_nascimento: date = None,
            dados_pagamento: Optional[str] = None,
            tipo_cliente: Optional[str] = None,
            **kwargs
    ):
        super().__init__(
            nome=nome,
            cpf=cpf,
            email=email,
            senha=senha,
            id=id_usuario,
            data_nascimento=data_nascimento,
            **kwargs
        )
        self.dados_pagamento = dados_pagamento
        self.tipo_cliente = tipo_cliente or TipoCliente.REGULAR.value
