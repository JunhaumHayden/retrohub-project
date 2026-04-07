from app.models.usuario import Usuario, Cliente, Funcionario
from app.models.jogo import Jogo, MidiaFisica, MidiaDigital
from app.models.transacao import (
    Transacao, Venda, Reserva, Aluguel, ItemTransacao,
    Comprovante, Multa, Avaliacao
)

# This allows importing everything directly from app.models
__all__ = [
    "Usuario", "Cliente", "Funcionario",
    "Jogo", "MidiaFisica", "MidiaDigital",
    "Transacao", "Venda", "Reserva", "Aluguel",
    "ItemTransacao", "Comprovante", "Multa", "Avaliacao"
]
