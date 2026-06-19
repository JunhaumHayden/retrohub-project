from __future__ import annotations
from abc import ABC
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base_model import Base
from app.models.enums import StatusPagamento

if TYPE_CHECKING:
    from app.models.transacao.comprovante import Comprovante
    from app.models.transacao.item_transacao import ItemTransacao
    from app.models.usuario.cliente import Cliente
    from app.models.usuario.funcionario import Funcionario

class Transacao(Base):
    __tablename__ = 'transacoes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    valor_total = Column(Numeric(10, 2))
    tipo = Column(String(50), nullable=False)
    data_transacao = Column(DateTime, default=datetime.utcnow)
    status_pagamento = Column(Enum(StatusPagamento), default=StatusPagamento.PENDENTE)
    
    id_cliente = Column(Integer, ForeignKey('clientes.id'))
    id_funcionario = Column(Integer, ForeignKey('funcionarios.id'))

    cliente = relationship("Cliente")
    funcionario = relationship("Funcionario")
    itens_transacao = relationship("ItemTransacao", back_populates="transacao")
    comprovantes = relationship("Comprovante", back_populates="transacao")
    avaliacao = relationship("Avaliacao", uselist=False, back_populates="transacao")

    __mapper_args__ = {
        'polymorphic_identity': 'transacao',
        'polymorphic_on': tipo
    }

    def __init__(
            self,
            id: int = None,
            valor_total: Optional[Decimal] = None,
            tipo: str = "transacao",
            data_transacao: Optional[datetime] = None,
            status_pagamento: Optional[str] = None,
            cliente: Optional["Cliente"] = None,
            funcionario: Optional["Funcionario"] = None,
            comprovantes: Optional[List["Comprovante"]] = None,
            itens_transacao: Optional[List["ItemTransacao"]] = None,
            avaliacao: Optional["Avaliacao"] = None,
            **kwargs,
    ):
        if type(self) is Transacao:
            raise TypeError("Erro: Operação Não permitida")

        self.id = id
        self.valor_total = valor_total
        self.tipo = tipo
        self.data_transacao = data_transacao or datetime.utcnow()
        self.pagamento = status_pagamento or StatusPagamento.PENDENTE.value
        self.cliente = cliente
        self.funcionario = funcionario
        self.itens_transacao = list(itens_transacao) if itens_transacao else []
        self.comprovantes = list(comprovantes) if comprovantes else []
        self.avaliacao = avaliacao

        for item in self.itens_transacao:
            item.transacao = self
        for comprovante in self.comprovantes:
            comprovante.transacao = self
        if self.avaliacao is not None:
            self.avaliacao.transacao = self

    def adicionar_comprovante(self, comprovante: "Comprovante") -> None:
        """Adiciona um comprovante mantendo a navegação bidirecional."""
        comprovante.transacao = self
        self.comprovantes.append(comprovante)

    def adicionar_item(self, item: "ItemTransacao") -> None:
        """Adiciona um item de transação mantendo a navegação bidirecional."""
        item.transacao = self
        self.itens_transacao.append(item)
