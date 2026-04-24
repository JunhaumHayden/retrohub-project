from datetime import date
from typing import Optional

from app.models.estoque.exemplar import Exemplar

class MidiaDigital(Exemplar):
    def __init__(self, id_exemplar: int, chave_ativacao: str, data_expiracao: Optional[date] = None, **kwargs):
        super().__init__(id=id_exemplar, tipo_midia="DIGITAL", **kwargs)
        self.id_exemplar = id_exemplar
        self.chave_ativacao = chave_ativacao
        self.data_expiracao = data_expiracao
