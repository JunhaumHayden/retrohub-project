import logging
from datetime import datetime, timedelta, date
from flask import request
from flask_restx import Namespace, Resource, fields

from app.models import (
    Cliente, Catalogo, Exemplar, MidiaFisica, MidiaDigital,
    Transacao, Aluguel, Venda, ItemTransacao, Funcionario, Comprovante
)
from app.container.container import container

# Criar namespace para aluguéis
alugueis_ns = Namespace('alugueis', description='Operações relacionadas aos aluguéis de jogos', path='/api/alugueis')

# --- Modelos para documentação Swagger ---

item_transacao_model = alugueis_ns.model('ItemTransacao', {
    'id_item': fields.Integer(description='ID do item da transação'),
    'id_exemplar': fields.Integer(description='ID do exemplar alugado'),
    'titulo_jogo': fields.String(description='Título do jogo'),
    'valor_diaria': fields.Float(description='Valor da diária do item'),
})

comprovante_model = alugueis_ns.model('Comprovante', {
    'id_comprovante': fields.Integer(description='ID do comprovante'),
    'tipo_comprovante': fields.String(description='Tipo do comprovante (ex: DEVOLUCAO)'),
    'data_emissao': fields.DateTime(description='Data e hora de emissão do comprovante'),
})

aluguel_model = alugueis_ns.model('Aluguel', {
    'id_transacao': fields.Integer(description='ID do aluguel'),
    'id_cliente': fields.Integer(description='ID do cliente'),
    'cliente_nome': fields.String(description='Nome do cliente'),
    'id_funcionario_recebimento': fields.Integer(description='ID do funcionário que registrou a devolução'),
    'funcionario_recebimento_nome': fields.String(description='Nome do funcionário que registrou a devolução'),
    'status_aluguel': fields.String(description='Status atual do aluguel'),
    'valor_total': fields.Float(description='Valor total do aluguel'),
    'data_transacao': fields.DateTime(description='Data da solicitação'),
    'data_retirada': fields.DateTime(description='Data da retirada'),
    'data_prevista_devolucao': fields.Date(description='Data de devolução prevista'),
    'data_devolucao_real': fields.DateTime(description='Data de devolução real'),
    'multa_aplicada': fields.Float(description='Multa por atraso'),
    'dias_atraso': fields.Integer(description='Dias de atraso na devolução'),
    'itens': fields.List(fields.Nested(item_transacao_model), description='Itens incluídos no aluguel'),
    'comprovantes': fields.List(fields.Nested(comprovante_model), description='Comprovantes associados ao aluguel'),
})

aluguel_solicitacao_model = alugueis_ns.model('AluguelSolicitacao', {
    'id_jogo': fields.Integer(required=True, description='ID do jogo no catálogo'),
    'dias_alugados': fields.Integer(required=True, description='Período do aluguel em dias (1-30)'),
    'data_inicio': fields.String(required=True, description='Data de início do aluguel (YYYY-MM-DD)'),
    'tipo_midia': fields.String(required=True, description='Tipo de mídia (FISICA ou DIGITAL)')
})

aluguel_devolucao_model = alugueis_ns.model('AluguelDevolucao', {
    'condicao_item': fields.String(required=True, description='Condição do item devolvido (bom, danificado, extraviado)')
})

aluguel_renovacao_model = alugueis_ns.model('AluguelRenovacao', {
    'dias_adicionais': fields.Integer(required=True, description='Número de dias adicionais (1-30)')
})

# --- Configuração de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Funções Auxiliares de Serialização ---

def _serialize_item(item: ItemTransacao):
    """Serializa um ItemTransacao, buscando informações do exemplar e catálogo."""
    exemplar = container.data_source.get_by_id(Exemplar, item.id_exemplar)
    titulo = "Título não encontrado"
    valor_diaria = None
    if exemplar:
        catalogo = container.catalogo_service.get_by_id(exemplar.id_catalogo)
        if catalogo:
            titulo = catalogo.titulo
        
        vd_aluguel = getattr(exemplar, 'valor_diaria_aluguel', None)
        if vd_aluguel is not None:
            try:
                valor_diaria = float(vd_aluguel)
            except (TypeError, ValueError):
                valor_diaria = None

    return {
        "id_item": item.id,
        "id_exemplar": item.id_exemplar,
        "titulo_jogo": titulo,
        "valor_diaria": valor_diaria,
    }

def _serialize_comprovante(comprovante: Comprovante):
    """Serializa um objeto Comprovante."""
    return {
        "id_comprovante": comprovante.id,
        "tipo_comprovante": comprovante.tipo_comprovante,
        "data_emissao": comprovante.data_envio.isoformat() if comprovante.data_envio else None,
    }

def serialize_aluguel_completo(aluguel: Aluguel):
    """Serializa um objeto Aluguel com todos os seus relacionamentos."""
    itens_do_aluguel = getattr(aluguel, 'itens_transacao', [])
    comprovantes_do_aluguel = getattr(aluguel, 'comprovantes', [])

    cliente = container.usuario_service.get_cliente_by_id(aluguel.id_cliente) if aluguel.id_cliente else None
    cliente_nome = getattr(cliente, 'nome', "Não encontrado")

    id_func_recebimento = getattr(aluguel, "id_funcionario_recebimento", None)
    funcionario_recebimento = container.usuario_service.get_funcionario_by_id(id_func_recebimento) if id_func_recebimento else None
    funcionario_recebimento_nome = getattr(funcionario_recebimento, 'nome', None)

    multa_obj = aluguel.get_multa()
    multa_valor = getattr(multa_obj, "valor", None)
    multa_aplicada_float = float(multa_valor) if multa_valor is not None else None

    return {
        "id_transacao": aluguel.id,
        "id_cliente": aluguel.id_cliente,
        "cliente_nome": cliente_nome,
        "id_funcionario_recebimento": id_func_recebimento,
        "funcionario_recebimento_nome": funcionario_recebimento_nome,
        "status_aluguel": aluguel.status,
        "valor_total": float(aluguel.valor_total) if aluguel.valor_total else None,
        "data_transacao": aluguel.data_transacao.isoformat() if aluguel.data_transacao else None,
        "periodo_dias": aluguel.periodo,
        "data_inicio": aluguel.data_inicio.isoformat() if aluguel.data_inicio else None,
        "data_prevista_devolucao": aluguel.data_prevista_devolucao.isoformat() if aluguel.data_prevista_devolucao else None,
        "data_devolucao_real": aluguel.data_devolucao_real.isoformat() if getattr(aluguel, "data_devolucao_real", None) else None,
        "data_retirada": aluguel.data_retirada.isoformat() if getattr(aluguel, 'data_retirada', None) else None,
        "condicao_item": getattr(aluguel, "condicao_item", None),
        "multa_aplicada": multa_aplicada_float,
        "multa_paga": aluguel.multa_paga,
        "dias_atraso": aluguel.dias_atraso,
        "itens": [_serialize_item(item) for item in itens_do_aluguel],
        "comprovantes": [_serialize_comprovante(comp) for comp in comprovantes_do_aluguel],
    }

# --- Funções de Autorização ---

def _get_cliente_from_header():
    cliente_id = request.headers.get('X-Cliente-Id')
    if not cliente_id:
        alugueis_ns.abort(403, "Header X-Cliente-Id é obrigatório.")
    try:
        cliente = container.usuario_service.get_cliente_by_id(int(cliente_id))
        if not cliente:
            alugueis_ns.abort(403, "Cliente não cadastrado ou não encontrado.")
        return cliente
    except ValueError:
        alugueis_ns.abort(403, "X-Cliente-Id inválido.")

def _get_funcionario_from_header():
    func_id = request.headers.get('X-Funcionario-Id') or request.headers.get('X-Admin-Id')
    if not func_id:
        alugueis_ns.abort(403, "Header X-Funcionario-Id (ou X-Admin-Id) é obrigatório.")
    try:
        funcionario = container.usuario_service.get_funcionario_by_id(int(func_id))
        if not funcionario:
            alugueis_ns.abort(403, "Funcionário não encontrado.")
        return funcionario
    except ValueError:
        alugueis_ns.abort(403, "O ID do funcionário deve ser um número inteiro.")

# --- Endpoints ---

@alugueis_ns.route('/solicitar')
class SolicitarAluguelResource(Resource):
    @alugueis_ns.expect(aluguel_solicitacao_model)
    @alugueis_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    def post(self):
        """Solicitar um novo aluguel"""
        cliente = _get_cliente_from_header()
        data = request.get_json()
        if not data:
            alugueis_ns.abort(400, "Dados não fornecidos.")

        required = ['id_jogo', 'dias_alugados', 'data_inicio', 'tipo_midia']
        if any(f not in data or str(data[f]).strip() == "" for f in required):
            alugueis_ns.abort(400, f"Campos obrigatórios: {', '.join(required)}.")

        try:
            dias_alugados = int(data['dias_alugados'])
            data_inicio = datetime.strptime(data['data_inicio'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            alugueis_ns.abort(400, "Formato de data ou dias inválido.")

        if not (1 <= dias_alugados <= 30):
            alugueis_ns.abort(400, "O período de aluguel deve ser entre 1 e 30 dias.")
        if data_inicio < date.today():
            alugueis_ns.abort(400, "A data de início não pode ser no passado.")

        tipo_midia = str(data['tipo_midia']).upper()
        if tipo_midia not in ['FISICA', 'DIGITAL']:
            alugueis_ns.abort(400, "tipo_midia deve ser FISICA ou DIGITAL.")

        aluguel, erro = container.aluguel_service.solicitar_aluguel(
            id_cliente=cliente.id,
            id_jogo=data['id_jogo'],
            dias_alugados=dias_alugados,
            data_inicio=data_inicio,
            tipo_midia=tipo_midia
        )

        if erro:
            code = 404 if "não existe" in erro.lower() else 400
            alugueis_ns.abort(code, erro)

        exemplar_id = None
        if aluguel and hasattr(aluguel, 'itens_transacao') and aluguel.itens_transacao:
            exemplar_id = aluguel.itens_transacao[0].id_exemplar

        logger.info(f"Cliente ID {cliente.id} solicitou aluguel com sucesso.")
        return {
            "mensagem": "Aluguel solicitado com sucesso!",
            "aluguel": serialize_aluguel_completo(aluguel),
            "exemplar_id": exemplar_id
        }, 201

@alugueis_ns.route('/meus-alugueis')
class MeusAlugueisResource(Resource):
    @alugueis_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    @alugueis_ns.marshal_list_with(aluguel_model)
    def get(self):
        """Listar meus aluguéis"""
        cliente = _get_cliente_from_header()
        alugueis = container.data_source.get_all(Aluguel)
        meus_alugueis = [a for a in alugueis if getattr(a, 'id_cliente', None) == cliente.id]
        return [serialize_aluguel_completo(a) for a in meus_alugueis]

@alugueis_ns.route('/<int:id>')
class DetalhesAluguelResource(Resource):
    @alugueis_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    @alugueis_ns.marshal_with(aluguel_model)
    def get(self, id):
        """Obter detalhes de um aluguel"""
        cliente = _get_cliente_from_header()
        aluguel = container.aluguel_service.repo.get_by_id(id)
        if not aluguel or getattr(aluguel, 'id_cliente', None) != cliente.id:
            alugueis_ns.abort(404, "Aluguel não encontrado ou não pertence a este cliente.")
        return serialize_aluguel_completo(aluguel)

@alugueis_ns.route('/<int:id>/retirada')
class RegistrarRetiradaAluguelResource(Resource):
    @alugueis_ns.doc(params={'X-Funcionario-Id': {'in': 'header', 'description': 'ID do funcionário', 'required': True}})
    @alugueis_ns.marshal_with(aluguel_model)
    def patch(self, id):
        """Registrar retirada de aluguel"""
        _get_funcionario_from_header()
        aluguel, err = container.aluguel_service.registrar_retirada(id)
        if err:
            alugueis_ns.abort(400, err)
        logger.info(f"Funcionário registrou retirada do aluguel ID {id}")
        return serialize_aluguel_completo(aluguel)

@alugueis_ns.route('/<int:id>/devolucao')
class RegistrarDevolucaoAluguelResource(Resource):
    @alugueis_ns.expect(aluguel_devolucao_model)
    @alugueis_ns.doc(params={'X-Funcionario-Id': {'in': 'header', 'description': 'ID do funcionário', 'required': True}})
    @alugueis_ns.marshal_with(aluguel_model)
    def patch(self, id):
        """Registrar devolução de aluguel"""
        funcionario = _get_funcionario_from_header()
        data = request.get_json()
        condicao = data.get("condicao_item") if data else None
        if not condicao:
            alugueis_ns.abort(400, "O campo 'condicao_item' é obrigatório.")
        
        aluguel, err = container.aluguel_service.registrar_devolucao(id, condicao, funcionario.id)
        if err:
            code = 404 if "não encontrado" in err.lower() else 400
            alugueis_ns.abort(code, err)

        logger.info(f"Devolução registrada para aluguel ID {id}.")
        return serialize_aluguel_completo(aluguel)

@alugueis_ns.route('/<int:id>/cancelar')
class CancelarAluguelResource(Resource):
    @alugueis_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    def patch(self, id):
        """Cancelar um aluguel"""
        cliente = _get_cliente_from_header()
        aluguel, erro = container.aluguel_service.cancelar_aluguel(id, cliente.id)
        
        if erro:
            code = 404 if "não encontrado" in erro.lower() else 400
            alugueis_ns.abort(code, erro)

        logger.info(f"Cliente ID {cliente.id} cancelou aluguel ID {id}")
        return {"mensagem": "Aluguel cancelado com sucesso."}, 200

@alugueis_ns.route('/<int:id>/renovar')
class RenovarAluguelResource(Resource):
    @alugueis_ns.expect(aluguel_renovacao_model)
    @alugueis_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    def patch(self, id):
        """Renovar um aluguel"""
        cliente = _get_cliente_from_header()
        data = request.get_json()
        dias_adicionais = data.get('dias_adicionais') if data else None
        
        if not isinstance(dias_adicionais, int) or not (1 <= dias_adicionais <= 30):
            alugueis_ns.abort(400, "O período de renovação ('dias_adicionais') deve ser entre 1 e 30 dias.")

        aluguel, erro = container.aluguel_service.renovar_aluguel(id, cliente.id, dias_adicionais)
        
        if erro:
            code = 404 if "não encontrado" in erro.lower() else 400
            alugueis_ns.abort(code, erro)

        logger.info(f"Cliente ID {cliente.id} renovou aluguel ID {aluguel.id} por mais {dias_adicionais} dias.")
        return {
            "mensagem": "Aluguel renovado com sucesso.",
            "nova_data_devolucao": aluguel.data_prevista_devolucao.isoformat(),
            "novo_valor_total": float(aluguel.valor_total)
        }, 200
