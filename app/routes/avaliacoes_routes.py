import logging
from flask import request
from flask_restx import Namespace, Resource, fields

from app.container.container import container
from app.models import Avaliacao

avaliacoes_ns = Namespace('avaliacoes', description='Operações relacionadas a avaliações de transações', path='/api/avaliacoes')

avaliacao_model = avaliacoes_ns.model('Avaliacao', {
    'id': fields.Integer(description='ID da avaliação'),
    'id_transacao': fields.Integer(description='ID da transação avaliada'),
    'nota': fields.Integer(description='Nota (1 a 5)'),
    'comentario': fields.String(description='Comentário opcional'),
    'data_avaliacao': fields.Date(description='Data da avaliação'),
})

avaliacao_input_model = avaliacoes_ns.model('AvaliacaoInput', {
    'nota': fields.Integer(required=True, description='Nota da avaliação (1 a 5)'),
    'comentario': fields.String(description='Comentário opcional'),
})

logger = logging.getLogger(__name__)

def _serialize_avaliacao(avaliacao: Avaliacao):
    return {
        "id": avaliacao.id,
        "id_transacao": avaliacao.id_transacao,
        "nota": avaliacao.nota,
        "comentario": avaliacao.comentario,
        "data_avaliacao": avaliacao.data_avaliacao.isoformat() if avaliacao.data_avaliacao else None,
    }

def _get_cliente_from_header():
    cliente_id = request.headers.get('X-Cliente-Id')
    if not cliente_id:
        avaliacoes_ns.abort(403, "Header X-Cliente-Id é obrigatório.")
    try:
        cliente = container.usuario_service.get_cliente_by_id(int(cliente_id))
        if not cliente:
            avaliacoes_ns.abort(403, "Cliente não encontrado.")
        return cliente
    except ValueError:
        avaliacoes_ns.abort(403, "X-Cliente-Id inválido.")

@avaliacoes_ns.route('/<int:id_transacao>')
class AvaliacaoResource(Resource):
    @avaliacoes_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    @avaliacoes_ns.expect(avaliacao_input_model)
    @avaliacoes_ns.marshal_with(avaliacao_model, code=201)
    def post(self, id_transacao):
        """Cria uma nova avaliação para uma transação."""
        cliente = _get_cliente_from_header()
        data = request.get_json()
        
        try:
            nova_avaliacao = container.avaliacao_service.criar_avaliacao(
                id_cliente=cliente.id,
                id_transacao=id_transacao,
                nota=data.get('nota'),
                comentario=data.get('comentario')
            )
            return _serialize_avaliacao(nova_avaliacao), 201
        except (ValueError, PermissionError) as e:
            avaliacoes_ns.abort(400, str(e))
        except Exception as e:
            logger.error(f"Erro ao criar avaliação: {e}")
            avaliacoes_ns.abort(500, "Erro interno ao processar a avaliação.")

@avaliacoes_ns.route('/minhas')
class MinhasAvaliacoesResource(Resource):
    @avaliacoes_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    @avaliacoes_ns.marshal_list_with(avaliacao_model)
    def get(self):
        """Lista todas as avaliações feitas pelo cliente."""
        cliente = _get_cliente_from_header()
        avaliacoes = container.avaliacao_service.get_avaliacoes_por_cliente(cliente.id)
        return [_serialize_avaliacao(av) for av in avaliacoes]

@avaliacoes_ns.route('/jogo/<int:id_catalogo>')
class AvaliacoesJogoResource(Resource):
    @avaliacoes_ns.marshal_list_with(avaliacao_model)
    def get(self, id_catalogo):
        """Lista todas as avaliações para um determinado jogo."""
        avaliacoes = container.avaliacao_service.get_avaliacoes_por_jogo(id_catalogo)
        return [_serialize_avaliacao(av) for av in avaliacoes]
