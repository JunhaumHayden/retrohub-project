from typing import List, Optional

from app.models import Usuario, Cliente, Funcionario, Venda, Aluguel
from app.models.transacao.avaliacao import Avaliacao
from app.repository.interface.usuario_repository_interface import UsuarioRepositoryInterface
from app.database.interfaces.data_source_interface import DataSourceInterface


class UsuarioRepositoryDB(UsuarioRepositoryInterface):
    """
    Implementação concreta do repositório de Usuário para banco de dados real (via DataSourceInterface).
    """

    def __init__(self, data_source: DataSourceInterface):
        self.data_source = data_source

    def list_all(self) -> List[Usuario]:
        usuarios = []
        usuarios.extend(self.data_source.get_all(Cliente))
        usuarios.extend(self.data_source.get_all(Funcionario))
        return usuarios

    def list_clientes(self) -> List[Cliente]:
        return self.data_source.get_all(Cliente)

    def list_funcionarios(self) -> List[Funcionario]:
        return self.data_source.get_all(Funcionario)

    def get_by_id(self, id: int) -> Optional[Usuario]:
        # Tenta buscar em Cliente e depois em Funcionario para abranger todos os usuários
        usuario = self.data_source.get_by_id(Cliente, id)
        if usuario:
            return usuario
        return self.data_source.get_by_id(Funcionario, id)

    def get_cliente_by_id(self, id: int) -> Optional[Cliente]:
        return self.data_source.get_by_id(Cliente, id)

    def get_funcionario_by_id(self, id: int) -> Optional[Funcionario]:
        return self.data_source.get_by_id(Funcionario, id)

    def get_by_user(self, usuario: Usuario) -> Optional[Usuario]:
        if hasattr(usuario, 'cpf') and usuario.cpf:
            return self.data_source.get_by_field(Usuario, 'cpf', usuario.cpf)
        if hasattr(usuario, 'email') and usuario.email:
            return self.data_source.get_by_field(Usuario, 'email', usuario.email)
        return None

    def get_by_email(self, email: str) -> Optional[Usuario]:
        # Try Cliente first
        result = self.data_source.get_by_field(Cliente, 'email', email)
        if result:
            return result
        # Try Funcionario
        return self.data_source.get_by_field(Funcionario, 'email', email)

    def get_by_cpf(self, cpf: str) -> Optional[Usuario]:
        # Try Cliente first
        result = self.data_source.get_by_field(Cliente, 'cpf', cpf)
        if result:
            return result
        # Try Funcionario
        return self.data_source.get_by_field(Funcionario, 'cpf', cpf)

    def get_cliente_by_cpf(self, cpf: str) -> Optional[Cliente]:
        return self.data_source.get_by_field(Cliente, 'cpf', cpf)

    def get_funcionario_by_matricula(self, matricula: str) -> Optional[Funcionario]:
        return self.data_source.get_by_field(Funcionario, 'matricula', matricula)

    def create(self, usuario: Usuario) -> Optional[Usuario]:
        return self.data_source.create(usuario)

    def update(self, usuario: Usuario) -> Optional[Usuario]:
        return self.data_source.update(usuario)

    def delete(self, usuario: Usuario) -> bool:
        if usuario:
            return self.data_source.delete(type(usuario), usuario.id)
        return False

    def get_transacao_by_id(self, id_transacao: int):
        transacao = self.data_source.get_by_id(Venda, id_transacao)
        if transacao:
            return transacao
        return self.data_source.get_by_id(Aluguel, id_transacao)

    def create_avaliacao(self, avaliacao: Avaliacao) -> Optional[Avaliacao]:
        return self.data_source.create(avaliacao)

    def get_avaliacoes_by_cliente(self, id_cliente: int) -> List[Avaliacao]:
        avaliacoes = self.data_source.get_all(Avaliacao)
        result = []
        for avaliacao in avaliacoes:
            transacao = self.get_transacao_by_id(avaliacao.id_transacao)
            if transacao and getattr(transacao, "id_cliente", None) == id_cliente:
                result.append(avaliacao)
        return result
