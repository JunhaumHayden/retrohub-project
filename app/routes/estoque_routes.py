import logging
from datetime import datetime
from flask import request
from flask_restx import Namespace, Resource, fields
from sqlalchemy.exc import IntegrityError

from app.models import Funcionario
from app.container.container import container

# Criar namespace para estoque
estoque_ns = Namespace('estoque', description='Operações relacionadas ao estoque de jogos', path='/api/estoque')

# Modelos para documentação Swagger
midia_fisica_model = estoque_ns.model('MidiaFisica', {
    'id': fields.Integer(description='ID do exemplar'),
    'id_catalogo': fields.Integer(description='ID do catálogo'),
    'tipo_midia': fields.String(description='Tipo de mídia'),
    'codigo_barras': fields.String(description='Código de barras'),
    'estado_conservacao': fields.String(description='Estado de conservação')
})

midia_digital_model = estoque_ns.model('MidiaDigital', {
    'id': fields.Integer(description='ID do exemplar'),
    'id_catalogo': fields.Integer(description='ID do catálogo'),
    'tipo_midia': fields.String(description='Tipo de mídia'),
    'chave_ativacao': fields.String(description='Chave de ativação')
})

midia_fisica_input_model = estoque_ns.model('MidiaFisicaInput', {
    'id_catalogo': fields.Integer(required=True, description='ID do catálogo'),
    'codigo_barras': fields.String(required=True, description='Código de barras'),
    'estado_conservacao': fields.String(description='Estado de conservação')
})

midia_digital_input_model = estoque_ns.model('MidiaDigitalInput', {
    'id_catalogo': fields.Integer(required=True, description='ID do catálogo'),
    'chave_ativacao': fields.String(required=True, description='Chave de ativação')
})

# Configuração de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_funcionario_from_header():
    """Verifica se o header X-Funcionario-Id foi passado e se é um funcionário válido."""
    func_id = request.headers.get('X-Funcionario-Id')
    
    # Faz fallback para X-Admin-Id caso alguém envie como admin
    if not func_id:
        func_id = request.headers.get('X-Admin-Id')
        
    if not func_id:
        return None, "Header X-Funcionario-Id (ou X-Admin-Id) é obrigatório para esta operação."
    
    try:
        func_id = int(func_id)
    except ValueError:
        return None, "O ID do funcionário deve ser um número inteiro."

    funcionario = container.usuario_service.get_funcionario_by_id(func_id)
    if not funcionario:
        return None, "Funcionário não encontrado."
        
    return funcionario, None




# ==========================================
# CREATE (C) - Cadastro de Mídia Física
# ==========================================
@estoque_ns.route('/fisico')
class MidiaFisicaResource(Resource):
    @estoque_ns.expect(midia_fisica_input_model)
    def post(self):
        try:
            funcionario, erro = get_funcionario_from_header()
            if erro: return {"erro": erro}, 403

            data = request.get_json()
            if not data: return {"erro": "Dados não fornecidos."}, 400

            required_fields = ['id_catalogo', 'codigo_barras', 'estado_conservacao']
            for field in required_fields:
                if field not in data or not str(data[field]).strip():
                    return {"erro": f"O campo '{field}' é obrigatório."}, 400

            midia, erro = container.estoque_service.create_midia_fisica(
                id_catalogo=data['id_catalogo'],
                codigo_barras=data['codigo_barras'],
                estado_conservacao=data['estado_conservacao']
            )
            
            if erro:
                return {"erro": erro}, 400

            logger.info(f"Funcionário ID {funcionario.id} cadastrou mídia FÍSICA '{midia.codigo_barras}'.")
            return container.estoque_service.serialize_exemplar(midia), 201

        except Exception as e:
            return {"erro": f"Erro interno: {str(e)}"}, 500


# ==========================================
# CREATE (C) - Cadastro de Mídia Digital
# ==========================================
@estoque_ns.route('/digital')
class MidiaDigitalResource(Resource):
    @estoque_ns.expect(midia_digital_input_model)
    def post(self):
        try:
            funcionario, erro = get_funcionario_from_header()
            if erro: return {"erro": erro}, 403

            data = request.get_json()
            if not data: return {"erro": "Dados não fornecidos."}, 400

            required_fields = ['id_catalogo', 'chave_ativacao']
            for field in required_fields:
                if field not in data or not str(data[field]).strip():
                    return {"erro": f"O campo '{field}' é obrigatório."}, 400

            data_expiracao = None
            if 'data_expiracao' in data and data['data_expiracao']:
                try:
                    data_expiracao = datetime.strptime(data['data_expiracao'], '%Y-%m-%d').date()
                except ValueError:
                    return {"erro": "Formato de data inválido. Use AAAA-MM-DD."}, 400

            midia, erro = container.estoque_service.create_midia_digital(
                id_catalogo=data['id_catalogo'],
                chave_ativacao=data['chave_ativacao'],
                data_expiracao=data_expiracao
            )
            
            if erro:
                return {"erro": erro}, 400

            logger.info(f"Funcionário ID {funcionario.id} cadastrou mídia DIGITAL para o catalogo ID {data['id_catalogo']}.")
            return container.estoque_service.serialize_exemplar(midia), 201

        except Exception as e:
            return {"erro": f"Erro interno: {str(e)}"}, 500


# ==========================================
# READ ALL (R) - Lista o estoque de um Jogo
# ==========================================
@estoque_ns.route('/catalogo/<int:id_catalogo>')
class EstoqueCatalogoResource(Resource):
    def get(self, id_catalogo):
        try:
            exemplares = container.estoque_service.get_exemplares_by_catalogo(id_catalogo)
            if not exemplares:
                return {"erro": "Jogo não encontrado no catálogo ou sem exemplares."}, 404
            
            return [container.estoque_service.serialize_exemplar(ex) for ex in exemplares], 200
        except Exception as e:
            return {"erro": f"Erro ao buscar estoque: {str(e)}"}, 500


# ==========================================
# UPDATE (U) - Atualizar estado de conservação
# ==========================================
@estoque_ns.route('/fisico/<int:id>')
class MidiaFisicaEstadoResource(Resource):
    @estoque_ns.expect(midia_fisica_model)
    @estoque_ns.marshal_with(midia_fisica_model, code=200)
    def put(self, id):
        try:
            funcionario, erro = get_funcionario_from_header()
            if erro: return {"erro": erro}, 403

            data = request.get_json()
            if not data or 'estado_conservacao' not in data:
                return {"erro": "O campo 'estado_conservacao' é obrigatório."}, 400

            midia, erro = container.estoque_service.update_estado_conservacao(id, data['estado_conservacao'])
            if erro:
                return {"erro": erro}, 400

            logger.info(f"Funcionário ID {funcionario.id} ATUALIZOU o estado da mídia {midia.codigo_barras}.")
            return container.estoque_service.serialize_exemplar(midia), 200

        except Exception as e:
            return {"erro": f"Erro interno: {str(e)}"}, 500


# ==========================================
# DELETE (D) - Exclusão de Exemplar
# ==========================================
@estoque_ns.route('/<int:id>')
class ExemplarResource(Resource):
    def delete(self, id):
        try:
            funcionario, erro = get_funcionario_from_header()
            if erro: return {"erro": erro}, 403

            exemplar = container.estoque_service.get_exemplar_by_id(id)
            if not exemplar:
                return {"erro": "Exemplar não encontrado."}, 404

            tipo = exemplar.tipo_midia
            success, erro = container.estoque_service.delete_exemplar(id)
            if erro:
                return {"erro": erro}, 400
            
            logger.warning(f"Funcionário ID {funcionario.id} EXCLUIU o exemplar ID {id} ({tipo}).")
            return {"mensagem": "Exemplar excluído do estoque com sucesso."}, 200
            
        except Exception as e:
            return {"erro": f"Erro ao excluir exemplar: {str(e)}"}, 500
