from enum import Enum


class StatusTransacao(Enum):
    PENDENTE = 'PENDENTE'
    CONCLUIDA = 'CONCLUIDA'
    CANCELADA = 'CANCELADA'


class StatusVenda(Enum):
    FINALIZADA = 'FINALIZADA'
    ESTORNADA = 'ESTORNADA'


class StatusAluguel(Enum):
    ATIVO = 'ATIVO'
    FINALIZADO = 'FINALIZADO'
    ATRASADO = 'ATRASADO'
    SOLICITADO = 'SOLICITADO'
    APROVADO = 'APROVADO'


class StatusReserva(Enum):
    ATIVA = 'ATIVA'
    CANCELADA = 'CANCELADA'
    EXPIRADA = 'EXPIRADA'
    CONVERTIDA = 'CONVERTIDA'


class StatusPagamento(Enum):
    PENDENTE = 'PENDENTE'
    PAGO = 'PAGO'


class TipoComprovante(Enum):
    VENDA = 'VENDA'
    ALUGUEL = 'ALUGUEL'


class TipoCliente(Enum):
    REGULAR = 'regular'
    PREMIUM = 'premium'
