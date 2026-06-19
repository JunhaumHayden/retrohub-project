"""
Dependency Injection Container
Manages the creation and lifecycle of application components
"""

from typing import Optional

from app.database.factories.database_factory import DatabaseFactory
from app.database.interfaces.data_source_interface import DataSourceInterface
from app.database.data_source.MockDataSource import MockDataSource

# Interfaces
from app.repository.interface.usuario_repository_interface import UsuarioRepositoryInterface
from app.repository.interface.catalogo_repository_interface import CatalogoRepositoryInterface
from app.repository.interface.aluguel_repository_interface import AluguelRepositoryInterface
from app.repository.interface.venda_repository_interface import VendaRepositoryInterface
from app.repository.interface.estoque_repository_interface import EstoqueRepositoryInterface

# Implementações
from app.repository.mock.usuario_repository_mock import UsuarioRepositoryMock
from app.repository.mock.catalogo_repository_mock import CatalogoRepositoryMock
from app.repository.mock.aluguel_repository_mock import AluguelRepositoryMock
from app.repository.mock.venda_repository_mock import VendaRepositoryMock
from app.repository.mock.estoque_repository_mock import EstoqueRepositoryMock
from app.repository.db.usuario_repository_db import UsuarioRepositoryDB
from app.repository.db.catalogo_repository_db import CatalogoRepositoryDB
from app.repository.db.aluguel_repository_db import AluguelRepositoryDB
from app.repository.db.venda_repository_db import VendaRepositoryDB
from app.repository.db.estoque_repository_db import EstoqueRepositoryDB

# Services
from app.services.usuario_service import UsuarioService
from app.services.catalogo_service import CatalogoService
from app.services.aluguel_service import AluguelService
from app.services.venda_service import VendaService
from app.services.estoque_service import EstoqueService


class Container:
    """
    Dependency injection container for the application.
    It retrieves the DataSource from the DatabaseFactory and then injects
    the correct repository implementation into the services.
    """
    
    def __init__(self):
        self._data_source: Optional[DataSourceInterface] = None
        self._usuario_repository: Optional[UsuarioRepositoryInterface] = None
        self._catalogo_repository: Optional[CatalogoRepositoryInterface] = None
        self._aluguel_repository: Optional[AluguelRepositoryInterface] = None
        self._venda_repository: Optional[VendaRepositoryInterface] = None
        self._estoque_repository: Optional[EstoqueRepositoryInterface] = None
        self._usuario_service: Optional[UsuarioService] = None
        self._catalogo_service: Optional[CatalogoService] = None
        self._aluguel_service: Optional[AluguelService] = None
        self._venda_service: Optional[VendaService] = None
        self._estoque_service: Optional[EstoqueService] = None
    
    @property
    def data_source(self) -> DataSourceInterface:
        """Get the data source instance from the central factory."""
        if self._data_source is None:
            self._data_source = DatabaseFactory.get_data_source()
        return self._data_source
    
    @property
    def usuario_repository(self) -> UsuarioRepositoryInterface:
        if self._usuario_repository is None:
            if isinstance(self.data_source, MockDataSource):
                self._usuario_repository = UsuarioRepositoryMock(self.data_source)
            else:
                self._usuario_repository = UsuarioRepositoryDB(self.data_source)
        return self._usuario_repository
    
    @property
    def catalogo_repository(self) -> CatalogoRepositoryInterface:
        if self._catalogo_repository is None:
            if isinstance(self.data_source, MockDataSource):
                self._catalogo_repository = CatalogoRepositoryMock(self.data_source)
            else:
                self._catalogo_repository = CatalogoRepositoryDB(self.data_source)
        return self._catalogo_repository

    @property
    def aluguel_repository(self) -> AluguelRepositoryInterface:
        if self._aluguel_repository is None:
            if isinstance(self.data_source, MockDataSource):
                self._aluguel_repository = AluguelRepositoryMock(self.data_source)
            else:
                self._aluguel_repository = AluguelRepositoryDB(self.data_source)
        return self._aluguel_repository

    @property
    def venda_repository(self) -> VendaRepositoryInterface:
        if self._venda_repository is None:
            if isinstance(self.data_source, MockDataSource):
                self._venda_repository = VendaRepositoryMock(self.data_source)
            else:
                self._venda_repository = VendaRepositoryDB(self.data_source)
        return self._venda_repository

    @property
    def estoque_repository(self) -> EstoqueRepositoryInterface:
        if self._estoque_repository is None:
            if isinstance(self.data_source, MockDataSource):
                self._estoque_repository = EstoqueRepositoryMock(self.data_source)
            else:
                self._estoque_repository = EstoqueRepositoryDB(self.data_source)
        return self._estoque_repository
    
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

    @property
    def venda_service(self) -> VendaService:
        if self._venda_service is None:
            self._venda_service = VendaService(
                self.venda_repository,
                self.estoque_repository,
                self.catalogo_repository
            )
        return self._venda_service

    @property
    def estoque_service(self) -> EstoqueService:
        if self._estoque_service is None:
            self._estoque_service = EstoqueService(
                self.estoque_repository,
                self.catalogo_repository
            )
        return self._estoque_service
    
    def reset(self) -> None:
        """Resets the container and the underlying data source factory."""
        DatabaseFactory.reset_data_source()
        self._data_source = None
        self._usuario_repository = None
        self._catalogo_repository = None
        self._aluguel_repository = None
        self._venda_repository = None
        self._estoque_repository = None
        self._usuario_service = None
        self._catalogo_service = None
        self._aluguel_service = None
        self._venda_service = None
        self._estoque_service = None


container = Container()
