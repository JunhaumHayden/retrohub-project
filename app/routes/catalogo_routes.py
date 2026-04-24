import logging
from decimal import Decimal
from flask import request
from flask_restx import Namespace, Resource, fields

from app.models import Catalogo, Funcionario
from app.database.data_factory import data_factory

# Criar namespace para catálogo
catalogo_ns = Namespace('catalogo', description='Operações relacionadas ao catálogo de jogos', path='/api/catalogo/itens')

# Modelos para documentação Swagger
catalogo_model = catalogo_ns.model('Catalogo', {
    'id': fields.Integer(description='ID do jogo'),
    'titulo': fields.String(description='Título do jogo'),
    'descricao': fields.String(description='Descrição do jogo'),
    'plataforma': fields.String(description='Plataforma do jogo'),
    'ativo': fields.Boolean(description='Status ativo do jogo'),
    'genero': fields.String(description='Gênero do jogo'),
    'classificacao': fields.String(description='Classificação do jogo'),
    'valor_venda': fields.Float(description='Valor de venda'),
    'valor_diaria_aluguel': fields.Float(description='Valor diário do aluguel')
})

catalogo_input_model = catalogo_ns.model('CatalogoInput', {
    'titulo': fields.String(required=True, description='Título do jogo'),
    'descricao': fields.String(description='Descrição do jogo'),
    'plataforma': fields.String(required=True, description='Plataforma do jogo'),
    'genero': fields.String(description='Gênero do jogo'),
    'classificacao': fields.String(description='Classificação do jogo'),
    'valor_venda': fields.Float(description='Valor de venda'),
    'valor_diaria_aluguel': fields.Float(description='Valor diário do aluguel'),
    'ativo': fields.Boolean(description='Status ativo do jogo', default=True)
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
        "plataforma": jogo.plataforma,
        "ativo": jogo.ativo,
        "genero": jogo.genero,
        "classificacao": jogo.classificacao,
        "valor_venda": float(jogo.valor_venda) if jogo.valor_venda else None,
        "valor_diaria_aluguel": float(jogo.valor_diaria_aluguel) if jogo.valor_diaria_aluguel else None
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

    funcionario = data_factory.get_by_id(Funcionario, func_id)
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
            required_fields = ['titulo', 'plataforma']
            for field in required_fields:
                if field not in data or not str(data[field]).strip():
                    return {"erro": f"O campo '{field}' é obrigatório."}, 400

            # Prevenção contra duplicidade (título + plataforma)
            catalogos = data_factory.get_all(Catalogo)
            jogo_duplicado = None
            for jogo in catalogos:
                if (jogo.titulo.lower() == data['titulo'].lower() and 
                    jogo.plataforma.lower() == data['plataforma'].lower()):
                    jogo_duplicado = jogo
                    break
            
            if jogo_duplicado:
                return {"erro": f"O jogo '{data['titulo']}' já está cadastrado para a plataforma '{data['plataforma']}'."}, 400

            valor_venda = Decimal(str(data['valor_venda'])) if data.get('valor_venda') else None
            valor_diaria_aluguel = Decimal(str(data['valor_diaria_aluguel'])) if data.get('valor_diaria_aluguel') else None

            # Note: In mock mode, we can't actually save new catalog items
            novo_catalogo = Catalogo(
                id=1,  # Placeholder ID
                titulo=data['titulo'],
                descricao=data.get('descricao'),
                plataforma=data['plataforma'],
                ativo=data.get('ativo', True),
                genero=data.get('genero'),
                classificacao=data.get('classificacao'),
                valor_venda=valor_venda,
                valor_diaria_aluguel=valor_diaria_aluguel
            )

            # In a real implementation, you would save this:
            # data_factory.save(novo_catalogo)

            logger.info(f"Funcionário ID {funcionario.id_usuario} criou novo item no catálogo: '{data['titulo']}'")
            return {
                "mensagem": "Item criado com sucesso!",
                "item": serialize_catalogo(novo_catalogo)
            }, 201

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
            # Permite filtrar por status ativo (ex: ?ativo=true)
            ativo_param = request.args.get('ativo')
            catalogos = data_factory.get_all(Catalogo)
            
            if ativo_param is not None:
                is_ativo = ativo_param.lower() == 'true'
                catalogos = [c for c in catalogos if c.ativo == is_ativo]
                
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
            jogo = data_factory.get_by_id(Catalogo, id)
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

            jogo = data_factory.get_by_id(Catalogo, id)
            if not jogo:
                return {"erro": "Catalogo não encontrado."}, 404

            # Prevenção contra duplicidade ao alterar título ou plataforma
            novo_titulo = data.get('titulo', jogo.titulo)
            nova_plataforma = data.get('plataforma', jogo.plataforma)

            if novo_titulo != jogo.titulo or nova_plataforma != jogo.plataforma:
                catalogos = data_factory.get_all(Catalogo)
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
            # data_factory.save(jogo)

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

            jogo = data_factory.get_by_id(Catalogo, id)
            if not jogo:
                return {"erro": "Catalogo não encontrado."}, 404

            # Note: In mock mode, we can't actually save changes
            # Soft delete: inativar em vez de excluir
            jogo.ativo = False
            
            # In a real implementation, you would save this:
            # data_factory.save(jogo)

            logger.info(f"Funcionário ID {funcionario.id_usuario} inativou o jogo ID {id}")
            return {
                "mensagem": "Item inativado com sucesso.",
                "item": serialize_catalogo(jogo)
            }, 200

        except Exception as e:
            logger.error(f"Erro em excluir_catalogo: {str(e)}")
            return {"erro": "Erro interno ao excluir item."}, 500
