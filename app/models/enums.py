from enum import Enum

class StatusVenda(Enum):
    FINALIZADA = 'FINALIZADA'
    PENDENTE = 'PENDENTE'
    ESTORNADA = 'ESTORNADA'
    CANCELADA = 'CANCELADA'


class StatusAluguel(Enum):
    ATIVO = 'ATIVO'
    PENDENTE = 'PENDENTE'
    FINALIZADO = 'FINALIZADO'
    ATRASADO = 'ATRASADO'
    SOLICITADO = 'SOLICITADO'
    APROVADO = 'APROVADO'

class StatusReserva(Enum):
    ATIVA = 'ATIVA'
    PENDENTE = 'PENDENTE'
    CANCELADA = 'CANCELADA'
    EXPIRADA = 'EXPIRADA'
    ATENDIDA = 'ATENDIDA'

class StatusPagamento(Enum):
    PENDENTE = 'PENDENTE'
    ESTORNADO = 'ESTORNADO'
    CANCELADO = 'CANCELADO'
    PAGO = 'PAGO'

class TipoComprovante(Enum):
    VENDA = 'VENDA'
    ALUGUEL = 'ALUGUEL'
    RESERVA = 'RESERVA'
    DEVOLUCAO = 'DEVOLUCAO'

class TipoCliente(Enum):
    REGULAR = 'REGULAR'
    PREMIUM = 'PREMIUM'

class TipoFuncionario(Enum):
    REGULAR = 'REGULAR'
    PREMIUM = 'PREMIUM'

class StatusCatalogo(Enum):
    DISPONIVEL = 'DISPONIVEL'
    INDISPONIVEL = 'INDISPONIVEL'
