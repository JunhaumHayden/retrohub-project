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

# --- Funções Auxiliares ---

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

def get_funcionario_from_header():
    func_id = request.headers.get('X-Funcionario-Id') or request.headers.get('X-Admin-Id')
    if not func_id:
        return None, "Header X-Funcionario-Id (ou X-Admin-Id) é obrigatório."
    try:
        func_id = int(func_id)
    except ValueError:
        return None, "O ID do funcionário deve ser um número inteiro."
    
    funcionario = container.usuario_service.get_funcionario_by_id(func_id)
    if not funcionario:
        return None, "Funcionário não encontrado."
    return funcionario, None

def find_exemplar_disponivel(id_catalogo, tipo_midia):
    """Find available exemplar for rental"""
    exemplares = container.data_source.get_all(Exemplar)
    alugueis = container.data_source.get_all(Aluguel)
    vendas = container.data_source.get_all(Venda)
    itens_transacao = container.data_source.get_all(ItemTransacao)
    
    alugueis_ativos_ids = {a.id for a in alugueis if a.status in ['ATIVO', 'ATRASADO', 'SOLICITADO', 'APROVADO']}
    vendas_ids = {v.id for v in vendas if v.status == 'FINALIZADA'}
    
    exemplares_indisponiveis = {
        item.id_exemplar for item in itens_transacao 
        if item.id_transacao in alugueis_ativos_ids or item.id_transacao in vendas_ids
    }
    
    for exemplar in exemplares:
        if (exemplar.id_catalogo == id_catalogo and 
            exemplar.id not in exemplares_indisponiveis and
            (exemplar.situacao is None or exemplar.situacao == 'DISPONIVEL')):
            
            if tipo_midia == 'DIGITAL' and isinstance(exemplar, MidiaDigital):
                return exemplar
            if tipo_midia == 'FISICA' and isinstance(exemplar, MidiaFisica):
                return exemplar
    return None

def _multa_to_float(multa):
    if multa is None: return None
    valor = getattr(multa, "valor", multa)
    try:
        return float(valor) if valor is not None else None
    except (TypeError, ValueError):
        return None

def serialize_item(item: ItemTransacao):
    """Serializa um ItemTransacao, buscando informações do exemplar e catálogo."""
    exemplar = container.data_source.get_by_id(Exemplar, item.id_exemplar)
    titulo = "Título não encontrado"
    valor_diaria = None
    if exemplar:
        catalogo = container.catalogo_service.get_by_id(exemplar.id_catalogo)
        if catalogo:
            titulo = catalogo.titulo
        
        # Correção do erro TypeError: float() argument must be a string or a real number, not 'NoneType'
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

def serialize_comprovante(comprovante: Comprovante):
    """Serializa um objeto Comprovante."""
    return {
        "id_comprovante": comprovante.id,
        "tipo_comprovante": comprovante.tipo_comprovante,
        "data_emissao": comprovante.data_envio.isoformat() if comprovante.data_envio else None,
    }

def serialize_aluguel(aluguel: Aluguel):
    """Serializa um objeto Aluguel, incluindo nomes, itens e comprovantes."""
    # Usar as propriedades de navegação da própria entidade, em vez de buscar 
    # todos do banco, para evitar duplicidades geradas pelo mock data source
    itens_do_aluguel = getattr(aluguel, 'itens_transacao', [])
    comprovantes_do_aluguel = getattr(aluguel, 'comprovantes', [])

    # Busca nomes de cliente e funcionário
    cliente = container.usuario_service.get_cliente_by_id(aluguel.id_cliente) if aluguel.id_cliente else None
    cliente_nome = getattr(cliente, 'nome', "Não encontrado")

    id_func_recebimento = getattr(aluguel, "id_funcionario_recebimento", None)
    funcionario_recebimento = container.usuario_service.get_funcionario_by_id(id_func_recebimento) if id_func_recebimento else None
    funcionario_recebimento_nome = getattr(funcionario_recebimento, 'nome', None)

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
        "multa_aplicada": _multa_to_float(getattr(aluguel, "multa_aplicada", None)),
        "multa_paga": aluguel.multa_paga if getattr(aluguel, "multa_paga", None) is not None else None,
        "dias_atraso": getattr(aluguel, "dias_atraso", None),
        "itens": [serialize_item(item) for item in itens_do_aluguel],
        "comprovantes": [serialize_comprovante(comp) for comp in comprovantes_do_aluguel],
    }

# --- Endpoints ---

@alugueis_ns.route('/solicitar')
class SolicitarAluguelResource(Resource):
    @alugueis_ns.expect(aluguel_solicitacao_model)
    @alugueis_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    def post(self):
        """Solicitar um novo aluguel"""
        cliente, erro = get_cliente_from_header()
        if erro: return {"erro": erro}, 403

        data = request.get_json()
        if not data: return {"erro": "Dados não fornecidos."}, 400

        required = ['id_jogo', 'dias_alugados', 'data_inicio', 'tipo_midia']
        if any(f not in data or str(data[f]).strip() == "" for f in required):
            return {"erro": f"Campos obrigatórios: {', '.join(required)}."}, 400

        try:
            dias_alugados = int(data['dias_alugados'])
            data_inicio = datetime.strptime(data['data_inicio'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return {"erro": "Formato de data ou dias inválido."}, 400

        if not (1 <= dias_alugados <= 30):
            return {"erro": "O período de aluguel deve ser entre 1 e 30 dias."}, 400
        if data_inicio < date.today():
            return {"erro": "A data de início não pode ser no passado."}, 400

        jogo = container.catalogo_service.get_by_id(data['id_jogo'])
        if not jogo or getattr(jogo, 'situacao', None) != 'DISPONIVEL':
            return {"erro": "Jogo não existe ou está inativo."}, 404

        tipo_midia = str(data['tipo_midia']).upper()
        if tipo_midia not in ['FISICA', 'DIGITAL']:
            return {"erro": "tipo_midia deve ser FISICA ou DIGITAL."}, 400

        exemplar = find_exemplar_disponivel(jogo.id, tipo_midia)
        if not exemplar:
            return {"erro": f"Não há exemplares de mídia {tipo_midia} disponíveis."}, 400

        valor_diaria = getattr(exemplar, 'valor_diaria_aluguel', None)
        if not valor_diaria:
            return {"erro": "Jogo não disponível para aluguel (valor da diária não definido)."}, 400
        
        # Simulação de criação de aluguel (ambiente mock)
        novo_aluguel = Aluguel(
            id=len(container.data_source.get_all(Aluguel)) + 1,
            id_cliente=cliente.id_usuario,
            valor_total=valor_diaria * dias_alugados,
            status='SOLICITADO',
            periodo=dias_alugados,
            data_inicio=data_inicio,
            data_prevista_devolucao=data_inicio + timedelta(days=dias_alugados)
        )
        
        return {
            "mensagem": "Aluguel solicitado com sucesso!",
            "aluguel": serialize_aluguel(novo_aluguel),
            "exemplar_id": exemplar.id
        }, 201

@alugueis_ns.route('/meus-alugueis')
class MeusAlugueisResource(Resource):
    @alugueis_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    @alugueis_ns.marshal_list_with(aluguel_model)
    def get(self):
        """Listar meus aluguéis"""
        cliente, erro = get_cliente_from_header()
        if erro: alugueis_ns.abort(403, erro)

        alugueis = container.data_source.get_all(Aluguel)
        meus_alugueis = [a for a in alugueis if getattr(a, 'id_cliente', None) == cliente.id_usuario]
        return [serialize_aluguel(a) for a in meus_alugueis]

@alugueis_ns.route('/<int:id>')
class DetalhesAluguelResource(Resource):
    @alugueis_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    @alugueis_ns.marshal_with(aluguel_model)
    def get(self, id):
        """Obter detalhes de um aluguel"""
        cliente, erro = get_cliente_from_header()
        if erro: alugueis_ns.abort(403, erro)

        aluguel = container.data_source.get_by_id(Aluguel, id)
        if not aluguel or getattr(aluguel, 'id_cliente', None) != cliente.id_usuario:
            alugueis_ns.abort(404, "Aluguel não encontrado ou não pertence a este cliente.")
        return serialize_aluguel(aluguel)

@alugueis_ns.route('/<int:id>/retirada')
class RegistrarRetiradaAluguelResource(Resource):
    @alugueis_ns.doc(params={'X-Funcionario-Id': {'in': 'header', 'description': 'ID do funcionário', 'required': True}})
    @alugueis_ns.marshal_with(aluguel_model)
    def patch(self, id):
        """Registrar retirada de aluguel"""
        _, erro = get_funcionario_from_header()
        if erro: alugueis_ns.abort(403, erro)

        aluguel, err = container.aluguel_service.registrar_retirada(id)
        if err: alugueis_ns.abort(400, err)
        
        logger.info(f"Funcionário registrou retirada do aluguel ID {id}")
        return serialize_aluguel(aluguel)

@alugueis_ns.route('/<int:id>/devolucao')
class RegistrarDevolucaoAluguelResource(Resource):
    @alugueis_ns.expect(aluguel_devolucao_model)
    @alugueis_ns.doc(params={'X-Funcionario-Id': {'in': 'header', 'description': 'ID do funcionário', 'required': True}})
    @alugueis_ns.marshal_with(aluguel_model)
    def patch(self, id):
        """Registrar devolução de aluguel"""
        funcionario, erro = get_funcionario_from_header()
        if erro: alugueis_ns.abort(403, erro)

        data = request.get_json()
        condicao = data.get("condicao_item") if data else None
        if not condicao:
            alugueis_ns.abort(400, "O campo 'condicao_item' é obrigatório.")
        
        aluguel, err = container.aluguel_service.registrar_devolucao(id, condicao, funcionario.id_usuario)
        if err:
            code = 404 if "não encontrado" in err.lower() else 400
            alugueis_ns.abort(code, err)

        logger.info(f"Devolução registrada para aluguel ID {id}.")
        return serialize_aluguel(aluguel)

@alugueis_ns.route('/<int:id>/cancelar')
class CancelarAluguelResource(Resource):
    @alugueis_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    def patch(self, id):
        """Cancelar um aluguel"""
        cliente, erro = get_cliente_from_header()
        if erro: return {"erro": erro}, 403

        aluguel = container.data_source.get_by_id(Aluguel, id)
        if not aluguel or getattr(aluguel, 'id_cliente', None) != cliente.id_usuario:
            return {"erro": "Aluguel não encontrado ou não pertence a este cliente."}, 404

        if aluguel.status not in ['SOLICITADO', 'APROVADO']:
             return {"erro": f"Não é possível cancelar um aluguel com status '{aluguel.status}'."}, 400
        if aluguel.data_inicio <= date.today():
            return {"erro": "Não é possível cancelar um aluguel que já iniciou ou está no dia de retirada."}, 400

        aluguel.status = 'FINALIZADO'
        
        item_tr = next((it for it in container.data_source.get_all(ItemTransacao) if getattr(it, 'id_transacao', None) == aluguel.id), None)
        if item_tr:
            exemplar = container.data_source.get_by_id(Exemplar, item_tr.id_exemplar)
            if exemplar and exemplar.situacao == 'RESERVADO':
                exemplar.situacao = 'DISPONIVEL'

        logger.info(f"Cliente ID {cliente.id_usuario} cancelou aluguel ID {id}")
        return {"mensagem": "Aluguel cancelado com sucesso."}, 200

@alugueis_ns.route('/<int:id>/renovar')
class RenovarAluguelResource(Resource):
    @alugueis_ns.expect(aluguel_renovacao_model)
    @alugueis_ns.doc(params={'X-Cliente-Id': {'in': 'header', 'description': 'ID do cliente', 'required': True}})
    def patch(self, id):
        """Renovar um aluguel"""
        cliente, erro = get_cliente_from_header()
        if erro: return {"erro": erro}, 403

        data = request.get_json()
        dias_adicionais = data.get('dias_adicionais') if data else None
        if not isinstance(dias_adicionais, int) or not (1 <= dias_adicionais <= 30):
            return {"erro": "O período de renovação ('dias_adicionais') deve ser entre 1 e 30 dias."}, 400

        aluguel = container.data_source.get_by_id(Aluguel, id)
        if not aluguel or getattr(aluguel, 'id_cliente', None) != cliente.id_usuario:
            return {"erro": "Aluguel não encontrado ou não pertence a este cliente."}, 404

        if aluguel.status == 'FINALIZADO':
            return {"erro": "Não é possível renovar um aluguel já finalizado."}, 400

        item_transacao = next((it for it in container.data_source.get_all(ItemTransacao) if getattr(it, 'id_transacao', None) == aluguel.id), None)
        if not item_transacao: return {"erro": "Item da transação não encontrado."}, 404
            
        exemplar = container.data_source.get_by_id(Exemplar, item_transacao.id_exemplar)
        if not exemplar or not hasattr(exemplar, 'valor_diaria_aluguel'):
            return {"erro": "Exemplar ou valor da diária não encontrado."}, 404
            
        acrescimo = exemplar.valor_diaria_aluguel * dias_adicionais
        aluguel.periodo += dias_adicionais
        aluguel.data_prevista_devolucao += timedelta(days=dias_adicionais)
        aluguel.valor_total += acrescimo

        logger.info(f"Cliente ID {cliente.id_usuario} renovou aluguel ID {aluguel.id} por mais {dias_adicionais} dias.")
        return {
            "mensagem": "Aluguel renovado com sucesso.",
            "nova_data_devolucao": aluguel.data_prevista_devolucao.isoformat(),
            "novo_valor_total": float(aluguel.valor_total)
        }, 200
