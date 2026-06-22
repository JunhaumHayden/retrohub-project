from sqlalchemy import create_engine, inspect as sa_inspect
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from typing import List, Optional, Type, TypeVar

from app.database.interfaces.data_source_interface import DataSourceInterface

T = TypeVar('T')

class SQLiteDataSource(DataSourceInterface):
    """
    DataSource implementation for SQLite database using SQLAlchemy.
    """

    def __init__(self, db_url: str):
        self.engine = create_engine(db_url, echo=True)  # echo=True para logar as queries SQL
        # Use scoped_session to keep a consistent session per thread/request
        self.SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=self.engine))

    def _get_session(self) -> Session:
        # scoped_session is callable and returns the current Session
        return self.SessionLocal()

    def load_data(self):
        # Em uma implementação de DB real, os dados já estão no banco.
        # Este método pode ser usado para criar as tabelas se elas não existirem.
        # from app.models import Base  # Supondo que seus modelos herdem de uma Base declarativa
        # Base.metadata.create_all(bind=self.engine)
        pass

    def get_all(self, entity_type: Type[T]) -> List[T]:
        session = self._get_session()
        results = session.query(entity_type).all()
        # access column attributes to ensure they are loaded while session is active
        for obj in results:
            for col in getattr(entity_type, '__table__', []).columns if hasattr(entity_type, '__table__') else []:
                _ = getattr(obj, col.name, None)
        return results

    def _touch_mapped_columns(self, entity_type: Type[T], obj: T) -> None:
        """Carrega colunas de todas as tabelas do mapeamento (inclui herança join)."""
        mapper = sa_inspect(entity_type)
        for table in mapper.tables:
            for col in table.columns:
                _ = getattr(obj, col.key, None)

    def get_by_id(self, entity_type: Type[T], entity_id: int) -> Optional[T]:
        session = self._get_session()
        # prefer Session.get for modern SQLAlchemy
        result = session.get(entity_type, entity_id)
        if result is not None:
            self._touch_mapped_columns(entity_type, result)
        return result

    def get_by_field(self, entity_type: Type[T], field_name: str, value) -> Optional[T]:
        session = self._get_session()
        return session.query(entity_type).filter(getattr(entity_type, field_name) == value).first()

    def create(self, entity: T) -> T:
        session = self._get_session()
        session.add(entity)
        session.commit()
        # refresh to load generated values
        session.refresh(entity)
        return entity

    def update(self, entity: T) -> Optional[T]:
        session = self._get_session()
        # Evita merge em instância já rastreada pela sessão (preserva FKs da superclasse).
        if entity in session:
            session.commit()
            session.refresh(entity)
            return entity

        entity = session.merge(entity)
        session.commit()
        session.refresh(entity)
        return entity

    def delete(self, entity_type: Type[T], entity_id: int) -> bool:
        session = self._get_session()
        entity = session.query(entity_type).get(entity_id)
        if entity:
            session.delete(entity)
            session.commit()
            return True
        return False

    def get_next_id(self, entity_type: Type[T]) -> int:
        # Em um DB real, o ID é geralmente autoincrementado pelo banco.
        # Esta função se torna menos relevante ou pode buscar o próximo valor de uma sequence.
        # Por simplicidade, vamos deixar o DB cuidar disso.
        return 0 # Retorna 0 ou None para indicar que o ID é gerado pelo DB
