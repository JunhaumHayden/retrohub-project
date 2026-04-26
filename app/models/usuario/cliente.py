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
            **kwargs,
    ):
        # Aceita tanto `id_usuario=` (nomenclatura interna) quanto `id=`
        # (forma canônica usada por testes e camadas superiores).
        if "id" in kwargs:
            id_usuario = kwargs.pop("id") if id_usuario is None else id_usuario
        super().__init__(
            nome=nome,
            cpf=cpf,
            email=email,
            senha=senha,
            id=id_usuario,
            data_nascimento=data_nascimento,
            **kwargs,
        )
        self.dados_pagamento = dados_pagamento
        self.tipo_cliente = tipo_cliente or TipoCliente.REGULAR.value

    @property
    def id_usuario(self) -> Optional[int]:
        """Compat alias para código que ainda referencia ``id_usuario``."""
        return self.id

    @id_usuario.setter
    def id_usuario(self, value: Optional[int]) -> None:
        self.id = value
