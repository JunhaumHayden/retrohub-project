import re
import logging
from datetime import datetime
from flask import request
from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

from app.models import Funcionario, Usuario
from app.database.factories.database_manager import DatabaseManager

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

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def calculate_age(birthdate):
    today = datetime.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

def serialize_funcionario(func: Funcionario):
    """Função utilitária para serializar um objeto Funcionario."""
    return {
        "id": func.id,
        "nome": func.nome,
        "cpf": func.cpf,
        "email": func.email,
        "matricula": func.matricula,
        "cargo": func.cargo,
        "setor": func.setor,
        "data_admissao": func.data_admissao.isoformat() if func.data_admissao else None,
        "data_cadastro": func.data_cadastro.isoformat() if func.data_cadastro else None,
        "data_nascimento": func.data_nascimento.isoformat() if func.data_nascimento else None
    }

def get_admin_from_header(session):
    """Verifica se o header X-Admin-Id foi passado e se ele é um administrador válido."""
    admin_id = request.headers.get('X-Admin-Id')
    if not admin_id:
        return None, "Header X-Admin-Id é obrigatório para esta operação."
    
    try:
        admin_id = int(admin_id)
    except ValueError:
        return None, "X-Admin-Id deve ser um número inteiro."

    admin = session.query(Funcionario).get(admin_id)
    if not admin:
        return None, "Administrador não encontrado."
    
    # Valida se o cargo é Administrador (ignorando case)
    if not admin.cargo or admin.cargo.lower() != 'administrador':
        return None, "Usuário não tem permissão de Administrador."
        
    return admin, None

# ==========================================
# CREATE (C) - Cria novo funcionário
# ==========================================
@funcionarios_ns.route('/')
class FuncionarioCadastro(Resource):
    @funcionarios_ns.expect(funcionario_input_model)
    @funcionarios_ns.marshal_with(funcionario_model, code=201)
    def post(self):
        session = DatabaseManager.get_session()
        try:
            # Apenas Admin
            admin, erro = get_admin_from_header(session)
            if erro:
                return {"erro": erro}, 403

            data = request.get_json()
            if not data:
                return {"erro": "Dados não fornecidos."}, 400

            required_fields = ['nome', 'cpf', 'email', 'senha', 'data_nascimento', 'matricula', 'cargo']
            for field in required_fields:
                if field not in data or not data[field]:
                    return {"erro": f"O campo '{field}' é obrigatório."}, 400

            if not is_valid_email(data['email']):
                return {"erro": "Formato de e-mail inválido."}, 400

            try:
                data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
            except ValueError:
                return {"erro": "Formato de data de nascimento inválido. Use AAAA-MM-DD."}, 400

            if calculate_age(data_nascimento) < 18:
                return {"erro": "O funcionário deve ter pelo menos 18 anos."}, 400

            # Verifica duplicidade
            email_exists = session.query(Usuario).filter_by(email=data['email']).first()
            if email_exists:
                return {"erro": "E-mail já cadastrado no sistema."}, 400
                
            cpf_exists = session.query(Usuario).filter_by(cpf=data['cpf']).first()
            if cpf_exists:
                return {"erro": "CPF já cadastrado no sistema."}, 400

            matricula_exists = session.query(Funcionario).filter_by(matricula=data['matricula']).first()
            if matricula_exists:
                return {"erro": "Matrícula já cadastrada."}, 400

            # Hash da senha
            senha_hash = generate_password_hash(data['senha'])

            data_admissao = datetime.strptime(data.get('data_admissao', datetime.today().strftime('%Y-%m-%d')), '%Y-%m-%d').date()

            novo_func = Funcionario(
                nome=data['nome'],
                cpf=data['cpf'],
                email=data['email'],
                senha=senha_hash,
                data_nascimento=data_nascimento,
                matricula=data['matricula'],
                cargo=data['cargo'],
                setor=data.get('setor'),
                data_admissao=data_admissao
            )

            session.add(novo_func)
            session.commit()

            logger.info(f"Admin ID {admin.id} ({admin.nome}) CRIOU o funcionário ID {novo_func.id} ({novo_func.nome}).")

            return serialize_funcionario(novo_func), 201

        except IntegrityError as e:
            session.rollback()
            return {"erro": "Conflito de dados de integridade no banco."}, 400
        except Exception as e:
            session.rollback()
            return {"erro": f"Erro interno do servidor: {str(e)}"}, 500
        finally:
            session.close()

# ==========================================
# READ ALL (R)
# ==========================================
@funcionarios_ns.route('/')
class FuncionarioList(Resource):
    @funcionarios_ns.marshal_with(funcionario_model)
    def get(self):
        session = DatabaseManager.get_session()
        try:
            funcionarios = session.query(Funcionario).all()
            return [serialize_funcionario(f) for f in funcionarios], 200
        except Exception as e:
            return {"erro": f"Erro ao buscar funcionários: {str(e)}"}, 500
        finally:
            session.close()

# ==========================================
# READ ONE (R)
# ==========================================
@funcionarios_ns.route('/<int:id>')
@funcionarios_ns.response(404, 'Funcionário não encontrado.')
class FuncionarioResource(Resource):
    @funcionarios_ns.marshal_with(funcionario_model)
    def get(self, id):
        session = DatabaseManager.get_session()
        try:
            func = session.query(Funcionario).get(id)
            if not func:
                return {"erro": "Funcionário não encontrado."}, 404
            
            return serialize_funcionario(func), 200
        except Exception as e:
            return {"erro": f"Erro ao buscar funcionário: {str(e)}"}, 500
        finally:
            session.close()

# ==========================================
# UPDATE (U)
# ==========================================
@funcionarios_ns.route('/<int:id>')
@funcionarios_ns.expect(funcionario_input_model)
@funcionarios_ns.response(404, 'Funcionário não encontrado.')
class FuncionarioUpdate(Resource):
    def put(self, id):
        session = DatabaseManager.get_session()
        try:
            # Apenas Admin pode atualizar cargos ou outros dados sensíveis de funcionários (regra geral)
            admin, erro = get_admin_from_header(session)
            if erro:
                return {"erro": erro}, 403

            data = request.get_json()
            if not data:
                return {"erro": "Dados não fornecidos."}, 400

            func = session.query(Funcionario).get(id)
            if not func:
                return {"erro": "Funcionário não encontrado."}, 404

            # Impede rebaixamento de último administrador
            if func.cargo and func.cargo.lower() == 'administrador' and 'cargo' in data and data['cargo'].lower() != 'administrador':
                total_admins = session.query(Funcionario).filter(Funcionario.cargo.ilike('administrador')).count()
                if total_admins <= 1:
                    return {"erro": "Não é possível rebaixar o último administrador do sistema."}, 400

            # Atualização de email
            if 'email' in data and data['email'] != func.email:
                if not is_valid_email(data['email']):
                    return {"erro": "Formato de e-mail inválido."}, 400
                email_exists = session.query(Usuario).filter_by(email=data['email']).first()
                if email_exists:
                    return {"erro": "E-mail já cadastrado por outro usuário."}, 400
                func.email = data['email']

            if 'nome' in data: func.nome = data['nome']
            if 'setor' in data: func.setor = data['setor']
            if 'cargo' in data: func.cargo = data['cargo']

            if 'senha' in data and data['senha']:
                func.senha = generate_password_hash(data['senha'])
                
            if 'data_nascimento' in data:
                try:
                    data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
                    if calculate_age(data_nascimento) < 18:
                        return {"erro": "A nova idade seria menor que 18 anos."}, 400
                    func.data_nascimento = data_nascimento
                except ValueError:
                    return {"erro": "Formato de data de nascimento inválido."}, 400

            session.commit()
            logger.info(f"Admin ID {admin.id} ({admin.nome}) ATUALIZOU o funcionário ID {func.id} ({func.nome}).")
            
            return serialize_funcionario(func), 200

        except IntegrityError as e:
            session.rollback()
            return {"erro": "Conflito de dados no banco."}, 400
        except Exception as e:
            session.rollback()
            return {"erro": f"Erro interno: {str(e)}"}, 500
        finally:
            session.close()

# ==========================================
# DELETE / INACTIVATE (D)
# ==========================================
@funcionarios_ns.route('/<int:id>')
@funcionarios_ns.response(404, 'Funcionário não encontrado.')
class FuncionarioDelete(Resource):
    def delete(self, id):
        session = DatabaseManager.get_session()
        try:
            admin, erro = get_admin_from_header(session)
            if erro:
                return {"erro": erro}, 403

            func = session.query(Funcionario).get(id)
            if not func:
                return {"erro": "Funcionário não encontrado."}, 404

            # Impedir auto-exclusão
            if admin.id == func.id:
                return {"erro": "Um administrador não pode excluir ou inativar a si mesmo."}, 400

            # Impedir exclusão do último administrador
            if func.cargo and func.cargo.lower() == 'administrador':
                total_admins = session.query(Funcionario).filter(Funcionario.cargo.ilike('administrador')).count()
                if total_admins <= 1:
                    return {"erro": "Não é possível remover o último administrador do sistema."}, 400

            # Removemos o funcionário (neste caso, delete real para simplificar, mas o critério pede para inativar ou excluir)
            # O CASCADE removeria o usuário também, o que deleta o funcionário.
            nome_removido = func.nome
            session.delete(func)
            session.commit()
            
            logger.warning(f"Admin ID {admin.id} ({admin.nome}) EXCLUIU o funcionário ID {id} ({nome_removido}).")
            
            return {"mensagem": "Funcionário excluído/inativado com sucesso."}, 200
            
        except IntegrityError as e:
            session.rollback()
            return {"erro": "Não é possível excluir o funcionário pois ele possui transações vinculadas (sugere-se inativação lógica)."}, 400
        except Exception as e:
            session.rollback()
            return {"erro": f"Erro ao excluir funcionário: {str(e)}"}, 500
        finally:
            session.close()
