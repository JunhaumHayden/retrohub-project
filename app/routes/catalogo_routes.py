import logging
from decimal import Decimal
from flask import request
from flask_restx import Namespace, Resource, fields

from app.models import Catalogo, Funcionario
from app.container.container import container
from app.models.enums import StatusCatalogo

# Criar namespace para catálogo
catalogo_ns = Namespace('catalogo', description='Operações relacionadas ao catálogo de jogos', path='/api/catalogo/itens')

# Modelos para documentação Swagger
catalogo_model = catalogo_ns.model('Catalogo', {
    'id': fields.Integer(description='ID do jogo'),
    'titulo': fields.String(description='Título do jogo'),
    'descricao': fields.String(description='Descrição do jogo'),
    'situacao': fields.String(description='Situação do jogo'),
    'genero': fields.String(description='Gênero do jogo'),
    'classificacao': fields.String(description='Classificação do jogo')
})

catalogo_input_model = catalogo_ns.model('CatalogoInput', {
    'titulo': fields.String(required=True, description='Título do jogo'),
    'descricao': fields.String(description='Descrição do jogo'),
    'genero': fields.String(description='Gênero do jogo'),
    'classificacao': fields.String(description='Classificação do jogo'),
    'situacao': fields.String(description='Situação do jogo', default=StatusCatalogo.DISPONIVEL.value)
})

# Configuração de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def serialize_catalogo(jogo: Catalogo):
    """Função utilitária para serializar um objeto Jogo."""
    return {
        "id": jogo.id,
        "titulo": jogo.titulo,
        "descricao": jogo.descricao,
        "situacao": jogo.situacao,
        "genero": jogo.genero,
        "classificacao": jogo.classificacao,
        "estoque_disponivel": jogo.estoque_disponivel if hasattr(jogo, 'estoque_disponivel') else 0
    }

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
# CREATE (C) - Inserir novo item no catálogo
# ==========================================
@catalogo_ns.route('/')
class CatalogoCreate(Resource):
    @catalogo_ns.expect(catalogo_input_model)
    def post(self):
        try:
            # Apenas Funcionários (ou Admin) podem cadastrar
            funcionario, erro = get_funcionario_from_header()
            if erro:
                return {"erro": erro}, 403

            data = request.get_json()
            if not data:
                return {"erro": "Dados não fornecidos."}, 400

            # Validação de campos obrigatórios
            required_fields = ['titulo']
            for field in required_fields:
                if field not in data or not str(data[field]).strip():
                    return {"erro": f"O campo '{field}' é obrigatório."}, 400

            # Check for existing title
            existing_jogo = container.catalogo_service.get_by_title(data['titulo'])
            if existing_jogo:
                return {"erro": f"O jogo '{data['titulo']}' já está cadastrado."}, 400

            # Create new catalog item using service
            novo_catalogo = Catalogo(
                id=None,  # Service will assign ID
                titulo=data['titulo'],
                descricao=data.get('descricao'),
                genero=data.get('genero'),
                classificacao=data.get('classificacao'),
                situacao=data.get('situacao', StatusCatalogo.DISPONIVEL.value)
            )

            try:
                created_catalogo = container.catalogo_service.create(novo_catalogo)
                logger.info(f"Funcionário ID {funcionario.id_usuario} criou novo item no catálogo: '{data['titulo']}'")
                return {
                    "mensagem": "Item criado com sucesso!",
                    "item": serialize_catalogo(created_catalogo)
                }, 201
            except ValueError as e:
                return {"erro": str(e)}, 400

        except Exception as e:
            logger.error(f"Erro em criar_catalogo: {str(e)}")
            return {"erro": "Erro interno ao criar item no catálogo."}, 500


# ==========================================
# READ ALL (R) - Listar jogos
# ==========================================
@catalogo_ns.route('/all')
class CatalogoList(Resource):
    def get(self):
        try:
            # Permite filtrar por status (ex: ?situacao=DISPONIVEL)
            situacao_param = request.args.get('situacao')
            ativo_param = request.args.get('ativo')  # Legacy support
            
            # Convert legacy 'ativo' parameter to 'situacao'
            if ativo_param is not None:
                is_ativo = ativo_param.lower() == 'true'
                situacao_param = StatusCatalogo.DISPONIVEL.value if is_ativo else StatusCatalogo.INDISPONIVEL.value
            
            catalogos = container.catalogo_service.list_all(situacao_param)
                
            return [serialize_catalogo(j) for j in catalogos], 200
        except Exception as e:
            logger.error(f"Erro em listar_catalogos: {str(e)}")
            return {"erro": "Erro ao buscar catálogo."}, 500

# ==========================================
# READ ALL DTO(R) - Listar jogos
# ==========================================
@catalogo_ns.route('/')
class CatalogoListDTO(Resource):
    def get(self):
        #to do
        pass
# ==========================================
# READ ONE (R) - Detalhes do jogo
# ==========================================
@catalogo_ns.route('/all/<int:id>')
class CatalogoDetail(Resource):
    def get(self, id):
        try:
            jogo = container.catalogo_service.get_by_id(id)
            if not jogo:
                return {"erro": "Catalogo não encontrado no catálogo."}, 404
                
            return serialize_catalogo(jogo), 200
        except Exception as e:
            logger.error(f"Erro em buscar_catalogo: {str(e)}")
            return {"erro": "Erro ao buscar jogo."}, 500

# ==========================================
# READ ONE DTO(R) - lista de jogos resumo
# ==========================================
@catalogo_ns.route('/<int:id>')
class CatalogoDetailDTO(Resource):
    def get(self, id):
        #to do
        pass

# ==========================================
# UPDATE (U) - Atualizar dados do jogo
# ==========================================
@catalogo_ns.route('/<int:id>')
class CatalogoUpdate(Resource):
    @catalogo_ns.expect(catalogo_input_model)
    def put(self, id):
        try:
            # Apenas Funcionários podem alterar
            funcionario, erro = get_funcionario_from_header()
            if erro:
                return {"erro": erro}, 403

            data = request.get_json()
            if not data:
                return {"erro": "Dados não fornecidos."}, 400

            jogo = container.catalogo_service.get_by_id(id)
            if not jogo:
                return {"erro": "Catalogo não encontrado."}, 404

            # Prevenção contra duplicidade ao alterar título ou plataforma
            novo_titulo = data.get('titulo', jogo.titulo)
            nova_plataforma = data.get('plataforma', jogo.plataforma)

            if novo_titulo != jogo.titulo or nova_plataforma != jogo.plataforma:
                catalogos = container.catalogo_service.list_all()
                jogo_duplicado = None
                for j in catalogos:
                    if (j.titulo.lower() == novo_titulo.lower() and 
                        j.plataforma.lower() == nova_plataforma.lower() and 
                        j.id != id):
                        jogo_duplicado = j
                        break
                if jogo_duplicado:
                    return {"erro": f"Já existe outro jogo cadastrado como '{novo_titulo}' na plataforma '{nova_plataforma}'."}, 400

            # Note: In mock mode, we can't actually save changes
            # Atualização dos campos
            if 'titulo' in data: jogo.titulo = data['titulo']
            if 'descricao' in data: jogo.descricao = data['descricao']
            if 'plataforma' in data: jogo.plataforma = data['plataforma']
            if 'ativo' in data: jogo.ativo = data['ativo']
            if 'genero' in data: jogo.genero = data['genero']
            if 'classificacao' in data: jogo.classificacao = data['classificacao']
            
            if 'valor_venda' in data:
                jogo.valor_venda = Decimal(str(data['valor_venda'])) if data['valor_venda'] is not None else None
                
            if 'valor_diaria_aluguel' in data:
                jogo.valor_diaria_aluguel = Decimal(str(data['valor_diaria_aluguel'])) if data['valor_diaria_aluguel'] is not None else None

            # In a real implementation, you would save this:
            # MockDataSource.save(jogo)

            logger.info(f"Funcionário ID {funcionario.id_usuario} atualizou o jogo ID {id}")
            return {
                "mensagem": "Item atualizado com sucesso!",
                "item": serialize_catalogo(jogo)
            }, 200

        except Exception as e:
            logger.error(f"Erro em atualizar_catalogo: {str(e)}")
            return {"erro": "Erro interno ao atualizar item."}, 500

# ==========================================
# DELETE (D) - Inativar ou Excluir item
# ==========================================
@catalogo_ns.route('/<int:id>')
class CatalogoDelete(Resource):
    def delete(self, id):
        try:
            # Apenas Funcionários podem excluir
            funcionario, erro = get_funcionario_from_header()
            if erro:
                return {"erro": erro}, 403

            jogo = container.catalogo_service.get_by_id(id)
            if not jogo:
                return {"erro": "Catalogo não encontrado."}, 404

            try:
                # Soft delete: inativar em vez de excluir
                inactivated_jogo = container.catalogo_service.inactivate(id)
                if not inactivated_jogo:
                    return {"erro": "Catalogo não encontrado."}, 404

                logger.info(f"Funcionário ID {funcionario.id_usuario} inativou o jogo ID {id}")
                return {
                    "mensagem": "Item inativado com sucesso.",
                    "item": serialize_catalogo(inactivated_jogo)
                }, 200
            except ValueError as e:
                return {"erro": str(e)}, 400

        except Exception as e:
            logger.error(f"Erro em excluir_catalogo: {str(e)}")
            return {"erro": "Erro interno ao excluir item."}, 500
