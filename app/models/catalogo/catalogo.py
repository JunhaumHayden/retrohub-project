from typing import Optional
from decimal import Decimal


class Catalogo:
    def __init__(self, id: int, titulo: str, descricao: Optional[str] = None,
                 ativo: Optional[bool] = True, genero: Optional[str] = None, 
                 classificacao: Optional[str] = None, valor_venda: Optional[Decimal] = None, 
                 valor_diaria_aluguel: Optional[Decimal] = None):
        self.id = id or None
        self.titulo = titulo
        self.descricao = descricao
        self.ativo = ativo
        self.genero = genero
        self.classificacao = classificacao
        self.valor_venda = valor_venda
        self.valor_diaria_aluguel = valor_diaria_aluguel
        self.exemplares = []

    @property
    def estoque_disponivel(self) -> int:
        """Calcula o estoque disponível em memória."""
        return sum(1 for ex in self.exemplares if ex.situacao == 'DISPONIVEL')

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, titulo='{self.titulo}')>"