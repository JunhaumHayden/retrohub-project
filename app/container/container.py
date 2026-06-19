"""
Dependency Injection Container
Manages the creation and lifecycle of application components
"""

from typing import Optional

from app.database.factories.database_manager import DatabaseManager
from app.database.interfaces.data_source_interface import DataSourceInterface
from app.database.adapters.mock_adapter import MockDataSource

# Interfaces
from app.repository.interface.usuario_repository_interface import UsuarioRepositoryInterface
from app.repository.interface.catalogo_repository_interface import CatalogoRepositoryInterface
# from app.repository.interface.aluguel_repository_interface import AluguelRepositoryInterface

# Implementações
from app.repository.mock.usuario_repository_mock import UsuarioRepositoryMock
from app.repository.mock.catalogo_repository_mock import CatalogoRepositoryMock
from app.repository.mock.aluguel_repository_mock import AluguelRepositoryMock
from app.repository.db.usuario_repository_db import UsuarioRepositoryDB
from app.repository.db.catalogo_repository_db import CatalogoRepositoryDB
# from app.repository.db.aluguel_repository_db import AluguelRepositoryDB

# Services
from app.services.usuario_service import UsuarioService
from app.services.catalogo_service import CatalogoService
from app.services.aluguel_service import AluguelService


class Container:
    """
    Dependency injection container for the application.
    It retrieves the DataSource from the DatabaseManager and then injects
    the correct repository implementation into the services.
    """
    
    def __init__(self):
        self._data_source: Optional[DataSourceInterface] = None
        self._usuario_repository: Optional[UsuarioRepositoryInterface] = None
        self._catalogo_repository: Optional[CatalogoRepositoryInterface] = None
        self._aluguel_repository: Optional[AluguelRepositoryMock] = None # TODO: Use interface
        self._usuario_service: Optional[UsuarioService] = None
        self._catalogo_service: Optional[CatalogoService] = None
        self._aluguel_service: Optional[AluguelService] = None
    
    @property
    def data_source(self) -> DataSourceInterface:
        """Get the data source instance from the central factory."""
        if self._data_source is None:
            self._data_source = DatabaseManager.get_data_source()
        return self._data_source
    
    @property
    def usuario_repository(self) -> UsuarioRepositoryInterface:
        if self._usuario_repository is None:
            if isinstance(self.data_source, MockDataSource):
                self._usuario_repository = UsuarioRepositoryMock(self.data_source)
            else:
                # self._usuario_repository = UsuarioRepositoryDB(self.data_source) # Assuming DB source provides a session
                raise NotImplementedError("UsuarioRepositoryDB not fully integrated yet.")
        return self._usuario_repository
    
    @property
    def catalogo_repository(self) -> CatalogoRepositoryInterface:
        if self._catalogo_repository is None:
            if isinstance(self.data_source, MockDataSource):
                self._catalogo_repository = CatalogoRepositoryMock(self.data_source)
            else:
                # self._catalogo_repository = CatalogoRepositoryDB(self.data_source)
                raise NotImplementedError("CatalogoRepositoryDB not fully integrated yet.")
        return self._catalogo_repository

    @property
    def aluguel_repository(self) -> AluguelRepositoryMock: # TODO: Use interface
        if self._aluguel_repository is None:
            if isinstance(self.data_source, MockDataSource):
                self._aluguel_repository = AluguelRepositoryMock(self.data_source)
            else:
                # self._aluguel_repository = AluguelRepositoryDB(self.data_source)
                raise NotImplementedError("AluguelRepositoryDB not fully integrated yet.")
        return self._aluguel_repository
    
    @property
    def usuario_service(self) -> UsuarioService:
        if self._usuario_service is None:
            self._usuario_service = UsuarioService(self.usuario_repository)
        return self._usuario_service
    
    @property
    def catalogo_service(self) -> CatalogoService:
        if self._catalogo_service is None:
            self._catalogo_service = CatalogoService(self.catalogo_repository)
        return self._catalogo_service

    @property
    def aluguel_service(self) -> AluguelService:
        if self._aluguel_service is None:
            self._aluguel_service = AluguelService(self.aluguel_repository)
        return self._aluguel_service
    
    def reset(self) -> None:
        """Resets the container and the underlying data source factory."""
        DatabaseManager.reset_data_source()
        self._data_source = None
        self._usuario_repository = None
        self._catalogo_repository = None
        self._aluguel_repository = None
        self._usuario_service = None
        self._catalogo_service = None
        self._aluguel_service = None


container = Container()
