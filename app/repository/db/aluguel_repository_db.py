from typing import List, Optional
from app.models import Aluguel, ItemTransacao, Exemplar, Multa, Comprovante
from app.repository.interface.aluguel_repository_interface import AluguelRepositoryInterface
from app.models import Venda, MidiaDigital, MidiaFisica
from app.database.interfaces.data_source_interface import DataSourceInterface

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

    def find_exemplar_disponivel(self, id_catalogo: int, tipo_midia: str) -> Optional[Exemplar]:
        # Simplified logic using DataSourceInterface
        exemplares = self.data_source.get_all(Exemplar)
        alugueis = self.data_source.get_all(Aluguel)
        vendas = self.data_source.get_all(Venda)
        itens_transacao = self.data_source.get_all(ItemTransacao)
        
        # Get occupied exemplar IDs from active rentals
        alugueis_ativos_ids = {a.id for a in alugueis if a.status in ['ATIVO', 'ATRASADO', 'SOLICITADO', 'APROVADO']}
        vendas_ids = {v.id for v in vendas if v.status == 'FINALIZADA'}
        
        # Get exemplar IDs that are in transactions
        exemplares_indisponiveis = set()
        for item in itens_transacao:
            if item.id_transacao in alugueis_ativos_ids or item.id_transacao in vendas_ids:
                exemplares_indisponiveis.add(item.id_exemplar)
        
        # Filter exemplares by catalog and availability
        for exemplar in exemplares:
            if (exemplar.id_catalogo == id_catalogo and 
                exemplar.id not in exemplares_indisponiveis and
                (exemplar.situacao is None or exemplar.situacao == 'DISPONIVEL')):
                
                # Check if it has the right media type
                if tipo_midia == 'DIGITAL' and exemplar.tipo_midia == 'DIGITAL':
                    return exemplar
                elif tipo_midia == 'FISICA' and exemplar.tipo_midia == 'FISICA':
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
