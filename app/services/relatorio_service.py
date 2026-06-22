from datetime import date
from typing import List, Dict, Optional

from app.repository.interface.catalogo_repository_interface import CatalogoRepositoryInterface

class RelatorioService:
    """
    Service layer for generating reports.
    """

    def __init__(self, catalogo_repo: CatalogoRepositoryInterface):
        self.catalogo_repo = catalogo_repo

    def gerar_relatorio_compras_locacoes(
        self, 
        data_inicio: Optional[date] = None, 
        data_fim: Optional[date] = None
    ) -> Dict:
        """
        Gera um relatório consolidado de vendas e aluguéis, com filtros opcionais de data.
        """
        vendas = self.catalogo_repo.get_vendas_por_periodo(data_inicio, data_fim)
        alugueis = self.catalogo_repo.get_alugueis_por_periodo(data_inicio, data_fim)

        total_vendas = sum(v.valor_total for v in vendas)
        total_alugueis = sum(a.valor_total for a in alugueis)

        breakdown_vendas = self._agrupar_por_jogo(vendas)
        breakdown_alugueis = self._agrupar_por_jogo(alugueis)

        return {
            "resumo": {
                "total_vendas": total_vendas,
                "quantidade_vendas": len(vendas),
                "total_alugueis": total_alugueis,
                "quantidade_alugueis": len(alugueis),
                "faturamento_total": total_vendas + total_alugueis
            },
            "breakdown_por_jogo": {
                "vendas": breakdown_vendas,
                "alugueis": breakdown_alugueis
            }
        }

    def _agrupar_por_jogo(self, transacoes: List) -> Dict:
        """Agrupa transações pelo título do jogo."""
        agrupado = {}
        for transacao in transacoes:
            for item in transacao.itens_transacao:
                jogo = item.exemplar.catalogo
                if jogo.titulo not in agrupado:
                    agrupado[jogo.titulo] = {"quantidade": 0, "valor_total": 0}
                
                agrupado[jogo.titulo]["quantidade"] += 1
                agrupado[jogo.titulo]["valor_total"] += transacao.valor_total
        
        return agrupado
