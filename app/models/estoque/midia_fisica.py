from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, Enum

from app.models.estoque.exemplar import Exemplar
from app.models.enums import StatusConservacao

class MidiaFisica(Exemplar):
    __tablename__ = 'midias_fisicas'
    
    id = Column(Integer, ForeignKey('exemplares.id'), primary_key=True)
    codigo_barras = Column(String(100), unique=True, nullable=False)
    estado_conservacao = Column(Enum(StatusConservacao), default=StatusConservacao.BOM)
    plataforma = Column(String(50))
    valor_venda = Column(Numeric(10, 2))
    valor_diaria_aluguel = Column(Numeric(10, 2))

    __mapper_args__ = {
        'polymorphic_identity': 'FISICA',
    }

    def __init__(
            self,
            id_exemplar: int,
            codigo_barras: str,
            catalogo,
            estado_conservacao: Optional[StatusConservacao] = StatusConservacao.BOM,
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
        self.codigo_barras = codigo_barras
        self.estado_conservacao = estado_conservacao
        self.plataforma = plataforma
        self.valor_venda = valor_venda
        self.valor_diaria_aluguel = valor_diaria_aluguel

    def set_estado_conservacao(self, condicao: str) -> str:
        """sd Devolucao — setEstadoConservacao(condicao)."""
        self.estado_conservacao = StatusConservacao(condicao)
        return self.estado_conservacao
