"""
Dependency Injection Container
Manages the creation and lifecycle of application components
"""

from typing import Optional
import os

from app.database.mock_data_source import MockDataSource
from app.database.interfaces.data_source_interface import DataSourceInterface
from app.repository.mock.usuario_repository_mock import UsuarioRepositoryMock
from app.repository.mock.catalogo_repository_mock import CatalogoRepositoryMock
from app.repository.interface.usuario_repository_interface import UsuarioRepositoryInterface
from app.repository.interface.catalogo_repository_interface import CatalogoRepositoryInterface
from app.services.usuario_service import UsuarioService
from app.services.catalogo_service import CatalogoService
from app.services.aluguel_service import AluguelService


class Container:
    """
    Dependency injection container for the application
    """
    
    def __init__(self):
        self._data_source: Optional[DataSourceInterface] = None
        self._usuario_repository: Optional[UsuarioRepositoryInterface] = None
        self._catalogo_repository: Optional[CatalogoRepositoryInterface] = None
        self._usuario_service: Optional[UsuarioService] = None
        self._catalogo_service: Optional[CatalogoService] = None
        self._aluguel_service: Optional[AluguelService] = None
    
    @property
    def data_source(self) -> DataSourceInterface:
        """Get the data source instance"""
        if self._data_source is None:
            # Check if we should use mock or real database
            use_mock = os.getenv('USE_MOCK_DB', 'true').lower() == 'true'
            
            if use_mock:
                self._data_source = MockDataSource()
            else:
                # TODO: Implement real database data source
                raise NotImplementedError("Real database data source not implemented yet")
            
            # Load initial data
            if hasattr(self._data_source, 'load_data'):
                self._data_source.load_data()
        
        return self._data_source
    
    @property
    def usuario_repository(self) -> UsuarioRepositoryInterface:
        """Get the usuario repository instance"""
        if self._usuario_repository is None:
            self._usuario_repository = UsuarioRepositoryMock(self.data_source)
        return self._usuario_repository
    
    @property
    def catalogo_repository(self) -> CatalogoRepositoryInterface:
        """Get the catalogo repository instance"""
        if self._catalogo_repository is None:
            self._catalogo_repository = CatalogoRepositoryMock(self.data_source)
        return self._catalogo_repository
    
    @property
    def usuario_service(self) -> UsuarioService:
        """Get the usuario service instance"""
        if self._usuario_service is None:
            self._usuario_service = UsuarioService(self.usuario_repository)
        return self._usuario_service
    
    @property
    def catalogo_service(self) -> CatalogoService:
        """Get the catalogo service instance"""
        if self._catalogo_service is None:
            self._catalogo_service = CatalogoService(self.catalogo_repository)
        return self._catalogo_service

    @property
    def aluguel_service(self) -> AluguelService:
        """Get the aluguel service instance"""
        if self._aluguel_service is None:
            self._aluguel_service = AluguelService(
                self.data_source, self.catalogo_service,
            )
        return self._aluguel_service

    def reset(self) -> None:
        """Reset all instances (useful for testing)"""
        self._data_source = None
        self._usuario_repository = None
        self._catalogo_repository = None
        self._usuario_service = None
        self._catalogo_service = None
        self._aluguel_service = None


# Global container instance
container = Container()
