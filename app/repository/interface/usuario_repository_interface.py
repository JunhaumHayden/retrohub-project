from abc import ABC, abstractmethod
from typing import List, Optional

from flask_restx.fields import Boolean

from app.models import Usuario


class UsuarioRepositoryInterface(ABC):
    """
    Camada de repositório para Usuario
    Responsável por todas as operações de banco de dados
    Essa camada é quem sabe como inserir e recuperar um objeto no banco de dados
    """

    @abstractmethod
    def list_all(self) -> List[Usuario]:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Usuario]:
        pass

    @abstractmethod
    def get_by_user(self, usuario: Usuario) -> Optional[Usuario]:
        pass

    @abstractmethod
    def create(self, usuario: Usuario) -> Optional[Usuario]:
        pass

    @abstractmethod
    def update(self, usuario: Usuario) -> Optional[Usuario]:
        pass

    @abstractmethod
    def delete(self, usuario: Usuario) -> Boolean:
        pass