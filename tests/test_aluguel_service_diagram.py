"""Testes alinhados aos diagramas — AluguelService e CatalogoService."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.container.container import Container
from app.models import Aluguel, ItemTransacao, MidiaFisica, Cliente, Funcionario
from app.models.enums import StatusAluguel, TipoComprovante


@pytest.fixture
def container():
    c = Container()
    c.reset()
    return c


class TestCatalogoInserirDiagrama:
    def test_inserir_catalogo_fisico_sucesso(self, container):
        dados = {
            "titulo": "Jogo Diagrama Teste FISICO",
            "descricao": "RF 13",
            "tipo_midia": "FISICA",
            "codigo_barras": "DIAG-FIS-001",
            "estado_conservacao": "bom",
            "plataforma": "SNES",
        }
        assert container.catalogo_service.inserir_catalogo(dados) is True
        cat = container.catalogo_service.get_by_title(dados["titulo"])
        assert cat is not None
        assert cat.estoque_disponivel >= 1

    def test_inserir_catalogo_duplicado_retorna_false(self, container):
        dados = {
            "titulo": "Jogo Duplicado Diagrama",
            "tipo_midia": "DIGITAL",
            "chave_ativacao": "CHAVE-DUP-1",
        }
        assert container.catalogo_service.inserir_catalogo(dados) is True
        assert container.catalogo_service.inserir_catalogo(dados) is False


class TestAluguelFinalizarDiagrama:
    def _montar_aluguel_ativo(self, container):
        catalogos = container.catalogo_service.list_all()
        assert catalogos
        catalogo = catalogos[0]
        exemplares = [
            ex for ex in container.data_source.get_all(MidiaFisica)
            if ex.id_catalogo == catalogo.id
        ]
        if not exemplares:
            container.catalogo_service.inserir_catalogo({
                "titulo": f"Temp {catalogo.id}",
                "tipo_midia": "FISICA",
                "codigo_barras": f"TMP-{catalogo.id}",
                "estado_conservacao": "bom",
            })
            exemplares = [
                ex for ex in container.data_source.get_all(MidiaFisica)
                if ex.id_catalogo == catalogo.id
            ]
        exemplar = exemplares[0]
        exemplar.valor_diaria_aluguel = Decimal("15.00")
        exemplar.set_situacao("DISPONIVEL")
        container.data_source.update(exemplar)

        clientes = container.data_source.get_all(Cliente)
        funcionarios = container.data_source.get_all(Funcionario)
        aluguel = Aluguel(
            valor_total=Decimal("30.00"),
            status=StatusAluguel.ATIVO.value,
            periodo=3,
            data_inicio=date.today() - timedelta(days=10),
            data_prevista_devolucao=date.today() - timedelta(days=2),
            cliente=clientes[0],
            funcionario=funcionarios[0],
        )
        aluguel = container.data_source.create(aluguel)
        item = ItemTransacao(
            id=container.data_source.get_next_id(ItemTransacao),
            transacao=aluguel,
            exemplar=exemplar,
            valor_unitario=Decimal("10.00"),
        )
        container.data_source.create(item)
        exemplar.set_situacao("ALUGADO")
        container.data_source.update(exemplar)
        return aluguel, exemplar, funcionarios[0]

    def test_finalizar_aluguel_com_multa_e_comprovante(self, container):
        aluguel, _exemplar, funcionario = self._montar_aluguel_ativo(container)
        ok = container.aluguel_service.finalizar_aluguel(
            aluguel.id, "bom", funcionario.id,
        )
        assert ok is True

        atualizado = container.aluguel_service.get_aluguel_by_id(aluguel.id)
        assert atualizado.status == StatusAluguel.FINALIZADO.value
        assert atualizado.dias_atraso > 0
        assert atualizado.get_multa().valor > 0
        assert any(
            c.tipo_comprovante == TipoComprovante.DEVOLUCAO.value
            for c in atualizado.comprovantes
        )
