import logging
from datetime import datetime, date
from flask import request
from flask_restx import Namespace, Resource, fields
from sqlalchemy.exc import IntegrityError
from sqlalchemy import not_, or_

from app.models import Cliente
from app.container.container import container

# Criar namespace para vendas
vendas_ns = Namespace('vendas', description='Operações relacionadas às vendas de jogos', path='/api/vendas')

# Modelos para documentação Swagger
venda_model = vendas_ns.model('Venda', {
    'id': fields.Integer(description='ID da venda'),
    'id_cliente': fields.Integer(description='ID do cliente'),
    'data_transacao': fields.Date(description='Data da transação'),
    'valor_total': fields.Float(description='Valor total'),
    'status': fields.String(description='Status da venda')
})

venda_solicitacao_model = vendas_ns.model('VendaSolicitacao', {
    'id_catalogo': fields.Integer(required=True, description='ID do catálogo do jogo'),
    'tipo_midia': fields.String(required=True, description='Tipo de mídia (FISICO ou DIGITAL)')
})

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_cliente_from_header():
    cliente_id = request.headers.get('X-Cliente-Id')
    if not cliente_id:
        return None, "Header X-Cliente-Id é obrigatório."
    try:
        cliente_id = int(cliente_id)
    except ValueError:
        return None, "X-Cliente-Id inválido."
    
    cliente = container.usuario_service.get_cliente_by_id(cliente_id)
    if not cliente:
        return None, "Cliente não cadastrado ou não encontrado."
    
    return cliente, None




@vendas_ns.route('/solicitar')
class SolicitarVendaResource(Resource):
    @vendas_ns.expect(venda_solicitacao_model)
    @vendas_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    def post(self):
        try:
            cliente, erro = get_cliente_from_header()
            if erro: return {"erro": erro}, 403

            data = request.get_json()
            if not data: return {"erro": "Dados não fornecidos."}, 400

            required_fields = ['id_catalogo', 'tipo_midia']
            for field in required_fields:
                if field not in data or str(data[field]).strip() == "":
                    return {"erro": f"O campo '{field}' é obrigatório."}, 400

            venda, erro = container.venda_service.criar_venda(
                cliente_id=cliente.id,
                id_catalogo=data['id_catalogo'],
                tipo_midia=data['tipo_midia']
            )
            
            if erro:
                return {"erro": erro}, 400

            logger.info(f"Cliente ID {cliente.id} COMPROU o catalogo ID {data['id_catalogo']}.")
            return {
                "mensagem": "Venda realizada com sucesso.",
                "id_transacao": venda.id,
                "valor_total": float(venda.valor_total) if venda.valor_total else None
            }, 201

        except Exception as e:
            return {"erro": f"Erro interno: {str(e)}"}, 500

@vendas_ns.route('/minhas-vendas')
class MinhasVendasResource(Resource):
    @vendas_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    def get(self):
        try:
            cliente, erro = get_cliente_from_header()
            if erro: return {"erro": erro}, 403

            vendas = container.venda_service.get_by_cliente(cliente.id)
            return [container.venda_service.serialize_venda(v) for v in vendas], 200

        except Exception as e:
            return {"erro": str(e)}, 500

@vendas_ns.route('/<int:id>')
class DetalhesVendaResource(Resource):
    @vendas_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    def get(self, id):
        try:
            cliente, erro = get_cliente_from_header()
            if erro: return {"erro": erro}, 403

            venda = container.venda_service.get_by_id(id)
            if not venda or venda.id_cliente != cliente.id:
                return {"erro": "Venda não encontrada ou não pertence a este cliente."}, 404

            return container.venda_service.serialize_venda(venda), 200

        except Exception as e:
            return {"erro": str(e)}, 500

@vendas_ns.route('/<int:id>/cancelar')
class EstornarVendaResource(Resource):
    @vendas_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    def patch(self, id):
        try:
            cliente, erro = get_cliente_from_header()
            if erro: return {"erro": erro}, 403

            success, erro = container.venda_service.estornar_venda(id, cliente.id)
            if erro:
                return {"erro": erro}, 400

            logger.info(f"Cliente ID {cliente.id} SOLICITOU ESTORNO da venda ID {id}.")
            return {"mensagem": "Venda estornada com sucesso."}, 200

        except Exception as e:
            return {"erro": str(e)}, 500
