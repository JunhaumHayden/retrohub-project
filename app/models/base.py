"""
Base model classes and utilities to avoid circular imports
"""

from typing import Any, Dict, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    pass


class BaseModel(ABC):
    """Base class for all models with common functionality"""
    
    def __init__(self, id: Optional[int] = None):
        self.id = id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation"""
        result = {}
        for key, value in self.__dict__.items():
            if hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [item.to_dict() if hasattr(item, 'to_dict') else item for item in value]
            else:
                result[key] = value
        return result
    
    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"<{class_name}(id={self.id})>"


class CatalogoReference:
    """Helper class to handle Catalogo references without circular imports"""
    
    def __init__(self, catalogo_id: int):
        self._catalogo_id = catalogo_id
        self._catalogo = None
    
    @property
    def id(self) -> int:
        return self._catalogo_id
    
    def get_catalogo(self, data_source=None):
        """Get the actual Catalogo object from data source"""
        if self._catalogo is None and data_source is not None:
            from app.models.catalogo.catalogo import Catalogo
            self._catalogo = data_source.get_by_id(Catalogo, self._catalogo_id)
        return self._catalogo
    
    def set_catalogo(self, catalogo):
        """Set the Catalogo object directly"""
        self._catalogo = catalogo
        if catalogo is not None:
            self._catalogo_id = catalogo.id


class ExemplarCollection:
    """Helper class to manage exemplar collections without circular imports"""
    
    def __init__(self):
        self._exemplares = []
    
    def add_exemplar(self, exemplar):
        """Add an exemplar to the collection"""
        self._exemplares.append(exemplar)
    
    def get_exemplares(self):
        """Get all exemplares"""
        return self._exemplares
    
    def get_available_count(self):
        """Get count of available exemplares"""
        return sum(1 for ex in self._exemplares if getattr(ex, 'situacao', None) == 'DISPONIVEL')
    
    def __len__(self):
        return len(self._exemplares)
    
    def __iter__(self):
        return iter(self._exemplares)
