from datetime import date
from decimal import Decimal
from typing import List, Dict, Optional

from app.repository.interface.catalogo_repository_interface import CatalogoRepositoryInterface


def _to_float(value) -> float:
    if value is None:
        return 0.0
    return float(value)


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

        total_vendas = sum((v.valor_total or 0) for v in vendas)
        total_alugueis = sum((a.valor_total or 0) for a in alugueis)

        breakdown_vendas = self._agrupar_por_jogo(vendas)
        breakdown_alugueis = self._agrupar_por_jogo(alugueis)

        return {
            "resumo": {
                "total_vendas": _to_float(total_vendas),
                "quantidade_vendas": len(vendas),
                "total_alugueis": _to_float(total_alugueis),
                "quantidade_alugueis": len(alugueis),
                "faturamento_total": _to_float(total_vendas + total_alugueis),
            },
            "breakdown_por_jogo": {
                "vendas": breakdown_vendas,
                "alugueis": breakdown_alugueis,
            },
        }

    def _agrupar_por_jogo(self, transacoes: List) -> Dict:
        """Agrupa transações pelo título do jogo."""
        agrupado = {}
        for transacao in transacoes:
            titulo = self._titulo_jogo_transacao(transacao)
            if not titulo:
                titulo = "Desconhecido"
            if titulo not in agrupado:
                agrupado[titulo] = {"quantidade": 0, "valor_total": 0.0}

            agrupado[titulo]["quantidade"] += 1
            agrupado[titulo]["valor_total"] = _to_float(
                Decimal(str(agrupado[titulo]["valor_total"])) + (transacao.valor_total or 0)
            )

        return agrupado

    def _titulo_jogo_transacao(self, transacao) -> Optional[str]:
        itens = getattr(transacao, "itens_transacao", None) or []
        for item in itens:
            exemplar = getattr(item, "exemplar", None)
            if exemplar is None and getattr(item, "id_exemplar", None):
                from app.repository.db.estoque_repository_db import EstoqueRepositoryDB
                repo = EstoqueRepositoryDB(self.catalogo_repo.data_source)
                exemplar = repo.get_exemplar_by_id(item.id_exemplar)
            catalogo = getattr(exemplar, "catalogo", None) if exemplar else None
            if catalogo and getattr(catalogo, "titulo", None):
                return catalogo.titulo
        return None
