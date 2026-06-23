from typing import List, Optional
from app.models.catalogo.catalogo import Catalogo
from app.repository.interface.catalogo_repository_interface import CatalogoRepositoryInterface
from app.models.enums import StatusSituacao

class CatalogoService:
    """
    Service layer for Catalogo operations.
    """

    def __init__(self, repository: CatalogoRepositoryInterface):
        self.repository = repository

    def list_all(self, situacao: Optional[str] = None) -> List[Catalogo]:
        """List all catalog items, optionally filtered by situacao."""
        if situacao:
            return self.repository.get_by_situacao(situacao)
        return self.repository.list_all()

    def get_by_id(self, id: int) -> Optional[Catalogo]:
        return self.repository.get_by_id(id)

    def get_by_title(self, title: str) -> Optional[Catalogo]:
        return self.repository.get_by_title(title)

    def create(self, catalogo: Catalogo) -> Optional[Catalogo]:
        if not catalogo.titulo:
            raise ValueError("Título é obrigatório")
        if self.repository.get_by_title(catalogo.titulo):
            raise ValueError(f"Jogo com título '{catalogo.titulo}' já existe")
        if not catalogo.situacao:
            catalogo.situacao = StatusSituacao.DISPONIVEL
        return self.repository.create(catalogo)

    def update(self, id: int, catalogo_data: dict) -> Optional[Catalogo]:
        catalogo = self.repository.get_by_id(id)
        if not catalogo:
            return None
        
        if 'titulo' in catalogo_data and catalogo_data['titulo'] != catalogo.titulo:
            if self.repository.get_by_title(catalogo_data['titulo']):
                raise ValueError(f"Jogo com título '{catalogo_data['titulo']}' já existe")
        
        for field, value in catalogo_data.items():
            if hasattr(catalogo, field):
                setattr(catalogo, field, value)
        
        return self.repository.update(catalogo)

    def inactivate(self, id: int) -> Optional[Catalogo]:
        """Inactivates a catalog item (soft delete)."""
        catalogo = self.repository.get_by_id(id)
        if not catalogo:
            return None
        
        catalogo.situacao = StatusSituacao.INDISPONIVEL
        return self.repository.update(catalogo)

    def get_estoque_disponivel(self, catalogo_id: int) -> int:
        catalogo = self.repository.get_by_id(catalogo_id)
        if not catalogo or not hasattr(catalogo, 'exemplares'):
            return 0

        return catalogo.exemplares.get_available_count()
