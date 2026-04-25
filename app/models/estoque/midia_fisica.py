from decimal import Decimal
from typing import Optional

from app.models import Catalogo
from app.models.estoque.exemplar import Exemplar

class MidiaFisica(Exemplar):
    def __init__(
            self,
            id_exemplar: int,
            codigo_barras: str,
            catalogo: Catalogo,
            estado_conservacao: Optional[str] = None,
            plataforma: Optional[str] = None,
            valor_venda: Optional[Decimal] = None,
            valor_diaria_aluguel: Optional[Decimal] = None,
            **kwargs
    ):
        super().__init__(
            id=id_exemplar,
            catalogo=catalogo,
            tipo_midia="FISICA",
            **kwargs
        )
        self.id_exemplar = id_exemplar
        self.codigo_barras = codigo_barras
        self.estado_conservacao = estado_conservacao
        self.plataforma = plataforma
        self.valor_venda = valor_venda
        self.valor_diaria_aluguel = valor_diaria_aluguel
