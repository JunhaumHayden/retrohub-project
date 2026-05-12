from datetime import date
from typing import Optional



class Avaliacao:
    def __init__(
            self,
            id: int,
            transacao: Optional["Transacao"] = None,
            nota: Optional[int] = None,
            comentario: Optional[str] = None,
            data_avaliacao: Optional[date] = None
    ):
        self.id = id
        self.transacao = transacao
        self.nota = nota
        self.comentario = comentario
        self.data_avaliacao = data_avaliacao or date.today()
