from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Tuple

from app.repository.mock.aluguel_repository_mock import AluguelRepositoryMock
from app.models import Aluguel, Comprovante, Multa, Exemplar, Catalogo, ItemTransacao
from app.models.estoque.midia_fisica import MidiaFisica
from app.models.enums import TipoComprovante, StatusAluguel

_CONDICOES_DEVOLUCAO = frozenset({"bom", "danificado", "extraviado"})

class AluguelService:
    """Service layer for rental (Aluguel) operations."""

    def __init__(self, repository: AluguelRepositoryMock):
        self.repo = repository

    def solicitar_aluguel(self, id_cliente: int, id_jogo: int, dias_alugados: int, data_inicio: datetime.date, tipo_midia: str) -> Tuple[Optional[Aluguel], Optional[str]]:
        jogo = self.repo.get_catalogo_by_id(id_jogo)
        if not jogo or getattr(jogo, 'situacao', None) != 'DISPONIVEL':
            return None, "Jogo não existe ou está inativo."

        exemplar = self.repo.find_exemplar_disponivel(jogo.id, tipo_midia)
        if not exemplar:
            return None, f"Não há exemplares da mídia {tipo_midia} disponíveis no momento para este jogo."

        valor_diaria = getattr(exemplar, 'valor_diaria_aluguel', None)
        if not valor_diaria:
            return None, "Este jogo não está disponível para aluguel (valor da diária não definido)."
        
        valor_total = valor_diaria * dias_alugados
        data_prevista_devolucao = data_inicio + timedelta(days=dias_alugados)

        novo_aluguel = Aluguel(
            id_cliente=id_cliente,
            valor_total=valor_total,
            status='SOLICITADO',
            periodo=dias_alugados,
            data_inicio=data_inicio,
            data_prevista_devolucao=data_prevista_devolucao
        )
        
        aluguel_criado = self.repo.create_aluguel(novo_aluguel)
        
        item_transacao = ItemTransacao(
            transacao=aluguel_criado,
            exemplar=exemplar,
            valor_unitario=valor_diaria
        )
        self.repo.create_item_transacao(item_transacao)

        return aluguel_criado, None

    def registrar_retirada(self, aluguel_id: int) -> Tuple[Optional[Aluguel], Optional[str]]:
        aluguel = self.repo.get_by_id(aluguel_id)
        if not aluguel:
            return None, "Aluguel não encontrado."
        
        if aluguel.status not in (StatusAluguel.SOLICITADO.value, StatusAluguel.APROVADO.value):
            return None, "Retirada permitida apenas para aluguel solicitado ou aprovado."

        agora = datetime.utcnow()
        aluguel.data_retirada = agora
        aluguel.status = StatusAluguel.ATIVO.value
        aluguel.data_inicio = agora.date()
        
        if aluguel.periodo and aluguel.periodo > 0:
            aluguel.data_prevista_devolucao = aluguel.data_inicio + timedelta(days=aluguel.periodo)

        items = self.repo.get_items_by_transacao(aluguel.id)
        if not items:
            return None, "Itens da transação não encontrados."

        for item in items:
            exemplar = self.repo.get_exemplar_by_id(item.id_exemplar)
            if exemplar:
                exemplar.set_situacao("ALUGADO")
                self.repo.update(exemplar)

        self._gerar_e_salvar_comprovante(aluguel, TipoComprovante.ALUGUEL.value)
        
        self.repo.update(aluguel)
        return aluguel, None

    def registrar_devolucao(self, aluguel_id: int, condicao_item: str, id_funcionario: int) -> Tuple[Optional[Aluguel], Optional[str]]:
        aluguel = self.repo.get_by_id(aluguel_id)
        if not aluguel:
            return None, "Aluguel não encontrado."

        if not condicao_item or not str(condicao_item).strip():
            return None, "O campo 'condicao_item' é obrigatório."
        cond_norm = str(condicao_item).strip().lower()
        if cond_norm not in _CONDICOES_DEVOLUCAO:
            return None, "condicao_item deve ser: bom, danificado ou extraviado."
        
        if aluguel.status not in (StatusAluguel.ATIVO.value, StatusAluguel.ATRASADO.value):
            return None, "Devolução permitida apenas para aluguel ativo ou atrasado."
        if aluguel.data_devolucao_real:
            return None, "Devolução já registrada para este aluguel."

        agora = datetime.utcnow()
        aluguel.data_devolucao_real = agora
        aluguel.data_devolucao = agora.date()
        aluguel.status = StatusAluguel.FINALIZADO.value
        aluguel.condicao_item = cond_norm
        aluguel.id_funcionario_recebimento = id_funcionario

        # Lazy loading
        items = self.repo.get_items_by_transacao(aluguel.id)
        if not items:
            return None, "Itens da transação não encontrados."

        multa_valor = self._calcular_multa(aluguel, items)
        aluguel.multa_paga = multa_valor == 0
        aluguel.dias_atraso = self._calcular_dias_atraso(aluguel)

        for item in items:
            exemplar = self.repo.get_exemplar_by_id(item.id_exemplar)
            if exemplar:
                exemplar.set_situacao("DISPONIVEL")
                if isinstance(exemplar, MidiaFisica):
                    exemplar.set_estado_conservacao(cond_norm)
                self.repo.update(exemplar)

        if multa_valor > 0:
            self._criar_e_salvar_multa(aluguel, multa_valor)

        self._gerar_e_salvar_comprovante(aluguel, TipoComprovante.DEVOLUCAO.value)

        self.repo.update(aluguel)
        return aluguel, None

    def renovar_aluguel(self, aluguel_id: int, id_cliente: int, dias_adicionais: int) -> Tuple[Optional[Aluguel], Optional[str]]:
        aluguel = self.repo.get_by_id(aluguel_id)
        if not aluguel or aluguel.id_cliente != id_cliente:
            return None, "Aluguel não encontrado ou não pertence a este cliente."

        if aluguel.status == 'FINALIZADO':
            return None, "Não é possível renovar um aluguel já finalizado."

        item_transacao = self.repo.get_items_by_transacao(aluguel.id)
        if not item_transacao:
            return None, "Item da transação não encontrado."
        
        exemplar = self.repo.get_exemplar_by_id(item_transacao[0].id_exemplar)
        if not exemplar or not hasattr(exemplar, 'valor_diaria_aluguel') or exemplar.valor_diaria_aluguel is None:
            return None, "Exemplar ou valor da diária não encontrado."
            
        acrescimo = exemplar.valor_diaria_aluguel * dias_adicionais
        aluguel.periodo += dias_adicionais
        aluguel.data_prevista_devolucao += timedelta(days=dias_adicionais)
        aluguel.valor_total += acrescimo
        
        self.repo.update(aluguel)
        return aluguel, None

    def cancelar_aluguel(self, aluguel_id: int, id_cliente: int) -> Tuple[Optional[Aluguel], Optional[str]]:
        aluguel = self.repo.get_by_id(aluguel_id)
        if not aluguel or aluguel.id_cliente != id_cliente:
            return None, "Aluguel não encontrado ou não pertence a este cliente."

        if aluguel.status not in ['SOLICITADO', 'APROVADO']:
             return None, f"Não é possível cancelar um aluguel com status '{aluguel.status}'."
        if aluguel.data_inicio <= datetime.today().date():
            return None, "Não é possível cancelar um aluguel que já iniciou ou está no dia de retirada."

        aluguel.status = 'FINALIZADO'
        
        item_tr = self.repo.get_items_by_transacao(aluguel.id)
        if item_tr:
            exemplar = self.repo.get_exemplar_by_id(item_tr[0].id_exemplar)
            if exemplar and exemplar.situacao == 'RESERVADO':
                exemplar.set_situacao('DISPONIVEL')
                self.repo.update(exemplar)
        
        self.repo.update(aluguel)
        return aluguel, None

    def _calcular_dias_atraso(self, aluguel: Aluguel) -> int:
        if aluguel.data_prevista_devolucao and aluguel.data_devolucao:
            if aluguel.data_devolucao > aluguel.data_prevista_devolucao:
                return (aluguel.data_devolucao - aluguel.data_prevista_devolucao).days
        return 0

    def _calcular_multa(self, aluguel: Aluguel, items: list) -> Decimal:
        dias_atraso = self._calcular_dias_atraso(aluguel)
        if dias_atraso <= 0:
            return Decimal("0")

        valor_diaria_total = sum(
            (self.repo.get_exemplar_by_id(item.id_exemplar).valor_diaria_aluguel or Decimal("0"))
            for item in items
        )

        if valor_diaria_total > 0:
            multa_bruta = self._quantize(Decimal(dias_atraso) * (valor_diaria_total * Decimal("0.10")))
            teto = self._quantize(aluguel.valor_total or Decimal("0"))
            return min(multa_bruta, teto) if teto > 0 else multa_bruta
        
        return Decimal("0")

    def _criar_e_salvar_multa(self, aluguel: Aluguel, valor: Decimal):
        multa = Multa(
            dias_atraso=aluguel.dias_atraso,
            valor=valor,
            status="PENDENTE",
            data_calculo=aluguel.data_devolucao
        )
        saved_multa = self.repo.create_multa(multa)
        aluguel.set_multa(saved_multa)

    def _gerar_e_salvar_comprovante(self, aluguel: Aluguel, tipo: str):
        aluguel.set_comprovante(tipo)
        for comprovante in aluguel.comprovantes:
            if not comprovante.id:
                saved = self.repo.create_comprovante(comprovante)
                comprovante.id = saved.id

    def _quantize(self, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
