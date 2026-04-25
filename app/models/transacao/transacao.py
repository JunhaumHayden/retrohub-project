from abc import ABC
from datetime import datetime
from typing import Optional
from decimal import Decimal

from app.models import Comprovante, Avaliacao, ItemTransacao
from app.models.enums import StatusPagamento
from app.models.usuario.cliente import Cliente
from app.models.usuario.funcionario import Funcionario


class Transacao(ABC):
    def __init__(
            self,
            id: int = None,
            valor_total: Optional[Decimal] = None,
            pagamento: Optional[str] = None,
            cliente: Optional[Cliente] = None,
            funcionario: Optional[Funcionario] = None,
            comprovante: Optional[Comprovante] = None,
            avaliacao: Optional[Avaliacao] = None,
            tipo: str = "transacao",
            data_transacao: Optional[datetime] = None,
            itens_transacao: Optional[list[ItemTransacao]] = None
    ):
        if type(self) is Transacao:
            raise TypeError("Erro: Operação Não permitida")

        self.id = id
        self.data_transacao = data_transacao or datetime.utcnow()
        self.valor_total = valor_total
        self.pagamento = pagamento or StatusPagamento.PENDENTE.value
        self.cliente = cliente
        self.funcionario = funcionario
        self.comprovante = comprovante
        self.avaliacao = avaliacao
        self.itens_transacao = itens_transacao or []
        self.tipo = tipo

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

    def __str__(self):
        return f"{self.__class__.__name__} id={self.id}, status={self.status}, valor={self.valor_total}, cliente={self.id_cliente}, funcionario={self.id_funcionario}"
