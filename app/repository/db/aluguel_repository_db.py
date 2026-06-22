from typing import List, Optional
from app.models import Aluguel, ItemTransacao, Exemplar, Multa, Comprovante
from app.repository.interface.aluguel_repository_interface import AluguelRepositoryInterface
from app.models import Venda, MidiaDigital, MidiaFisica
from app.database.interfaces.data_source_interface import DataSourceInterface
from app.models.enums import StatusAluguel, StatusSituacao

class AluguelRepositoryDB(AluguelRepositoryInterface):
    """
    Implementação concreta do repositório de Aluguel para banco de dados real (via DataSourceInterface).
    """

    def __init__(self, data_source: DataSourceInterface):
        self.data_source = data_source

    def get_by_id(self, id: int) -> Optional[Aluguel]:
        return self.data_source.get_by_id(Aluguel, id)

    def get_items_by_transacao(self, transacao_id: int) -> List[ItemTransacao]:
        all_items = self.data_source.get_all(ItemTransacao)
        return [item for item in all_items if item.id_transacao == transacao_id]

    def get_exemplar_by_id(self, exemplar_id: int) -> Optional[Exemplar]:
        return self.data_source.get_by_id(Exemplar, exemplar_id)

    def get_catalogo_by_id(self, catalogo_id: int):
        from app.models.catalogo.catalogo import Catalogo
        return self.data_source.get_by_id(Catalogo, catalogo_id)

    def find_exemplar_disponivel(self, id_catalogo: int, tipo_midia: str) -> Optional[Exemplar]:
        # Simplified logic using DataSourceInterface
        exemplares = self.data_source.get_all(Exemplar)
        alugueis = self.data_source.get_all(Aluguel)
        vendas = self.data_source.get_all(Venda)
        itens_transacao = self.data_source.get_all(ItemTransacao)

        # Get occupied exemplar IDs from active rentals
        # Support both Enum and string values for status
        alugueis_ativos_ids = {a.id for a in alugueis if (
            getattr(a.status, 'value', a.status) in ['ATIVO', 'ATRASADO', 'SOLICITADO', 'APROVADO']
        )}
        vendas_ids = {v.id for v in vendas if (
            getattr(getattr(v, 'status', None), 'value', getattr(v, 'status', None)) == 'FINALIZADA'
        )}

        # Get exemplar IDs that are in transactions
        exemplares_indisponiveis = set()
        for item in itens_transacao:
            if item.id_transacao in alugueis_ativos_ids or item.id_transacao in vendas_ids:
                exemplares_indisponiveis.add(item.id_exemplar)

        # Filter exemplares by catalog and availability
        for exemplar in exemplares:
            situacao = getattr(exemplar, 'situacao', None)
            # Support both Enum and string values for situacao
            situacao_val = getattr(situacao, 'value', situacao) if situacao else None
            if (getattr(exemplar, 'id_catalogo', None) == id_catalogo and
                exemplar.id not in exemplares_indisponiveis and
                (situacao_val is None or situacao_val == 'DISPONIVEL')):

                # Check if it has the right media type
                if tipo_midia == 'DIGITAL' and getattr(exemplar, 'tipo_midia', None) == 'DIGITAL':
                    return exemplar
                elif tipo_midia == 'FISICA' and getattr(exemplar, 'tipo_midia', None) == 'FISICA':
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

    def update(self, entity) -> Optional[any]:
        return self.data_source.update(entity)
