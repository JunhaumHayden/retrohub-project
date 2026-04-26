"""Rotas REST para o recurso Aluguel.

Controller magro: faz parse de headers/body, delega ao
``AluguelService`` (regra de negócio) e serializa a resposta.
"""

from __future__ import annotations

import logging
from datetime import datetime, date

from flask import request
from flask_restx import Namespace, Resource, fields

from app.container.container import container
from app.models import Cliente, Funcionario, Aluguel
from app.models.transacao.aluguel.multa import Multa

alugueis_ns = Namespace(
    'alugueis',
    description='Operações relacionadas aos aluguéis de jogos',
    path='/api/alugueis',
)

aluguel_solicitacao_model = alugueis_ns.model('AluguelSolicitacao', {
    'id_jogo': fields.Integer(
        required=True, description='ID do jogo no catálogo',
    ),
    'dias_alugados': fields.Integer(
        required=True, description='Período do aluguel em dias (1-30)',
    ),
    'data_inicio': fields.String(
        required=True, description='Data de início (YYYY-MM-DD)',
    ),
    'tipo_midia': fields.String(
        required=True, description='Tipo de mídia (FISICA ou DIGITAL)',
    ),
})

aluguel_devolucao_model = alugueis_ns.model('AluguelDevolucao', {
    'condicao_item': fields.String(
        required=True,
        description='Condição do item devolvido (bom/danificado/extraviado)',
    ),
})

aluguel_renovacao_model = alugueis_ns.model('AluguelRenovacao', {
    'dias_adicionais': fields.Integer(
        required=True, description='Número de dias adicionais (1-30)',
    ),
})

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers de header / serialização
# ---------------------------------------------------------------------------
def _get_cliente_from_header() -> tuple[Cliente | None, str | None]:
    cliente_id = request.headers.get('X-Cliente-Id')
    if not cliente_id:
        return None, 'Header X-Cliente-Id é obrigatório.'
    try:
        cliente_id = int(cliente_id)
    except ValueError:
        return None, 'X-Cliente-Id inválido.'
    cliente = container.data_source.get_by_id(Cliente, cliente_id)
    if not cliente:
        return None, 'Cliente não cadastrado ou não encontrado.'
    return cliente, None


def _get_funcionario_from_header() -> tuple[Funcionario | None, str | None]:
    func_id = request.headers.get('X-Funcionario-Id') or request.headers.get(
        'X-Admin-Id'
    )
    if not func_id:
        return None, (
            'Header X-Funcionario-Id (ou X-Admin-Id) é obrigatório '
            'para esta operação.'
        )
    try:
        func_id = int(func_id)
    except ValueError:
        return None, 'O ID do funcionário deve ser um número inteiro.'
    funcionario = container.data_source.get_by_id(Funcionario, func_id)
    if not funcionario:
        return None, 'Funcionário não encontrado.'
    return funcionario, None


def _multa_to_dict(multa: Multa | None) -> dict | None:
    if multa is None:
        return None
    return {
        'id': multa.id,
        'dias_atraso': multa.dias_atraso,
        'valor': float(multa.valor) if multa.valor is not None else None,
        'status': multa.status,
        'data_calculo': (
            multa.data_calculo.isoformat() if multa.data_calculo else None
        ),
    }


def _serialize_aluguel(aluguel: Aluguel) -> dict:
    multa = aluguel.multa_aplicada if isinstance(
        aluguel.multa_aplicada, Multa
    ) else None
    return {
        'id_transacao': aluguel.id,
        'id_cliente': aluguel.id_cliente,
        'id_funcionario': aluguel.id_funcionario,
        'data_transacao': (
            aluguel.data_transacao.isoformat()
            if aluguel.data_transacao else None
        ),
        'valor_total': (
            float(aluguel.valor_total) if aluguel.valor_total else None
        ),
        'status_aluguel': aluguel.status,
        'periodo_dias': aluguel.periodo,
        'data_inicio': (
            aluguel.data_inicio.isoformat() if aluguel.data_inicio else None
        ),
        'data_prevista_devolucao': (
            aluguel.data_prevista_devolucao.isoformat()
            if aluguel.data_prevista_devolucao else None
        ),
        'data_retirada': (
            aluguel.data_retirada.isoformat()
            if aluguel.data_retirada else None
        ),
        'data_devolucao_real': (
            aluguel.data_devolucao_real.isoformat()
            if aluguel.data_devolucao_real else None
        ),
        'condicao_item': aluguel.condicao_item,
        'dias_atraso': getattr(aluguel, 'dias_atraso', None),
        'multa': _multa_to_dict(multa),
        'multa_paga': aluguel.multa_paga,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@alugueis_ns.route('/solicitar')
class SolicitarAluguelResource(Resource):
    @alugueis_ns.expect(aluguel_solicitacao_model)
    def post(self):
        """Solicita um novo aluguel (status SOLICITADO)."""
        cliente, erro = _get_cliente_from_header()
        if erro:
            return {'erro': erro}, 403

        data = request.get_json() or {}
        for field in ('id_jogo', 'dias_alugados', 'data_inicio', 'tipo_midia'):
            if data.get(field) in (None, ''):
                return {'erro': f"O campo '{field}' é obrigatório."}, 400

        try:
            data_inicio = datetime.strptime(
                data['data_inicio'], '%Y-%m-%d'
            ).date()
        except ValueError:
            return {
                'erro': 'Formato de data_inicio inválido. Use AAAA-MM-DD.',
            }, 400

        try:
            aluguel = container.aluguel_service.solicitar(
                cliente=cliente,
                id_jogo=int(data['id_jogo']),
                dias_alugados=int(data['dias_alugados']),
                data_inicio=data_inicio,
                tipo_midia=data['tipo_midia'],
            )
        except ValueError as exc:
            return {'erro': str(exc)}, 400
        except Exception:  # noqa: BLE001
            logger.exception('Erro ao solicitar aluguel')
            return {'erro': 'Erro interno ao processar solicitação.'}, 500

        logger.info(
            'Cliente ID %s solicitou aluguel ID %s.', cliente.id, aluguel.id,
        )
        return {
            'mensagem': 'Aluguel solicitado com sucesso!',
            'aluguel': _serialize_aluguel(aluguel),
        }, 201


@alugueis_ns.route('/meus-alugueis')
class MeusAlugueisResource(Resource):
    def get(self):
        """Lista os aluguéis do cliente autenticado pelo header."""
        cliente, erro = _get_cliente_from_header()
        if erro:
            return {'erro': erro}, 403

        alugueis = container.aluguel_service.listar_por_cliente(cliente.id)
        return [_serialize_aluguel(a) for a in alugueis], 200


@alugueis_ns.route('/<int:id>')
class DetalhesAluguelResource(Resource):
    def get(self, id):
        """Detalhes de um aluguel (apenas dono pode consultar)."""
        cliente, erro = _get_cliente_from_header()
        if erro:
            return {'erro': erro}, 403

        aluguel = container.aluguel_service.obter(id, cliente.id)
        if not aluguel:
            return {
                'erro': 'Aluguel não encontrado ou não pertence a este cliente.',
            }, 404
        return _serialize_aluguel(aluguel), 200


@alugueis_ns.route('/<int:id>/cancelar')
class CancelarAluguelResource(Resource):
    def patch(self, id):
        """Cancela um aluguel (SOLICITADO ou APROVADO)."""
        cliente, erro = _get_cliente_from_header()
        if erro:
            return {'erro': erro}, 403

        try:
            aluguel = container.aluguel_service.cancelar(id, cliente.id)
        except LookupError as exc:
            return {'erro': str(exc)}, 404
        except ValueError as exc:
            return {'erro': str(exc)}, 400

        logger.info(
            'Cliente ID %s cancelou o aluguel ID %s.', cliente.id, id,
        )
        return {
            'mensagem': 'Aluguel cancelado com sucesso.',
            'aluguel': _serialize_aluguel(aluguel),
        }, 200


@alugueis_ns.route('/<int:id>/renovar')
class RenovarAluguelResource(Resource):
    @alugueis_ns.expect(aluguel_renovacao_model)
    def patch(self, id):
        """Renova um aluguel ativo por mais N dias."""
        cliente, erro = _get_cliente_from_header()
        if erro:
            return {'erro': erro}, 403

        data = request.get_json() or {}
        if 'dias_adicionais' not in data:
            return {'erro': "O campo 'dias_adicionais' é obrigatório."}, 400
        try:
            dias_adicionais = int(data['dias_adicionais'])
        except (TypeError, ValueError):
            return {'erro': "'dias_adicionais' deve ser inteiro."}, 400

        try:
            aluguel = container.aluguel_service.renovar(
                id, cliente.id, dias_adicionais,
            )
        except LookupError as exc:
            return {'erro': str(exc)}, 404
        except ValueError as exc:
            return {'erro': str(exc)}, 400

        return {
            'mensagem': 'Aluguel renovado com sucesso.',
            'aluguel': _serialize_aluguel(aluguel),
        }, 200


@alugueis_ns.route('/<int:id>/aprovar')
class AprovarAluguelResource(Resource):
    def patch(self, id):
        """Funcionário aprova um aluguel SOLICITADO."""
        funcionario, erro = _get_funcionario_from_header()
        if erro:
            return {'erro': erro}, 403

        try:
            aluguel = container.aluguel_service.aprovar(id, funcionario)
        except LookupError as exc:
            return {'erro': str(exc)}, 404
        except ValueError as exc:
            return {'erro': str(exc)}, 400

        logger.info(
            'Funcionário ID %s aprovou aluguel ID %s.', funcionario.id, id,
        )
        return _serialize_aluguel(aluguel), 200


@alugueis_ns.route('/<int:id>/retirada')
class RegistrarRetiradaAluguelResource(Resource):
    def patch(self, id):
        """Funcionário registra a retirada física/digital do item."""
        funcionario, erro = _get_funcionario_from_header()
        if erro:
            return {'erro': erro}, 403

        try:
            aluguel = container.aluguel_service.registrar_retirada(
                id, funcionario,
            )
        except LookupError as exc:
            return {'erro': str(exc)}, 404
        except ValueError as exc:
            return {'erro': str(exc)}, 400

        logger.info(
            'Funcionário ID %s registrou retirada do aluguel %s.',
            funcionario.id, id,
        )
        return {
            'mensagem': 'Retirada registrada com sucesso.',
            'aluguel': _serialize_aluguel(aluguel),
        }, 200


@alugueis_ns.route('/<int:id>/devolucao')
class RegistrarDevolucaoAluguelResource(Resource):
    @alugueis_ns.expect(aluguel_devolucao_model)
    def patch(self, id):
        """Funcionário registra a devolução do item (calcula multa)."""
        funcionario, erro = _get_funcionario_from_header()
        if erro:
            return {'erro': erro}, 403

        data = request.get_json() or {}
        condicao = data.get('condicao_item')

        try:
            aluguel, multa = container.aluguel_service.registrar_devolucao(
                id, condicao, funcionario,
            )
        except LookupError as exc:
            return {'erro': str(exc)}, 404
        except ValueError as exc:
            return {'erro': str(exc)}, 400

        logger.info(
            'Funcionário ID %s registrou devolução do aluguel %s '
            '(condição=%s, dias_atraso=%s, multa=%s).',
            funcionario.id, id, aluguel.condicao_item,
            aluguel.dias_atraso, multa.valor,
        )
        return {
            'mensagem': 'Devolução registrada com sucesso.',
            'aluguel': _serialize_aluguel(aluguel),
            'multa': _multa_to_dict(multa),
        }, 200
