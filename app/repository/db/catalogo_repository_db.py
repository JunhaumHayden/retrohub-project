from typing import List, Optional
from app.models.catalogo.catalogo import Catalogo
from app.repository.interface.catalogo_repository_interface import CatalogoRepositoryInterface


class CatalogoRepositoryDB(CatalogoRepositoryInterface):
    """
    Implementação concreta do repositório de Catálogo para banco de dados real (via SQLAlchemy).
    """

    def __init__(self, session):
        self.session = session

    def list_all(self) -> List[Catalogo]:
        return self.session.query(Catalogo).all()

    def get_by_id(self, id: int) -> Optional[Catalogo]:
        return self.session.query(Catalogo).filter(Catalogo.id == id).first()

    def get_by_title(self, title: str) -> Optional[Catalogo]:
        return self.session.query(Catalogo).filter(Catalogo.titulo == title).first()

    def create(self, catalogo: Catalogo) -> Optional[Catalogo]:
        self.session.add(catalogo)
        self.session.commit()
        return catalogo

    def update(self, catalogo: Catalogo) -> Optional[Catalogo]:
        self.session.add(catalogo)
        self.session.commit()
        return catalogo

    def delete(self, id: int) -> bool:
        catalogo = self.get_by_id(id)
        if catalogo:
            self.session.delete(catalogo)
            self.session.commit()
            return True
        return False

    def get_by_genero(self, genero: str) -> List[Catalogo]:
        return self.session.query(Catalogo).filter(Catalogo.genero == genero).all()

    def get_by_situacao(self, situacao: str) -> List[Catalogo]:
        return self.session.query(Catalogo).filter(Catalogo.situacao == situacao).all()
