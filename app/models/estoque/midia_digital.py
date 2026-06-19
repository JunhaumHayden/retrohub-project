from datetime import date
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, String, Integer, Numeric, Date, ForeignKey

from app.models.estoque.exemplar import Exemplar

class MidiaDigital(Exemplar):
    __tablename__ = 'midias_digitais'

    id = Column(Integer, ForeignKey('exemplares.id'), primary_key=True)
    chave_ativacao = Column(String(100), unique=True, nullable=False)
    data_expiracao = Column(Date)
    plataforma = Column(String(50))
    valor_venda = Column(Numeric(10, 2))
    valor_diaria_aluguel = Column(Numeric(10, 2))

    __mapper_args__ = {
        'polymorphic_identity': 'DIGITAL',
    }

    def __init__(
            self,
            id_exemplar: int,
            chave_ativacao: str,
            catalogo,
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
