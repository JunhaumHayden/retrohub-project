from typing import List, Optional
from datetime import date, datetime

from app.models import Exemplar, Venda, Aluguel
from app.models.catalogo.catalogo import Catalogo
from app.models.transacao.avaliacao import Avaliacao
from app.models.transacao.item_transacao import ItemTransacao
from app.repository.interface.catalogo_repository_interface import CatalogoRepositoryInterface
from app.database.interfaces.data_source_interface import DataSourceInterface

class CatalogoRepositoryDB(CatalogoRepositoryInterface):
    """
    Implementação concreta do repositório de Catálogo para banco de dados real (via DataSourceInterface).
    """

    def __init__(self, data_source: DataSourceInterface):
        self.data_source = data_source

    def list_all(self) -> List[Catalogo]:
        return self.data_source.get_all(Catalogo)

    def get_by_id(self, id: int) -> Optional[Catalogo]:
        return self.data_source.get_by_id(Catalogo, id)

    def get_by_title(self, title: str) -> Optional[Catalogo]:
        return self.data_source.get_by_field(Catalogo, 'titulo', title)

    def create(self, catalogo: Catalogo) -> Optional[Catalogo]:
        return self.data_source.create(catalogo)

    def update(self, catalogo: Catalogo) -> Optional[Catalogo]:
        return self.data_source.update(catalogo)

    def delete(self, id: int) -> bool:
        return self.data_source.delete(Catalogo, id)

    def get_by_genero(self, genero: str) -> List[Catalogo]:
        return [c for c in self.data_source.get_all(Catalogo) if c.genero == genero]

    def get_by_situacao(self, situacao: str) -> List[Catalogo]:
        return [c for c in self.data_source.get_all(Catalogo) if c.situacao == situacao]

    def add_exemplar(self, exemplar: Exemplar) -> Optional[Exemplar]:
        return self.data_source.add_exemplar(exemplar)

    def _in_period(self, data_transacao, data_inicio: Optional[date], data_fim: Optional[date]) -> bool:
        if data_transacao is None:
            return data_inicio is None and data_fim is None
        dt = data_transacao.date() if isinstance(data_transacao, datetime) else data_transacao
        if data_inicio and dt < data_inicio:
            return False
        if data_fim and dt > data_fim:
            return False
        return True

    def get_vendas_por_periodo(self, data_inicio: Optional[date] = None, data_fim: Optional[date] = None) -> List[Venda]:
        vendas = self.data_source.get_all(Venda)
        return [v for v in vendas if self._in_period(v.data_transacao, data_inicio, data_fim)]

    def get_alugueis_por_periodo(self, data_inicio: Optional[date] = None, data_fim: Optional[date] = None) -> List[Aluguel]:
        alugueis = self.data_source.get_all(Aluguel)
        return [a for a in alugueis if self._in_period(a.data_transacao, data_inicio, data_fim)]

    def get_avaliacoes_by_jogo(self, id_catalogo: int) -> List[Avaliacao]:
        avaliacoes = self.data_source.get_all(Avaliacao)
        itens = self.data_source.get_all(ItemTransacao)
        transacao_ids = {
            item.id_transacao
            for item in itens
            if item.id_exemplar is not None and self._exemplar_belongs_to_catalogo(item.id_exemplar, id_catalogo)
        }
        return [a for a in avaliacoes if a.id_transacao in transacao_ids]

    def _exemplar_belongs_to_catalogo(self, exemplar_id: int, catalogo_id: int) -> bool:
        from app.models.estoque.midia_fisica import MidiaFisica
        from app.models.estoque.midia_digital import MidiaDigital

        exemplar = self.data_source.get_by_id(MidiaFisica, exemplar_id)
        if exemplar is None:
            exemplar = self.data_source.get_by_id(MidiaDigital, exemplar_id)
        return exemplar is not None and getattr(exemplar, "id_catalogo", None) == catalogo_id
