from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple

from app.models import Exemplar
from app.models.catalogo.catalogo import Catalogo
from app.models.estoque.midia_fisica import MidiaFisica
from app.models.estoque.midia_digital import MidiaDigital
from app.models.enums import StatusSituacao
from app.repository.interface.catalogo_repository_interface import CatalogoRepositoryInterface
from app.repository.db.estoque_repository_db import EstoqueRepositoryDB

DEFAULT_VALOR_VENDA = Decimal("49.99")
DEFAULT_VALOR_DIARIA = Decimal("5.99")


def _enum_to_str(value):
    if value is None:
        return None
    return getattr(value, "value", getattr(value, "name", value))


class EstoqueService:
    """Service layer for Estoque (Exemplar) operations."""

    def __init__(self, repository: CatalogoRepositoryInterface):
        self.repository = repository
        self._estoque_repo = EstoqueRepositoryDB(repository.data_source)

    def create_exemplar(self, exemplar: Exemplar) -> Exemplar:
        return self.repository.data_source.create(exemplar)

    def _get_catalogo(self, id_catalogo: int) -> Optional[Catalogo]:
        return self.repository.get_by_id(id_catalogo)

    def create_midia_fisica(
        self,
        id_catalogo: int,
        codigo_barras: str,
        estado_conservacao: str,
        valor_venda: Optional[Decimal] = None,
        valor_diaria_aluguel: Optional[Decimal] = None,
    ) -> Tuple[Optional[MidiaFisica], Optional[str]]:
        catalogo = self._get_catalogo(id_catalogo)
        if not catalogo:
            return None, "Catálogo não encontrado."

        if self._estoque_repo.get_midia_fisica_by_codigo_barras(codigo_barras):
            return None, f"Código de barras '{codigo_barras}' já cadastrado."

        midia = MidiaFisica(
            catalogo=catalogo,
            codigo_barras=codigo_barras,
            valor_venda=valor_venda or DEFAULT_VALOR_VENDA,
            valor_diaria_aluguel=valor_diaria_aluguel or DEFAULT_VALOR_DIARIA,
        )
        midia.set_estado_conservacao(estado_conservacao)

        created = self._estoque_repo.create_midia_fisica(midia)
        return created, None

    def create_midia_digital(
        self,
        id_catalogo: int,
        chave_ativacao: str,
        data_expiracao: Optional[date] = None,
        valor_venda: Optional[Decimal] = None,
        valor_diaria_aluguel: Optional[Decimal] = None,
    ) -> Tuple[Optional[MidiaDigital], Optional[str]]:
        catalogo = self._get_catalogo(id_catalogo)
        if not catalogo:
            return None, "Catálogo não encontrado."

        if self._estoque_repo.get_midia_digital_by_chave(chave_ativacao):
            return None, f"Chave de ativação '{chave_ativacao}' já cadastrada."

        midia = MidiaDigital(
            catalogo=catalogo,
            chave_ativacao=chave_ativacao,
            data_expiracao=data_expiracao,
            valor_venda=valor_venda or DEFAULT_VALOR_VENDA,
            valor_diaria_aluguel=valor_diaria_aluguel or DEFAULT_VALOR_DIARIA,
            situacao=StatusSituacao.DISPONIVEL,
        )

        created = self._estoque_repo.create_midia_digital(midia)
        return created, None

    def get_exemplar_by_id(self, exemplar_id: int) -> Optional[Exemplar]:
        return self._estoque_repo.get_exemplar_by_id(exemplar_id)

    def get_exemplares_by_catalogo(self, catalogo_id: int) -> List[Exemplar]:
        return self._estoque_repo.get_exemplares_by_catalogo(catalogo_id)

    def update_estado_conservacao(self, exemplar_id: int, estado: str):
        exemplar = self.get_exemplar_by_id(exemplar_id)
        if not exemplar:
            return None, "Exemplar não encontrado."
        if not isinstance(exemplar, MidiaFisica):
            return None, "Apenas mídias físicas possuem estado de conservação."
        exemplar.set_estado_conservacao(estado)
        updated = self.repository.data_source.update(exemplar)
        return updated, None

    def delete_exemplar(self, exemplar_id: int):
        exemplar = self.get_exemplar_by_id(exemplar_id)
        if not exemplar:
            return False, "Exemplar não encontrado."
        deleted = self._estoque_repo.delete_exemplar(exemplar)
        return deleted, None if deleted else "Não foi possível excluir o exemplar."

    def serialize_exemplar(self, exemplar: Exemplar) -> dict:
        data = {
            "id": exemplar.id,
            "id_catalogo": exemplar.id_catalogo,
            "tipo_midia": exemplar.tipo_midia,
            "situacao": _enum_to_str(exemplar.situacao),
            "valor_venda": float(exemplar.valor_venda) if exemplar.valor_venda is not None else None,
            "valor_diaria_aluguel": float(exemplar.valor_diaria_aluguel)
            if exemplar.valor_diaria_aluguel is not None
            else None,
        }
        if isinstance(exemplar, MidiaFisica):
            data["codigo_barras"] = exemplar.codigo_barras
            data["estado_conservacao"] = _enum_to_str(exemplar.estado_conservacao)
        elif isinstance(exemplar, MidiaDigital):
            data["chave_ativacao"] = exemplar.chave_ativacao
        return data
