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
    BASICO = 'BASICO'

class TipoFuncionario(Enum):
    REGULAR = 'REGULAR'
    PREMIUM = 'PREMIUM'

class StatusSituacao(Enum):
    DISPONIVEL = 'DISPONIVEL'
    INDISPONIVEL = 'INDISPONIVEL'

class StatusConservacao(Enum):
    EXCELENTE = 'EXCELENTE'
    BOM = 'BOM'
    POUCA_AVARIA = 'POUCA_AVARIA'
    AVARIADO = 'AVARIADO'
    RUIM = 'RUIM'

