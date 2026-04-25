from datetime import date
from typing import Optional

from app.models.usuario.usuario import Usuario
from app.models.enums import TipoCliente

class Cliente(Usuario):
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
