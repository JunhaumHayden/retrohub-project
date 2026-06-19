from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional, Type, TypeVar

from app.database.interfaces.data_source_interface import DataSourceInterface

T = TypeVar('T')

class SQLiteDataSource(DataSourceInterface):
    """
    DataSource implementation for SQLite database using SQLAlchemy.
    """

    def __init__(self, db_url: str):
        self.engine = create_engine(db_url, echo=True)  # echo=True para logar as queries SQL
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def _get_session(self) -> Session:
        return self.SessionLocal()

    def load_data(self):
        # Em uma implementação de DB real, os dados já estão no banco.
        # Este método pode ser usado para criar as tabelas se elas não existirem.
        # from app.models import Base  # Supondo que seus modelos herdem de uma Base declarativa
        # Base.metadata.create_all(bind=self.engine)
        pass

    def get_all(self, entity_type: Type[T]) -> List[T]:
        with self._get_session() as session:
            return session.query(entity_type).all()

    def get_by_id(self, entity_type: Type[T], entity_id: int) -> Optional[T]:
        with self._get_session() as session:
            return session.query(entity_type).get(entity_id)

    def get_by_field(self, entity_type: Type[T], field_name: str, value) -> Optional[T]:
        with self._get_session() as session:
            return session.query(entity_type).filter(getattr(entity_type, field_name) == value).first()

    def create(self, entity: T) -> T:
        with self._get_session() as session:
            session.add(entity)
            session.commit()
            session.refresh(entity)
            return entity

    def update(self, entity: T) -> Optional[T]:
        with self._get_session() as session:
            session.merge(entity)
            session.commit()
            return entity

    def delete(self, entity_type: Type[T], entity_id: int) -> bool:
        with self._get_session() as session:
            entity = self.get_by_id(entity_type, entity_id)
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
