import logging
from flask import request
from flask_restx import Namespace, Resource, fields

from app.models import Catalogo
from app.container.container import container
from app.models.enums import StatusSituacao

# Criar namespace para catálogo
catalogo_ns = Namespace('catalogo', description='Operações relacionadas ao catálogo de jogos', path='/api/catalogo/itens')

# Modelos para documentação Swagger
catalogo_model = catalogo_ns.model('Catalogo', {
    'id': fields.Integer(description='ID do jogo'),
    'titulo': fields.String(description='Título do jogo'),
    'descricao': fields.String(description='Descrição do jogo'),
    'situacao': fields.String(description='Situação do jogo'),
    'genero': fields.String(description='Gênero do jogo'),
    'classificacao': fields.String(description='Classificação do jogo'),
    'estoque_disponivel': fields.Integer(description='Quantidade de exemplares disponíveis')
})

catalogo_input_model = catalogo_ns.model('CatalogoInput', {
    'titulo': fields.String(required=True, description='Título do jogo'),
    'descricao': fields.String(description='Descrição do jogo'),
    'genero': fields.String(description='Gênero do jogo'),
    'classificacao': fields.String(description='Classificação do jogo'),
    'situacao': fields.String(description='Situação do jogo', default=StatusSituacao.DISPONIVEL.value)
})

# Configuração de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _enum_to_str(value):
    if value is None:
        return None
    return getattr(value, "value", getattr(value, "name", value))

def serialize_catalogo(jogo: Catalogo):
    """Função utilitária para serializar um objeto Catalogo."""
    return {
        "id": jogo.id,
        "titulo": jogo.titulo,
        "descricao": jogo.descricao,
        "situacao": _enum_to_str(jogo.situacao),
        "genero": jogo.genero,
        "classificacao": jogo.classificacao,
        "estoque_disponivel": container.catalogo_service.get_estoque_disponivel(jogo.id)
    }

def get_funcionario_from_header():
    """Verifica se o header X-Funcionario-Id foi passado e se é um funcionário válido."""
    func_id = request.headers.get('X-Funcionario-Id') or request.headers.get('X-Admin-Id')
    if not func_id:
        catalogo_ns.abort(403, "Header X-Funcionario-Id (ou X-Admin-Id) é obrigatório para esta operação.")
    
    try:
        funcionario = container.usuario_service.get_funcionario_by_id(int(func_id))
        if not funcionario:
            catalogo_ns.abort(403, "Funcionário não encontrado.")
        return funcionario
    except ValueError:
        catalogo_ns.abort(400, "ID de funcionário inválido.")


@catalogo_ns.route('/')
class CatalogoCollectionResource(Resource):
    @catalogo_ns.marshal_list_with(catalogo_model)
    def get(self):
        """Lista todos os jogos do catálogo, com filtros opcionais."""
        try:
            situacao_param = request.args.get('situacao')
            catalogos = container.catalogo_service.list_all(situacao=situacao_param)
            return [serialize_catalogo(j) for j in catalogos], 200
        except Exception as e:
            logger.error(f"Erro em listar_catalogos: {str(e)}")
            catalogo_ns.abort(500, "Erro ao buscar catálogo.")

    @catalogo_ns.doc(params={'X-Funcionario-Id': {'in': 'header', 'description': 'ID do funcionário (ou X-Admin-Id)', 'required': True}})
    @catalogo_ns.expect(catalogo_input_model)
    def post(self):
        """Cria um novo item no catálogo."""
        funcionario = get_funcionario_from_header()
        data = request.get_json()
        if not data or not data.get('titulo'):
            catalogo_ns.abort(400, "O campo 'titulo' é obrigatório.")

        try:
            novo_catalogo = Catalogo(
                titulo=data['titulo'],
                descricao=data.get('descricao'),
                genero=data.get('genero'),
                classificacao=data.get('classificacao'),
                situacao=data.get('situacao', StatusSituacao.DISPONIVEL.value)
            )
            created_catalogo = container.catalogo_service.create(novo_catalogo)
            logger.info(f"Funcionário ID {funcionario.id} criou o item de catálogo '{created_catalogo.titulo}'.")
            return serialize_catalogo(created_catalogo), 201
        except ValueError as e:
            catalogo_ns.abort(400, str(e))
        except Exception as e:
            logger.error(f"Erro em criar_catalogo: {str(e)}")
            catalogo_ns.abort(500, "Erro interno ao criar item no catálogo.")


@catalogo_ns.route('/<int:id>')
@catalogo_ns.response(404, 'Jogo não encontrado no catálogo.')
class CatalogoItemResource(Resource):
    @catalogo_ns.marshal_with(catalogo_model)
    def get(self, id):
        """Busca um item do catálogo por ID."""
        jogo = container.catalogo_service.get_by_id(id)
        if not jogo:
            catalogo_ns.abort(404, "Jogo não encontrado no catálogo.")
        return serialize_catalogo(jogo)

    @catalogo_ns.doc(params={'X-Funcionario-Id': {'in': 'header', 'description': 'ID do funcionário (ou X-Admin-Id)', 'required': True}})
    @catalogo_ns.expect(catalogo_input_model)
    def put(self, id):
        """Atualiza um item do catálogo."""
        funcionario = get_funcionario_from_header()
        data = request.get_json()
        if not data:
            catalogo_ns.abort(400, "Dados não fornecidos.")

        try:
            updated_catalogo = container.catalogo_service.update(id, data)
            if not updated_catalogo:
                catalogo_ns.abort(404, "Jogo não encontrado.")
            logger.info(f"Funcionário ID {funcionario.id} atualizou o item de catálogo ID {id}.")
            return serialize_catalogo(updated_catalogo)
        except ValueError as e:
            catalogo_ns.abort(400, str(e))
        except Exception as e:
            logger.error(f"Erro em atualizar_catalogo: {str(e)}")
            catalogo_ns.abort(500, "Erro interno ao atualizar item.")

    @catalogo_ns.doc(params={'X-Funcionario-Id': {'in': 'header', 'description': 'ID do funcionário (ou X-Admin-Id)', 'required': True}})
    def delete(self, id):
        """Inativa um item do catálogo (soft delete)."""
        funcionario = get_funcionario_from_header()
        try:
            inactivated_jogo = container.catalogo_service.inactivate(id)
            if not inactivated_jogo:
                catalogo_ns.abort(404, "Jogo não encontrado.")
            logger.info(f"Funcionário ID {funcionario.id} inativou o jogo ID {id}.")
            return {"mensagem": "Item inativado com sucesso."}, 200
        except Exception as e:
            logger.error(f"Erro em excluir_catalogo: {str(e)}")
            catalogo_ns.abort(500, "Erro interno ao inativar item.")
