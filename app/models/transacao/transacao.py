from __future__ import annotations

from abc import ABC
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from app.models.enums import StatusPagamento

if TYPE_CHECKING:
    from app.models.transacao.comprovante import Comprovante
    from app.models.transacao.avaliacao import Avaliacao
    from app.models.transacao.item_transacao import ItemTransacao
    from app.models.usuario.cliente import Cliente
    from app.models.usuario.funcionario import Funcionario


class Transacao(ABC):
    """
    Classe base abstrata para Venda e Aluguel.

    Mantém navegação bidirecional com Comprovante e ItemTransacao:
    ao receber a lista, marca cada item com `item.transacao = self`.
    """

    def __init__(
            self,
            id: int = None,
            valor_total: Optional[Decimal] = None,
            tipo: str = "transacao",
            data_transacao: Optional[datetime] = None,
            status_pagamento: Optional[str] = None,
            cliente: Optional["Cliente"] = None,
            funcionario: Optional["Funcionario"] = None,
            comprovantes: Optional[list["Comprovante"]] = None,
            itens_transacao: Optional[list["ItemTransacao"]] = None,
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

    @property
    def id_cliente(self):
        return getattr(self.cliente, "id", None)

    @property
    def id_funcionario(self):
        return getattr(self.funcionario, "id", None)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

    def __str__(self):
        status = getattr(self, "status", self.pagamento)
        return (
            f"{self.__class__.__name__} id={self.id}, status={status}, "
            f"valor={self.valor_total}, cliente={self.id_cliente}, "
            f"funcionario={self.id_funcionario}"
        )
