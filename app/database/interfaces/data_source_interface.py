from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Type

T = TypeVar('T')

class DataSourceInterface(ABC):
    """
    Interface for data sources (memory, database, etc.)
    Provides generic CRUD operations for any entity type
    """
    
    @abstractmethod
    def load_data(self) -> None:
        """Load initial data from JSON file"""
        pass
    
    @abstractmethod
    def get_all(self, entity_type: Type[T]) -> List[T]:
        """Get all entities of a specific type"""
        pass
    
    @abstractmethod
    def get_by_id(self, entity_type: Type[T], entity_id: int) -> Optional[T]:
        """Get entity by ID and type"""
        pass
    
    @abstractmethod
    def get_by_field(self, entity_type: Type[T], field_name: str, value) -> Optional[T]:
        """Get entity by field value"""
        pass
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """Create a new entity"""
        pass
    
    @abstractmethod
    def update(self, entity: T) -> Optional[T]:
        """Update an existing entity"""
        pass
    
    @abstractmethod
    def delete(self, entity_type: Type[T], entity_id: int) -> bool:
        """Delete entity by ID"""
        pass
    
    @abstractmethod
    def get_next_id(self, entity_type: Type[T]) -> int:
        """Get next available ID for entity type"""
        pass
