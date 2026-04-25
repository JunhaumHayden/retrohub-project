from datetime import date
from decimal import Decimal
from typing import Optional

from app.models import Catalogo
from app.models.estoque.exemplar import Exemplar

class MidiaDigital(Exemplar):
    def __init__(
            self,
            id_exemplar: int,
            chave_ativacao: str,
            catalogo: Catalogo,
            data_expiracao: Optional[date] = None,
            plataforma: Optional[str] = None,
            valor_venda: Optional[Decimal] = None,
            valor_diaria_aluguel: Optional[Decimal] = None,
            **kwargs
    ):
        super().__init__(
            id=id_exemplar,
            catalogo=catalogo,
            tipo_midia="DIGITAL",
            **kwargs
        )
        self.chave_ativacao = chave_ativacao
        self.data_expiracao = data_expiracao
        self.plataforma = plataforma
        self.valor_venda = valor_venda
        self.valor_diaria_aluguel = valor_diaria_aluguel
