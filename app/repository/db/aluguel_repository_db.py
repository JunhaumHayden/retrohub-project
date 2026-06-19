from typing import List, Optional
from app.models import Aluguel, ItemTransacao, Exemplar, Multa, Comprovante
from app.repository.interface.aluguel_repository_interface import AluguelRepositoryInterface
from app.models import Venda, MidiaDigital, MidiaFisica

class AluguelRepositoryDB(AluguelRepositoryInterface):
    """
    Implementação concreta do repositório de Aluguel para banco de dados real (via SQLAlchemy).
    """

    def __init__(self, session):
        self.session = session

    def get_by_id(self, id: int) -> Optional[Aluguel]:
        return self.session.query(Aluguel).filter(Aluguel.id == id).first()

    def get_items_by_transacao(self, transacao_id: int) -> List[ItemTransacao]:
        return self.session.query(ItemTransacao).filter(ItemTransacao.id_transacao == transacao_id).all()

    def get_exemplar_by_id(self, exemplar_id: int) -> Optional[Exemplar]:
        return self.session.query(Exemplar).filter(Exemplar.id == exemplar_id).first()

    def find_exemplar_disponivel(self, id_catalogo: int, tipo_midia: str) -> Optional[Exemplar]:
        # Logica complexa que envolveria joins e subqueries no SQLAlchemy
        # Simplificada aqui para não criar dependencias pesadas no momento
        
        # Subquery para encontrar IDs de exemplares em transações ativas
        alugueis_ativos = self.session.query(Aluguel.id).filter(Aluguel.status.in_(['ATIVO', 'ATRASADO', 'SOLICITADO', 'APROVADO'])).subquery()
        vendas_finalizadas = self.session.query(Venda.id).filter(Venda.status == 'FINALIZADA').subquery()
        
        itens_indisponiveis_aluguel = self.session.query(ItemTransacao.id_exemplar).filter(ItemTransacao.id_transacao.in_(alugueis_ativos))
        itens_indisponiveis_venda = self.session.query(ItemTransacao.id_exemplar).filter(ItemTransacao.id_transacao.in_(vendas_finalizadas))
        
        indisponiveis = itens_indisponiveis_aluguel.union(itens_indisponiveis_venda).subquery()

        # Query principal
        query = self.session.query(Exemplar).filter(
            Exemplar.id_catalogo == id_catalogo,
            Exemplar.id.not_in(indisponiveis),
            (Exemplar.situacao == None) | (Exemplar.situacao == 'DISPONIVEL')
        )
        
        if tipo_midia == 'DIGITAL':
            query = query.filter(Exemplar.tipo_midia == 'DIGITAL')
        elif tipo_midia == 'FISICA':
             query = query.filter(Exemplar.tipo_midia == 'FISICA')
             
        return query.first()

    def create_aluguel(self, aluguel: Aluguel) -> Aluguel:
        self.session.add(aluguel)
        self.session.commit()
        return aluguel

    def create_item_transacao(self, item_transacao: ItemTransacao) -> ItemTransacao:
        self.session.add(item_transacao)
        self.session.commit()
        return item_transacao

    def create_multa(self, multa: Multa) -> Multa:
        self.session.add(multa)
        self.session.commit()
        return multa

    def create_comprovante(self, comprovante: Comprovante) -> Comprovante:
        self.session.add(comprovante)
        self.session.commit()
        return comprovante

    def update(self, entity) -> Optional[any]:
        self.session.add(entity)
        self.session.commit()
        return entity
