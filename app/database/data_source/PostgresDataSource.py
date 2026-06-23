from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional, Type, TypeVar

from app.database.interfaces.data_source_interface import DataSourceInterface

T = TypeVar('T')

class PostgresDataSource(DataSourceInterface):
    """
    DataSource implementation for PostgreSQL database using SQLAlchemy.
    """

    def __init__(self, db_url: str):
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=self.engine)

    def _get_session(self) -> Session:
        return self.SessionLocal()

    # ... rest of the code remains the same

    def load_data(self):
        # Em uma implementação de DB real, os dados já estão no banco.
        # Este método pode ser usado para criar as tabelas se elas não existirem.
        # from app.database.base_model import Base
        # Base.metadata.create_all(bind=self.engine)
        pass

    def get_all(self, entity_type: Type[T]) -> List[T]:
        session = self._get_session()
        return session.query(entity_type).all()

    def get_by_id(self, entity_type: Type[T], entity_id: int) -> Optional[T]:
        session = self._get_session()
        return session.query(entity_type).get(entity_id)

    def get_by_field(self, entity_type: Type[T], field_name: str, value) -> Optional[T]:
        session = self._get_session()
        return session.query(entity_type).filter(getattr(entity_type, field_name) == value).first()

    def create(self, entity: T) -> T:
        session = self._get_session()
        session.add(entity)
        session.commit()
        return entity

    def update(self, entity: T) -> Optional[T]:
        session = self._get_session()
        entity = session.merge(entity)
        session.commit()
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
        return 0
