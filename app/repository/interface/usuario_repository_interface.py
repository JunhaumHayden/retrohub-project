from abc import ABC, abstractmethod
from typing import List, Optional

from app.models import Usuario, Cliente, Funcionario


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
    def get_by_email(self, email: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def get_by_cpf(self, cpf: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def list_clientes(self) -> List[Cliente]:
        pass

    @abstractmethod
    def list_funcionarios(self) -> List[Funcionario]:
        pass

    @abstractmethod
    def get_cliente_by_id(self, id: int) -> Optional[Cliente]:
        pass

    @abstractmethod
    def get_funcionario_by_id(self, id: int) -> Optional[Funcionario]:
        pass

    @abstractmethod
    def get_cliente_by_cpf(self, cpf: str) -> Optional[Cliente]:
        pass

    @abstractmethod
    def get_funcionario_by_matricula(self, matricula: str) -> Optional[Funcionario]:
        pass

    @abstractmethod
    def create(self, usuario: Usuario) -> Optional[Usuario]:
        pass

    @abstractmethod
    def update(self, usuario: Usuario) -> Optional[Usuario]:
        pass

    @abstractmethod
    def delete(self, usuario: Usuario) -> bool:
        pass