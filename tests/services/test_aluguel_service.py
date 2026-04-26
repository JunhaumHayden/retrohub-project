"""Testes unitários do AluguelService.

Usa o ``container`` global (modo mock) e reseta entre os testes para
garantir isolamento. Cada teste exercita uma transição do ciclo de vida
do aluguel ou uma regra de negócio (multa, validações).
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.container.container import container
from app.models import Aluguel, Cliente, Funcionario
from app.models.enums import StatusAluguel, StatusPagamento
from app.models.transacao.aluguel.multa import Multa


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _cliente() -> Cliente:
    return container.usuario_service.get_cliente_by_id(3)


def _funcionario() -> Funcionario:
    return container.usuario_service.get_funcionario_by_id(1)


def _solicitar_padrao(
        id_jogo: int = 1, dias: int = 5, tipo: str = "FISICA",
) -> Aluguel:
    """Cria um aluguel padrão para reuso nos testes."""
    return container.aluguel_service.solicitar(
        cliente=_cliente(),
        id_jogo=id_jogo,
        dias_alugados=dias,
        data_inicio=date.today(),
        tipo_midia=tipo,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _reset_container():
    container.reset()
    yield
    container.reset()


# ---------------------------------------------------------------------------
# solicitar()
# ---------------------------------------------------------------------------
class TestSolicitar:
    def test_solicitar_cria_aluguel_e_marca_exemplar_reservado(self):
        aluguel = _solicitar_padrao(id_jogo=1, dias=5, tipo="FISICA")

        assert aluguel.id is not None
        assert aluguel.status == StatusAluguel.SOLICITADO.value
        assert aluguel.id_cliente == 3
        assert aluguel.periodo == 5
        assert aluguel.data_prevista_devolucao == date.today() + timedelta(days=5)
        # 5.90 (diária do exemplar 1) * 5 dias = 29.50
        assert aluguel.valor_total == Decimal("29.50")

        # Exemplar associado deve ter ficado RESERVADO
        item = aluguel.itens_transacao[0]
        assert item.exemplar.situacao == "RESERVADO"

    def test_solicitar_falha_quando_periodo_invalido(self):
        with pytest.raises(ValueError, match="entre 1 e 30 dias"):
            container.aluguel_service.solicitar(
                cliente=_cliente(),
                id_jogo=1,
                dias_alugados=0,
                data_inicio=date.today(),
                tipo_midia="FISICA",
            )

    def test_solicitar_falha_quando_data_passada(self):
        with pytest.raises(ValueError, match="data atual"):
            container.aluguel_service.solicitar(
                cliente=_cliente(),
                id_jogo=1,
                dias_alugados=3,
                data_inicio=date.today() - timedelta(days=1),
                tipo_midia="FISICA",
            )

    def test_solicitar_falha_quando_jogo_inexistente(self):
        with pytest.raises(ValueError, match="indispon"):
            container.aluguel_service.solicitar(
                cliente=_cliente(),
                id_jogo=99999,
                dias_alugados=3,
                data_inicio=date.today(),
                tipo_midia="FISICA",
            )

    def test_solicitar_falha_quando_sem_exemplar_disponivel(self):
        # Solicita o primeiro -> reserva o único exemplar físico do catálogo 1
        _solicitar_padrao(id_jogo=1, dias=2, tipo="FISICA")
        # Segunda tentativa deve falhar
        with pytest.raises(ValueError, match="exemplares"):
            container.aluguel_service.solicitar(
                cliente=_cliente(),
                id_jogo=1,
                dias_alugados=2,
                data_inicio=date.today(),
                tipo_midia="FISICA",
            )

    def test_solicitar_tipo_midia_invalido(self):
        with pytest.raises(ValueError, match="FISICA ou DIGITAL"):
            container.aluguel_service.solicitar(
                cliente=_cliente(),
                id_jogo=1,
                dias_alugados=2,
                data_inicio=date.today(),
                tipo_midia="VHS",
            )


# ---------------------------------------------------------------------------
# aprovar()
# ---------------------------------------------------------------------------
class TestAprovar:
    def test_aprovar_passa_para_aprovado(self):
        aluguel = _solicitar_padrao()
        aprovado = container.aluguel_service.aprovar(aluguel.id, _funcionario())
        assert aprovado.status == StatusAluguel.APROVADO.value
        assert aprovado.id_funcionario == 1

    def test_aprovar_aluguel_inexistente(self):
        with pytest.raises(LookupError):
            container.aluguel_service.aprovar(99999, _funcionario())

    def test_aprovar_status_invalido(self):
        aluguel = _solicitar_padrao()
        container.aluguel_service.aprovar(aluguel.id, _funcionario())
        with pytest.raises(ValueError, match="status atual"):
            container.aluguel_service.aprovar(aluguel.id, _funcionario())


# ---------------------------------------------------------------------------
# cancelar()
# ---------------------------------------------------------------------------
class TestCancelar:
    def test_cancelar_solicitado_libera_exemplar(self):
        # Coloca data_inicio no futuro para o cancelamento ser válido
        aluguel = container.aluguel_service.solicitar(
            cliente=_cliente(),
            id_jogo=1,
            dias_alugados=3,
            data_inicio=date.today() + timedelta(days=1),
            tipo_midia="FISICA",
        )
        item = aluguel.itens_transacao[0]
        assert item.exemplar.situacao == "RESERVADO"

        cancelado = container.aluguel_service.cancelar(aluguel.id, 3)
        assert cancelado.status == "CANCELADO"
        assert item.exemplar.situacao == "DISPONIVEL"

    def test_cancelar_de_outro_cliente_falha(self):
        aluguel = container.aluguel_service.solicitar(
            cliente=_cliente(),
            id_jogo=1,
            dias_alugados=3,
            data_inicio=date.today() + timedelta(days=1),
            tipo_midia="FISICA",
        )
        with pytest.raises(LookupError):
            container.aluguel_service.cancelar(aluguel.id, 99)


# ---------------------------------------------------------------------------
# retirada()
# ---------------------------------------------------------------------------
class TestRetirada:
    def test_retirada_passa_para_ativo_e_exemplar_alugado(self):
        aluguel = _solicitar_padrao()
        item = aluguel.itens_transacao[0]
        retirado = container.aluguel_service.registrar_retirada(
            aluguel.id, _funcionario(),
        )
        assert retirado.status == StatusAluguel.ATIVO.value
        assert retirado.data_retirada is not None
        assert item.exemplar.situacao == "ALUGADO"

    def test_retirada_sem_aluguel_existente(self):
        with pytest.raises(LookupError):
            container.aluguel_service.registrar_retirada(99999, _funcionario())

    def test_retirada_status_invalido(self):
        aluguel = _solicitar_padrao()
        container.aluguel_service.registrar_retirada(aluguel.id, _funcionario())
        with pytest.raises(ValueError):
            # Tentar retirar de novo um aluguel ATIVO -> rejeitar
            container.aluguel_service.registrar_retirada(aluguel.id, _funcionario())


# ---------------------------------------------------------------------------
# devolução() + multa
# ---------------------------------------------------------------------------
class TestDevolucao:
    def test_devolucao_sem_atraso_gera_multa_zero_e_paga(self):
        aluguel = _solicitar_padrao(id_jogo=1, dias=5, tipo="FISICA")
        container.aluguel_service.registrar_retirada(aluguel.id, _funcionario())
        # data_prevista_devolucao foi recalculada para 5 dias a partir de hoje,
        # então hoje a devolução não está atrasada.
        finalizado, multa = container.aluguel_service.registrar_devolucao(
            aluguel.id, "bom", _funcionario(),
        )
        assert finalizado.status == StatusAluguel.FINALIZADO.value
        assert finalizado.dias_atraso == 0
        assert finalizado.condicao_item == "bom"
        assert isinstance(multa, Multa)
        assert multa.valor == Decimal("0")
        assert multa.status == StatusPagamento.PAGO.value
        # Exemplar volta a ficar disponível
        item = finalizado.itens_transacao[0]
        assert item.exemplar.situacao == "DISPONIVEL"

    def test_devolucao_com_atraso_calcula_multa(self):
        aluguel = _solicitar_padrao(id_jogo=1, dias=2, tipo="FISICA")
        container.aluguel_service.registrar_retirada(aluguel.id, _funcionario())
        # Forja um atraso de 3 dias retroagindo a previsão
        aluguel.data_prevista_devolucao = date.today() - timedelta(days=3)
        finalizado, multa = container.aluguel_service.registrar_devolucao(
            aluguel.id, "bom", _funcionario(),
        )
        assert finalizado.dias_atraso == 3
        # 3 dias * (5.90 * 0.10) = 1.77
        assert multa.valor == Decimal("1.77")
        assert multa.status == StatusPagamento.PENDENTE.value
        assert multa.aluguel is finalizado
        assert finalizado.multa_aplicada is multa

    def test_devolucao_aplica_teto_de_100_por_cento(self):
        aluguel = _solicitar_padrao(id_jogo=1, dias=2, tipo="FISICA")
        container.aluguel_service.registrar_retirada(aluguel.id, _funcionario())
        # Atraso enorme -> garante que multa bruta passa do teto
        aluguel.data_prevista_devolucao = date.today() - timedelta(days=200)
        finalizado, multa = container.aluguel_service.registrar_devolucao(
            aluguel.id, "danificado", _funcionario(),
        )
        # Teto = valor_total = 2 * 5.90 = 11.80
        assert multa.valor == finalizado.valor_total

    def test_devolucao_condicao_invalida(self):
        aluguel = _solicitar_padrao()
        container.aluguel_service.registrar_retirada(aluguel.id, _funcionario())
        with pytest.raises(ValueError, match="condicao_item"):
            container.aluguel_service.registrar_devolucao(
                aluguel.id, "perfeito", _funcionario(),
            )

    def test_devolucao_de_aluguel_nao_ativo_rejeitada(self):
        aluguel = _solicitar_padrao()
        # Ainda está SOLICITADO (sem retirada)
        with pytest.raises(ValueError, match="status"):
            container.aluguel_service.registrar_devolucao(
                aluguel.id, "bom", _funcionario(),
            )


# ---------------------------------------------------------------------------
# renovar()
# ---------------------------------------------------------------------------
class TestRenovar:
    def test_renovar_estende_prazo_e_valor(self):
        aluguel = _solicitar_padrao(id_jogo=1, dias=2, tipo="FISICA")
        container.aluguel_service.registrar_retirada(aluguel.id, _funcionario())
        prazo_original = aluguel.data_prevista_devolucao
        valor_original = Decimal(aluguel.valor_total)

        renovado = container.aluguel_service.renovar(
            aluguel.id, 3, dias_adicionais=4,
        )
        assert renovado.periodo == 6  # 2 + 4
        assert renovado.data_prevista_devolucao == prazo_original + timedelta(days=4)
        # Valor original + (4 * 5.90) = original + 23.60
        assert renovado.valor_total == valor_original + Decimal("23.60")

    def test_renovar_aluguel_nao_ativo(self):
        aluguel = _solicitar_padrao()
        # Ainda SOLICITADO
        with pytest.raises(ValueError):
            container.aluguel_service.renovar(aluguel.id, 3, dias_adicionais=2)


# ---------------------------------------------------------------------------
# listar / obter
# ---------------------------------------------------------------------------
class TestQueries:
    def test_listar_por_cliente_traz_apenas_proprios(self):
        aluguel = _solicitar_padrao()
        meus = container.aluguel_service.listar_por_cliente(3)
        ids = {a.id for a in meus}
        assert aluguel.id in ids

        outros = container.aluguel_service.listar_por_cliente(99)
        assert outros == []

    def test_obter_exige_posse(self):
        aluguel = _solicitar_padrao()
        assert container.aluguel_service.obter(aluguel.id, 3) is not None
        assert container.aluguel_service.obter(aluguel.id, 99) is None
