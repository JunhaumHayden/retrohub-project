from typing import Any, List, Optional

from app.database.mock_data_source import MockDataSource
from app.database.interfaces.data_source_interface import DataSourceInterface
from app.models import Aluguel, ItemTransacao, Exemplar, Catalogo, Multa, Comprovante


class AluguelRepositoryMock:
    """Mock repository para operacões de Aluguel usando MockDataSource em uma lista em memória e a abordagem "Lazy Loading"."""

    def __init__(self, data_source: Optional[DataSourceInterface] = None):
        # Accept any DataSourceInterface implementation
        self.data_source = data_source or MockDataSource()
        # Ensure data is loaded
        if hasattr(self.data_source, 'load_data'):
            self.data_source.load_data()

    def get_by_id(self, id: int) -> Optional[Aluguel]:
        return self.data_source.get_by_id(Aluguel, id)

    def update(self, entity: Any) -> Optional[Any]:
        return self.data_source.update(entity)

    def get_items_by_transacao(self, transacao_id: int) -> List[ItemTransacao]:
        items = self.data_source.get_all(ItemTransacao)
        return [i for i in items if i.id_transacao == transacao_id]

    def get_exemplar_by_id(self, exemplar_id: int) -> Optional[Exemplar]:
        return self.data_source.get_by_id(Exemplar, exemplar_id)

    def get_catalogo_by_id(self, catalogo_id: int) -> Optional[Catalogo]:
        return self.data_source.get_by_id(Catalogo, catalogo_id)

    def find_exemplar_disponivel(self, id_catalogo: int, tipo_midia: str) -> Optional[Exemplar]:
        """Finds an available exemplar for a given catalog and media type."""
        exemplares = self.data_source.get_all(Exemplar)
        alugueis = self.data_source.get_all(Aluguel)
        from app.models import Venda # Local import to avoid circular dependency
        vendas = self.data_source.get_all(Venda)
        itens_transacao = self.data_source.get_all(ItemTransacao)
        
        alugueis_ativos_ids = {a.id for a in alugueis if a.status in ['ATIVO', 'ATRASADO', 'SOLICITADO', 'APROVADO']}
        vendas_ids = {v.id for v in vendas if getattr(v, 'status', None) == 'FINALIZADA'}
        
        exemplares_indisponiveis = {
            item.id_exemplar for item in itens_transacao 
            if item.id_transacao in alugueis_ativos_ids or item.id_transacao in vendas_ids
        }
        
        for exemplar in exemplares:
            if (exemplar.id_catalogo == id_catalogo and 
                exemplar.id not in exemplares_indisponiveis and
                (exemplar.situacao is None or exemplar.situacao == 'DISPONIVEL')):
                
                from app.models import MidiaDigital, MidiaFisica
                if tipo_midia == 'DIGITAL' and isinstance(exemplar, MidiaDigital):
                    return exemplar
                if tipo_midia == 'FISICA' and isinstance(exemplar, MidiaFisica):
                    return exemplar
        return None

    def create_aluguel(self, aluguel: Aluguel) -> Aluguel:
        return self.data_source.create(aluguel)

    def create_item_transacao(self, item_transacao: ItemTransacao) -> ItemTransacao:
        return self.data_source.create(item_transacao)

    def create_multa(self, multa: Multa) -> Multa:
        return self.data_source.create(multa)

    def create_comprovante(self, comprovante: Comprovante) -> Comprovante:
        return self.data_source.create(comprovante)
