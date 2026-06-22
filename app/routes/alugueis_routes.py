import logging
from datetime import datetime, date
from flask import request
from flask_restx import Namespace, Resource, fields

from app.models import Aluguel, ItemTransacao, Comprovante, Exemplar
from app.container.container import container

# Namespace e Modelos
alugueis_ns = Namespace('alugueis', description='Operações relacionadas a aluguéis', path='/api/alugueis')

item_transacao_model = alugueis_ns.model('ItemTransacao', {
    'id_item': fields.Integer,
    'id_exemplar': fields.Integer,
    'titulo_jogo': fields.String,
    'valor_diaria': fields.Float,
})

comprovante_model = alugueis_ns.model('Comprovante', {
    'id_comprovante': fields.Integer,
    'tipo_comprovante': fields.String,
    'data_emissao': fields.DateTime,
})

aluguel_model = alugueis_ns.model('Aluguel', {
    'id_transacao': fields.Integer,
    'id_cliente': fields.Integer,
    'cliente_nome': fields.String,
    'status_aluguel': fields.String,
    'valor_total': fields.Float,
    'data_transacao': fields.DateTime,
    'data_retirada': fields.DateTime,
    'data_prevista_devolucao': fields.Date,
    'itens': fields.List(fields.Nested(item_transacao_model)),
    'comprovantes': fields.List(fields.Nested(comprovante_model)),
})

aluguel_solicitacao_model = alugueis_ns.model('AluguelSolicitacao', {
    'id_catalogo': fields.Integer(required=True),
    'dias_alugados': fields.Integer(required=True),
    'data_inicio': fields.String(required=True, description='YYYY-MM-DD'),
    'tipo_midia': fields.String(required=True, enum=['FISICA', 'DIGITAL'])
})

aluguel_devolucao_model = alugueis_ns.model('AluguelDevolucao', {
    'condicao_item': fields.String(required=True, description='bom, danificado, extraviado')
})

aluguel_renovacao_model = alugueis_ns.model('AluguelRenovacao', {
    'dias_adicionais': fields.Integer(required=True, min=1)
})

pagamento_model = alugueis_ns.model('Pagamento', {
    'sucesso': fields.Boolean(required=True)
})

logger = logging.getLogger(__name__)

# Funções Auxiliares
def _serialize_item(item: ItemTransacao):
    exemplar = container.aluguel_repository.get_exemplar_by_id(item.id_exemplar)
    titulo = exemplar.catalogo.titulo if exemplar and exemplar.catalogo else "N/A"
    return {
        "id_item": item.id,
        "id_exemplar": item.id_exemplar,
        "titulo_jogo": titulo,
        "valor_diaria": float(item.valor_unitario) if item.valor_unitario else None,
    }

def _serialize_comprovante(comprovante: Comprovante):
    return {
        "id_comprovante": comprovante.id,
        "tipo_comprovante": comprovante.tipo_comprovante,
        "data_emissao": comprovante.data_envio.isoformat() if comprovante.data_envio else None,
    }

def serialize_aluguel_completo(aluguel: Aluguel):
    cliente = container.usuario_service.get_cliente_by_id(aluguel.id_cliente)
    return {
        "id_transacao": aluguel.id,
        "id_cliente": aluguel.id_cliente,
        "cliente_nome": cliente.nome if cliente else "N/A",
        "status_aluguel": aluguel.status,
        "valor_total": float(aluguel.valor_total) if aluguel.valor_total else None,
        "data_transacao": aluguel.data_transacao.isoformat(),
        "data_retirada": aluguel.data_retirada.isoformat() if aluguel.data_retirada else None,
        "data_prevista_devolucao": aluguel.data_prevista_devolucao.isoformat() if aluguel.data_prevista_devolucao else None,
        "itens": [_serialize_item(item) for item in aluguel.itens_transacao],
        "comprovantes": [_serialize_comprovante(comp) for comp in aluguel.comprovantes],
    }

def _get_cliente_from_header():
    cliente_id = request.headers.get('X-Cliente-Id')
    if not cliente_id: alugueis_ns.abort(403, "Header X-Cliente-Id é obrigatório.")
    cliente = container.usuario_service.get_cliente_by_id(int(cliente_id))
    if not cliente: alugueis_ns.abort(403, "Cliente não encontrado.")
    return cliente

def _get_funcionario_from_header():
    func_id = request.headers.get('X-Funcionario-Id') or request.headers.get('X-Admin-Id')
    if not func_id: alugueis_ns.abort(403, "Header X-Funcionario-Id é obrigatório.")
    funcionario = container.usuario_service.get_funcionario_by_id(int(func_id))
    if not funcionario: alugueis_ns.abort(403, "Funcionário não encontrado.")
    return funcionario

# Endpoints
@alugueis_ns.route('/solicitar')
class SolicitarAluguel(Resource):
    @alugueis_ns.expect(aluguel_solicitacao_model)
    @alugueis_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    def post(self):
        cliente = _get_cliente_from_header()
        data = request.get_json()
        aluguel, erro = container.aluguel_service.solicitar_aluguel(
            cliente.id, data['id_catalogo'], data['dias_alugados'], 
            datetime.strptime(data['data_inicio'], '%Y-%m-%d').date(), data['tipo_midia'].upper()
        )
        if erro: alugueis_ns.abort(400, erro)
        return {"mensagem": "Aluguel solicitado!", "aluguel": serialize_aluguel_completo(aluguel)}, 201

@alugueis_ns.route('/<int:id>/pagamento')
class Pagamento(Resource):
    @alugueis_ns.expect(pagamento_model)
    @alugueis_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    def patch(self, id):
        _get_cliente_from_header()
        aluguel, erro = container.aluguel_service.processar_pagamento(id, request.get_json()['sucesso'])
        if erro: alugueis_ns.abort(400, erro)
        return serialize_aluguel_completo(aluguel)

@alugueis_ns.route('/<int:id>/pagamento/recusar')
class PagamentoRecusado(Resource):
    @alugueis_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    def patch(self, id):
        _get_cliente_from_header()
        aluguel, erro = container.aluguel_service.pagamento_recusado(id)
        if erro: alugueis_ns.abort(400, erro)
        return serialize_aluguel_completo(aluguel)

@alugueis_ns.route('/<int:id>/retirada')
class Retirada(Resource):
    @alugueis_ns.doc(params={'X-Funcionario-Id': {'in': 'header', 'description': 'ID do funcionário (ou X-Admin-Id)', 'required': True}})
    def patch(self, id):
        _get_funcionario_from_header()
        aluguel, erro = container.aluguel_service.registrar_retirada(id)
        if erro: alugueis_ns.abort(400, erro)
        return serialize_aluguel_completo(aluguel)

@alugueis_ns.route('/<int:id>/devolucao')
class Devolucao(Resource):
    @alugueis_ns.expect(aluguel_devolucao_model)
    @alugueis_ns.doc(params={'X-Funcionario-Id': {'in': 'header', 'description': 'ID do funcionário (ou X-Admin-Id)', 'required': True}})
    def patch(self, id):
        funcionario = _get_funcionario_from_header()
        aluguel, erro = container.aluguel_service.registrar_devolucao(id, request.get_json()['condicao_item'], funcionario.id)
        if erro: alugueis_ns.abort(400, erro)
        return serialize_aluguel_completo(aluguel)

@alugueis_ns.route('/<int:id>/cancelar')
class Cancelar(Resource):
    @alugueis_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    def patch(self, id):
        cliente = _get_cliente_from_header()
        _, erro = container.aluguel_service.cancelar_aluguel(id, cliente.id)
        if erro: alugueis_ns.abort(400, erro)
        return {"mensagem": "Aluguel cancelado com sucesso."}

@alugueis_ns.route('/<int:id>/renovar')
class Renovar(Resource):
    @alugueis_ns.expect(aluguel_renovacao_model)
    @alugueis_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    def patch(self, id):
        cliente = _get_cliente_from_header()
        aluguel, erro = container.aluguel_service.renovar_aluguel(id, cliente.id, request.get_json()['dias_adicionais'])
        if erro: alugueis_ns.abort(400, erro)
        return {"aluguel": serialize_aluguel_completo(aluguel)}
