"""
Classes e utilitários do modelo base para evitar importações circulares.
"""
from app.models.enums import StatusSituacao


class BaseModel:
    def __init__(self, id: int = 0):
        self.id = id


class ExemplarCollection(list):
    """
    Coleção customizada para exemplares que herda de list.
    Permite adicionar métodos específicos para a coleção de exemplares.
    """
    def get_available_count(self) -> int:
        """Calcula o número de exemplares disponíveis na coleção."""
        return sum(1 for ex in self if ex.situacao == StatusSituacao.DISPONIVEL.value)

    def add_exemplar(self, exemplar):
        """Adiciona um exemplar à coleção."""
        self.append(exemplar)


class CatalogoReference:
    def __init__(self, id_catalogo: int):
        self.id = id_catalogo
        self._catalogo = None

    def set_catalogo(self, catalogo):
        self._catalogo = catalogo

    def __getattr__(self, name):
        if self._catalogo:
            return getattr(self._catalogo, name)
        raise AttributeError(f"'CatalogoReference' object has no attribute '{name}' until resolved")
