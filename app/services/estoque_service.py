from datetime import datetime
from typing import List, Optional

from app.models.estoque.exemplar import Exemplar
from app.models.estoque.midia_fisica import MidiaFisica
from app.models.estoque.midia_digital import MidiaDigital
from app.models.catalogo.catalogo import Catalogo
from app.repository.interface.estoque_repository_interface import EstoqueRepositoryInterface
from app.repository.interface.catalogo_repository_interface import CatalogoRepositoryInterface


class EstoqueService:
    """
    Service layer for Estoque operations
    Handles business logic for inventory management
    """

    def __init__(
        self,
        estoque_repository: EstoqueRepositoryInterface,
        catalogo_repository: CatalogoRepositoryInterface
    ):
        self.estoque_repository = estoque_repository
        self.catalogo_repository = catalogo_repository

    def get_exemplar_by_id(self, id: int) -> Optional[Exemplar]:
        """Get exemplar by ID"""
        return self.estoque_repository.get_exemplar_by_id(id)

    def get_exemplares_by_catalogo(self, catalogo_id: int) -> List[Exemplar]:
        """Get all exemplares for a specific catalogo"""
        return self.estoque_repository.get_exemplares_by_catalogo(catalogo_id)

    def create_midia_fisica(
        self,
        id_catalogo: int,
        codigo_barras: str,
        estado_conservacao: str
    ) -> tuple[Optional[MidiaFisica], Optional[str]]:
        """
        Create a new MidiaFisica
        Returns (midia, error_message)
        """
        # Validate catalogo exists
        catalogo = self.catalogo_repository.get_by_id(id_catalogo)
        if not catalogo:
            return None, "Jogo não encontrado no catálogo."

        # Check for duplicate codigo_barras
        existing = self.estoque_repository.get_midia_fisica_by_codigo_barras(codigo_barras)
        if existing:
            return None, f"O código de barras '{codigo_barras}' já está cadastrado."

        # Create midia fisica
        nova_midia = MidiaFisica(
            id_catalogo=id_catalogo,
            codigo_barras=codigo_barras,
            estado_conservacao=estado_conservacao
        )

        midia_criada = self.estoque_repository.create_midia_fisica(nova_midia)
        return midia_criada, None

    def create_midia_digital(
        self,
        id_catalogo: int,
        chave_ativacao: str,
        data_expiracao: Optional[datetime] = None
    ) -> tuple[Optional[MidiaDigital], Optional[str]]:
        """
        Create a new MidiaDigital
        Returns (midia, error_message)
        """
        # Validate catalogo exists
        catalogo = self.catalogo_repository.get_by_id(id_catalogo)
        if not catalogo:
            return None, "Jogo não encontrado no catálogo."

        # Check for duplicate chave_ativacao
        existing = self.estoque_repository.get_midia_digital_by_chave(chave_ativacao)
        if existing:
            return None, "Esta chave de ativação já está cadastrada."

        # Create midia digital
        nova_midia = MidiaDigital(
            id_catalogo=id_catalogo,
            chave_ativacao=chave_ativacao,
            data_expiracao=data_expiracao
        )

        midia_criada = self.estoque_repository.create_midia_digital(nova_midia)
        return midia_criada, None

    def update_estado_conservacao(
        self,
        midia_id: int,
        novo_estado: str
    ) -> tuple[Optional[MidiaFisica], Optional[str]]:
        """
        Update the conservation state of a MidiaFisica
        Returns (midia, error_message)
        """
        midia = self.estoque_repository.get_exemplar_by_id(midia_id)
        if not midia:
            return None, "Exemplar não encontrado."

        if not isinstance(midia, MidiaFisica):
            return None, "Este exemplar não é uma mídia física."

        midia.estado_conservacao = novo_estado
        midia_atualizada = self.estoque_repository.update_midia_fisica(midia)
        return midia_atualizada, None

    def delete_exemplar(self, exemplar_id: int) -> tuple[bool, Optional[str]]:
        """
        Delete an exemplar from inventory
        Returns (success, error_message)
        """
        exemplar = self.estoque_repository.get_exemplar_by_id(exemplar_id)
        if not exemplar:
            return False, "Exemplar não encontrado."

        success = self.estoque_repository.delete_exemplar(exemplar)
        if not success:
            return False, "Não é possível excluir este exemplar pois existem transações atreladas a ele."

        return True, None

    def serialize_exemplar(self, exemplar: Exemplar) -> dict:
        """Serialize exemplar to dict based on its type"""
        base_data = {
            "id": exemplar.id,
            "id_catalogo": exemplar.id_catalogo,
            "tipo_midia": exemplar.tipo_midia
        }

        if isinstance(exemplar, MidiaFisica):
            base_data.update({
                "codigo_barras": exemplar.codigo_barras,
                "estado_conservacao": exemplar.estado_conservacao
            })
        elif isinstance(exemplar, MidiaDigital):
            base_data.update({
                "chave_ativacao": exemplar.chave_ativacao,
                "data_expiracao": exemplar.data_expiracao.isoformat() if exemplar.data_expiracao else None
            })

        return base_data
