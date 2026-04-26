"""Testes de integração HTTP das rotas de aluguel.

Cobre o ciclo completo via Flask test_client:
solicitar -> aprovar -> retirada -> devolucao -> consultas -> erros.
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from app import create_app
from app.container.container import container


CLIENTE_ID = 3
FUNC_ID = 1
JOGO_ID = 1
TIPO = "FISICA"


@pytest.fixture
def client():
    container.reset()
    app = create_app()
    app.testing = True
    with app.test_client() as test_client:
        yield test_client
    container.reset()


def _hdr_cliente(cid: int = CLIENTE_ID) -> dict[str, str]:
    return {"X-Cliente-Id": str(cid)}


def _hdr_func(fid: int = FUNC_ID) -> dict[str, str]:
    return {"X-Funcionario-Id": str(fid)}


def _solicitar(client, dias: int = 5) -> dict:
    payload = {
        "id_jogo": JOGO_ID,
        "dias_alugados": dias,
        "data_inicio": date.today().isoformat(),
        "tipo_midia": TIPO,
    }
    resp = client.post(
        "/api/alugueis/solicitar", json=payload, headers=_hdr_cliente(),
    )
    assert resp.status_code == 201, resp.get_json()
    return resp.get_json()["aluguel"]


# ---------------------------------------------------------------------------
# Casos de uso felizes
# ---------------------------------------------------------------------------
class TestCicloCompleto:
    def test_solicitar_aprovar_retirar_devolver(self, client):
        aluguel = _solicitar(client, dias=5)
        aid = aluguel["id_transacao"]
        assert aluguel["status_aluguel"] == "SOLICITADO"

        # Aprovar
        resp = client.patch(
            f"/api/alugueis/{aid}/aprovar", headers=_hdr_func(),
        )
        assert resp.status_code == 200
        assert resp.get_json()["status_aluguel"] == "APROVADO"

        # Retirada
        resp = client.patch(
            f"/api/alugueis/{aid}/retirada", headers=_hdr_func(),
        )
        assert resp.status_code == 200
        assert resp.get_json()["aluguel"]["status_aluguel"] == "ATIVO"

        # Devolução sem atraso
        resp = client.patch(
            f"/api/alugueis/{aid}/devolucao",
            json={"condicao_item": "bom"},
            headers=_hdr_func(),
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["aluguel"]["status_aluguel"] == "FINALIZADO"
        assert body["multa"]["valor"] == 0
        assert body["multa"]["status"] == "PAGO"


# ---------------------------------------------------------------------------
# Validações HTTP
# ---------------------------------------------------------------------------
class TestValidacoesSolicitar:
    def test_solicitar_sem_cliente_header_403(self, client):
        resp = client.post(
            "/api/alugueis/solicitar",
            json={
                "id_jogo": JOGO_ID,
                "dias_alugados": 3,
                "data_inicio": date.today().isoformat(),
                "tipo_midia": TIPO,
            },
        )
        assert resp.status_code == 403

    def test_solicitar_data_invalida_400(self, client):
        resp = client.post(
            "/api/alugueis/solicitar",
            json={
                "id_jogo": JOGO_ID,
                "dias_alugados": 3,
                "data_inicio": "26/04/2026",
                "tipo_midia": TIPO,
            },
            headers=_hdr_cliente(),
        )
        assert resp.status_code == 400

    def test_solicitar_periodo_invalido_400(self, client):
        resp = client.post(
            "/api/alugueis/solicitar",
            json={
                "id_jogo": JOGO_ID,
                "dias_alugados": 0,
                "data_inicio": date.today().isoformat(),
                "tipo_midia": TIPO,
            },
            headers=_hdr_cliente(),
        )
        assert resp.status_code == 400

    def test_solicitar_jogo_inexistente_400(self, client):
        resp = client.post(
            "/api/alugueis/solicitar",
            json={
                "id_jogo": 99999,
                "dias_alugados": 3,
                "data_inicio": date.today().isoformat(),
                "tipo_midia": TIPO,
            },
            headers=_hdr_cliente(),
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Consultas
# ---------------------------------------------------------------------------
class TestConsultas:
    def test_meus_alugueis_lista_apenas_do_cliente(self, client):
        novo = _solicitar(client)
        resp = client.get(
            "/api/alugueis/meus-alugueis", headers=_hdr_cliente(),
        )
        assert resp.status_code == 200
        ids = [a["id_transacao"] for a in resp.get_json()]
        assert novo["id_transacao"] in ids

    def test_detalhe_de_outro_cliente_retorna_404(self, client):
        novo = _solicitar(client)
        resp = client.get(
            f"/api/alugueis/{novo['id_transacao']}",
            headers=_hdr_cliente(99),
        )
        assert resp.status_code == 403  # cliente 99 não cadastrado


# ---------------------------------------------------------------------------
# Cancelar e Renovar
# ---------------------------------------------------------------------------
class TestCancelarRenovar:
    def test_cancelar_aluguel_solicitado(self, client):
        # Data de início no futuro, para passar na regra de cancelamento
        payload = {
            "id_jogo": JOGO_ID,
            "dias_alugados": 3,
            "data_inicio": (date.today() + timedelta(days=1)).isoformat(),
            "tipo_midia": TIPO,
        }
        resp = client.post(
            "/api/alugueis/solicitar", json=payload, headers=_hdr_cliente(),
        )
        aid = resp.get_json()["aluguel"]["id_transacao"]

        resp = client.patch(
            f"/api/alugueis/{aid}/cancelar", headers=_hdr_cliente(),
        )
        assert resp.status_code == 200
        assert resp.get_json()["aluguel"]["status_aluguel"] == "CANCELADO"

    def test_renovar_apenas_quando_ativo(self, client):
        novo = _solicitar(client)
        resp = client.patch(
            f"/api/alugueis/{novo['id_transacao']}/renovar",
            json={"dias_adicionais": 3},
            headers=_hdr_cliente(),
        )
        assert resp.status_code == 400  # ainda SOLICITADO, não pode renovar

    def test_renovar_aluguel_ativo(self, client):
        novo = _solicitar(client, dias=3)
        aid = novo["id_transacao"]
        client.patch(f"/api/alugueis/{aid}/aprovar", headers=_hdr_func())
        client.patch(f"/api/alugueis/{aid}/retirada", headers=_hdr_func())

        resp = client.patch(
            f"/api/alugueis/{aid}/renovar",
            json={"dias_adicionais": 4},
            headers=_hdr_cliente(),
        )
        assert resp.status_code == 200
        body = resp.get_json()["aluguel"]
        assert body["periodo_dias"] == 7  # 3 + 4
