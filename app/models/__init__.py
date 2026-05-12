from .usuario import Usuario, Cliente, Funcionario
from .estoque import Exemplar, MidiaFisica, MidiaDigital
from .catalogo import Catalogo
from .transacao import (
    Transacao, Venda, Aluguel, Reserva,
    ItemTransacao, Comprovante, Multa, Avaliacao
)

__all__ = [
    "Usuario", "Cliente", "Funcionario",
    "Catalogo", "Exemplar", "MidiaFisica", "MidiaDigital",
    "Transacao", "Venda", "Aluguel", "Reserva",
    "ItemTransacao", "Comprovante", "Multa", "Avaliacao"
]

# Backwards compatibility: historically the domain used the name `Jogo`.
# Provide an alias so older tests and code importing `Jogo` continue to work.
Jogo = Catalogo
__all__.insert(3, "Jogo")
