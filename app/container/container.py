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

# Implementações
from app.repository.mock.usuario_repository_mock import UsuarioRepositoryMock
from app.repository.mock.catalogo_repository_mock import CatalogoRepositoryMock
from app.repository.mock.aluguel_repository_mock import AluguelRepositoryMock
from app.repository.db.usuario_repository_db import UsuarioRepositoryDB
from app.repository.db.catalogo_repository_db import CatalogoRepositoryDB
from app.repository.db.aluguel_repository_db import AluguelRepositoryDB
from app.repository.db.venda_repository_db import VendaRepositoryDB
from app.repository.db.estoque_repository_db import EstoqueRepositoryDB

# Services
from app.services.usuario_service import UsuarioService
from app.services.catalogo_service import CatalogoService
from app.services.aluguel_service import AluguelService
from app.services.estoque_service import EstoqueService
from app.services.venda_service import VendaService
from app.services.relatorio_service import RelatorioService
from app.services.avaliacao_service import AvaliacaoService


class Container:
    """
    Dependency injection container for the application.
    """
    
    def __init__(self):
        self._data_source: Optional[DataSourceInterface] = None
        self._usuario_repository: Optional[UsuarioRepositoryInterface] = None
        self._catalogo_repository: Optional[CatalogoRepositoryInterface] = None
        self._aluguel_repository: Optional[AluguelRepositoryInterface] = None
        self._venda_repository: Optional[VendaRepositoryDB] = None
        self._usuario_service: Optional[UsuarioService] = None
        self._catalogo_service: Optional[CatalogoService] = None
        self._aluguel_service: Optional[AluguelService] = None
        self._estoque_service: Optional[EstoqueService] = None
        self._venda_service: Optional[VendaService] = None
        self._relatorio_service: Optional[RelatorioService] = None
        self._avaliacao_service: Optional[AvaliacaoService] = None

    @property
    def data_source(self) -> DataSourceInterface:
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
    def estoque_service(self) -> EstoqueService:
        if self._estoque_service is None:
            # O EstoqueService pode reutilizar o catalogo_repository, pois ambos precisam de acesso ao DataSource
            self._estoque_service = EstoqueService(self.catalogo_repository)
        return self._estoque_service

    @property
    def venda_repository(self):
        if self._venda_repository is None:
            # database-backed venda repository
            self._venda_repository = VendaRepositoryDB(self.data_source)
        return self._venda_repository

    @property
    def venda_service(self) -> VendaService:
        if self._venda_service is None:
            # VendaService depends on venda_repository, estoque_repository and catalogo_repository
            estoque_repo = EstoqueRepositoryDB(self.data_source)
            self._venda_service = VendaService(self.venda_repository, estoque_repo, self.catalogo_repository)
        return self._venda_service

    @property
    def relatorio_service(self) -> RelatorioService:
        if self._relatorio_service is None:
            self._relatorio_service = RelatorioService(self.catalogo_repository)
        return self._relatorio_service

    @property
    def avaliacao_service(self) -> AvaliacaoService:
        if self._avaliacao_service is None:
            self._avaliacao_service = AvaliacaoService(self.usuario_repository, self.catalogo_repository)
        return self._avaliacao_service

    def reset(self) -> None:
        """Resets the container and the underlying data source factory."""
        DatabaseFactory.reset_data_source()
        self._data_source = None
        self._usuario_repository = None
        self._catalogo_repository = None
        self._aluguel_repository = None
        self._usuario_service = None
        self._catalogo_service = None
        self._aluguel_service = None
        self._estoque_service = None
        self._venda_service = None
        self._relatorio_service = None
        self._avaliacao_service = None


container = Container()
