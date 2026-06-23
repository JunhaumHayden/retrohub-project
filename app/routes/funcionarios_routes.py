import logging
from datetime import datetime
from flask import request
from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash

from app.models import Funcionario
from app.container.container import container

# Criar namespace para funcionários
funcionarios_ns = Namespace('funcionarios', description='Operações relacionadas aos funcionários', path='/api/funcionarios')

# Modelos para documentação Swagger
funcionario_model = funcionarios_ns.model('Funcionario', {
    'id': fields.Integer(description='ID do funcionário'),
    'nome': fields.String(description='Nome do funcionário'),
    'cpf': fields.String(description='CPF do funcionário'),
    'email': fields.String(description='Email do funcionário'),
    'matricula': fields.String(description='Matrícula do funcionário'),
    'cargo': fields.String(description='Cargo do funcionário'),
    'setor': fields.String(description='Setor do funcionário'),
    'data_admissao': fields.Date(description='Data de admissão'),
    'data_cadastro': fields.Date(description='Data de cadastro'),
    'data_nascimento': fields.Date(description='Data de nascimento')
})

funcionario_input_model = funcionarios_ns.model('FuncionarioInput', {
    'nome': fields.String(required=True, description='Nome do funcionário'),
    'cpf': fields.String(required=True, description='CPF do funcionário'),
    'email': fields.String(required=True, description='Email do funcionário'),
    'senha': fields.String(required=True, description='Senha do funcionário'),
    'matricula': fields.String(required=True, description='Matrícula do funcionário'),
    'cargo': fields.String(description='Cargo do funcionário'),
    'setor': fields.String(description='Setor do funcionário'),
    'data_nascimento': fields.String(required=True, description='Data de nascimento (YYYY-MM-DD)'),
    'data_admissao': fields.String(description='Data de admissão (YYYY-MM-DD)')
})

# Configuração simples de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def serialize_funcionario(func: Funcionario):
    """Função utilitária para serializar um objeto Funcionario de forma segura."""
    if not isinstance(func, Funcionario):
        # Retorna um dicionário vazio ou lança um erro se o objeto não for do tipo esperado
        return {}
        
    return {
        "id": getattr(func, 'id', None),
        "nome": getattr(func, 'nome', None),
        "cpf": getattr(func, 'cpf', None),
        "email": getattr(func, 'email', None),
        "matricula": getattr(func, 'matricula', None),
        "cargo": getattr(func, 'cargo', None),
        "setor": getattr(func, 'setor', None),
        "data_admissao": func.data_admissao.isoformat() if hasattr(func, 'data_admissao') and func.data_admissao else None,
        "data_cadastro": func.data_cadastro.isoformat() if hasattr(func, 'data_cadastro') and func.data_cadastro else None,
        "data_nascimento": func.data_nascimento.isoformat() if hasattr(func, 'data_nascimento') and func.data_nascimento else None
    }

def get_admin_from_header():
    """Verifica se o header X-Admin-Id foi passado e se ele é um administrador válido."""
    admin_id = request.headers.get('X-Admin-Id')
    if not admin_id:
        funcionarios_ns.abort(403, "Header X-Admin-Id é obrigatório para esta operação.")
    
    try:
        admin = container.usuario_service.get_funcionario_by_id(int(admin_id))
        if not admin or not admin.cargo or admin.cargo.lower() != 'administrador':
            funcionarios_ns.abort(403, "Usuário não é um administrador válido.")
        return admin
    except ValueError:
        funcionarios_ns.abort(400, "X-Admin-Id deve ser um número inteiro.")
    except Exception:
        funcionarios_ns.abort(500, "Erro ao validar administrador.")


@funcionarios_ns.route('/')
class FuncionarioCollectionResource(Resource):
    @funcionarios_ns.doc(params={'X-Admin-Id': {'in': 'header', 'description': 'ID do administrador', 'required': True}})
    @funcionarios_ns.expect(funcionario_input_model)
    @funcionarios_ns.marshal_with(funcionario_model, code=201)
    def post(self):
        """Cria um novo funcionário."""
        admin = get_admin_from_header()
        data = request.get_json()
        
        try:
            data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
            data_admissao = datetime.strptime(data.get('data_admissao', datetime.today().strftime('%Y-%m-%d')), '%Y-%m-%d').date()

            novo_func = Funcionario(
                nome=data['nome'],
                cpf=data['cpf'],
                email=data['email'],
                senha=generate_password_hash(data['senha']),
                data_nascimento=data_nascimento,
                matricula=data['matricula'],
                cargo=data['cargo'],
                setor=data.get('setor'),
                data_admissao=data_admissao
            )
            
            funcionario_criado = container.usuario_service.create_funcionario(novo_func)
            logger.info(f"Admin ID {admin.id} CRIOU o funcionário ID {funcionario_criado.id}.")
            return funcionario_criado, 201
        except (ValueError, KeyError) as e:
            funcionarios_ns.abort(400, f"Erro nos dados fornecidos: {e}")
        except Exception as e:
            logger.error(f"Erro interno ao criar funcionário: {e}")
            funcionarios_ns.abort(500, "Erro interno ao criar funcionário.")

    @funcionarios_ns.marshal_list_with(funcionario_model)
    def get(self):
        """Lista todos os funcionários."""
        funcionarios = container.usuario_service.list_funcionarios()
        return funcionarios


@funcionarios_ns.route('/<int:id>')
@funcionarios_ns.response(404, 'Funcionário não encontrado.')
class FuncionarioItemResource(Resource):
    @funcionarios_ns.marshal_with(funcionario_model)
    def get(self, id):
        """Busca um funcionário por ID."""
        func = container.usuario_service.get_funcionario_by_id(id)
        if not func:
            funcionarios_ns.abort(404, "Funcionário não encontrado.")
        return func

    @funcionarios_ns.doc(params={'X-Admin-Id': {'in': 'header', 'description': 'ID do administrador', 'required': True}})
    @funcionarios_ns.expect(funcionario_input_model)
    @funcionarios_ns.marshal_with(funcionario_model)
    def put(self, id):
        """Atualiza os dados de um funcionário."""
        admin = get_admin_from_header()
        data = request.get_json()
        
        try:
            funcionario_atualizado = container.usuario_service.update_funcionario(id, data)
            if not funcionario_atualizado:
                funcionarios_ns.abort(404, "Funcionário não encontrado.")
            
            logger.info(f"Admin ID {admin.id} ATUALIZOU o funcionário ID {funcionario_atualizado.id}.")
            return funcionario_atualizado
        except ValueError as e:
            funcionarios_ns.abort(400, str(e))
        except Exception as e:
            logger.error(f"Erro interno ao atualizar funcionário: {e}")
            funcionarios_ns.abort(500, "Erro interno ao atualizar funcionário.")

    @funcionarios_ns.doc(params={'X-Admin-Id': {'in': 'header', 'description': 'ID do administrador', 'required': True}})
    @funcionarios_ns.response(200, 'Funcionário excluído com sucesso.')
    def delete(self, id):
        """Exclui um funcionário."""
        admin = get_admin_from_header()
        
        try:
            sucesso = container.usuario_service.delete_funcionario(id, admin_id=admin.id)
            if not sucesso:
                funcionarios_ns.abort(404, "Funcionário não encontrado.")
            
            logger.warning(f"Admin ID {admin.id} EXCLUIU o funcionário ID {id}.")
            return {"mensagem": "Funcionário excluído com sucesso."}, 200
        except ValueError as e:
            funcionarios_ns.abort(400, str(e))
        except Exception as e:
            logger.error(f"Erro ao excluir funcionário: {e}")
            funcionarios_ns.abort(500, "Erro interno ao excluir funcionário.")
