"""Rotas REST para o recurso Funcionario.

Refatorado para usar o `Container` + `UsuarioService` em vez de SQLAlchemy.
A autorização por header ``X-Admin-Id`` foi mantida, mas agora consulta
funcionários através do serviço.
"""

import logging
import re
from datetime import datetime

from flask import request
from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash

from app.container.container import container
from app.models import Funcionario

funcionarios_ns = Namespace(
    'funcionarios',
    description='Operações relacionadas aos funcionários',
    path='/api/funcionarios',
)

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
    'data_nascimento': fields.Date(description='Data de nascimento'),
})

funcionario_input_model = funcionarios_ns.model('FuncionarioInput', {
    'nome': fields.String(required=True, description='Nome do funcionário'),
    'cpf': fields.String(required=True, description='CPF do funcionário'),
    'email': fields.String(required=True, description='Email do funcionário'),
    'senha': fields.String(required=True, description='Senha do funcionário'),
    'matricula': fields.String(required=True, description='Matrícula do funcionário'),
    'cargo': fields.String(description='Cargo do funcionário'),
    'setor': fields.String(description='Setor do funcionário'),
    'data_nascimento': fields.String(
        required=True, description='Data de nascimento (YYYY-MM-DD)'
    ),
    'data_admissao': fields.String(description='Data de admissão (YYYY-MM-DD)'),
})

logger = logging.getLogger(__name__)


def _is_valid_email(email: str) -> bool:
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None


def _calculate_age(birthdate) -> int:
    today = datetime.today().date()
    return (
        today.year
        - birthdate.year
        - ((today.month, today.day) < (birthdate.month, birthdate.day))
    )


def _serialize_funcionario(func: Funcionario) -> dict:
    return {
        'id': func.id,
        'nome': func.nome,
        'cpf': func.cpf,
        'email': func.email,
        'matricula': func.matricula,
        'cargo': func.cargo,
        'setor': func.setor,
        'data_admissao': (
            func.data_admissao.isoformat() if func.data_admissao else None
        ),
        'data_cadastro': (
            func.data_cadastro.isoformat() if func.data_cadastro else None
        ),
        'data_nascimento': (
            func.data_nascimento.isoformat() if func.data_nascimento else None
        ),
    }


def _get_admin_from_header():
    """Recupera (e valida) o admin a partir de ``X-Admin-Id``."""
    admin_id = request.headers.get('X-Admin-Id')
    if not admin_id:
        return None, 'Header X-Admin-Id é obrigatório para esta operação.'
    try:
        admin_id = int(admin_id)
    except ValueError:
        return None, 'X-Admin-Id deve ser um número inteiro.'

    admin = container.usuario_service.get_funcionario_by_id(admin_id)
    if not admin:
        return None, 'Administrador não encontrado.'
    if not admin.cargo or admin.cargo.lower() != 'administrador':
        return None, 'Usuário não tem permissão de Administrador.'
    return admin, None


@funcionarios_ns.route('/')
class FuncionariosListResource(Resource):
    def get(self):
        try:
            funcionarios = container.usuario_service.list_funcionarios()
            return [_serialize_funcionario(f) for f in funcionarios], 200
        except Exception as exc:  # noqa: BLE001
            logger.exception('Erro ao listar funcionários')
            return {'erro': f'Erro ao buscar funcionários: {exc}'}, 500

    @funcionarios_ns.expect(funcionario_input_model)
    def post(self):
        admin, erro = _get_admin_from_header()
        if erro:
            return {'erro': erro}, 403

        data = request.get_json() or {}
        required = ['nome', 'cpf', 'email', 'senha', 'data_nascimento',
                    'matricula', 'cargo']
        for field in required:
            if not data.get(field):
                return {'erro': f"O campo '{field}' é obrigatório."}, 400

        if not _is_valid_email(data['email']):
            return {'erro': 'Formato de e-mail inválido.'}, 400

        try:
            data_nascimento = datetime.strptime(
                data['data_nascimento'], '%Y-%m-%d'
            ).date()
        except ValueError:
            return {
                'erro': 'Formato de data de nascimento inválido. Use AAAA-MM-DD.'
            }, 400
        if _calculate_age(data_nascimento) < 18:
            return {'erro': 'O funcionário deve ter pelo menos 18 anos.'}, 400

        data_admissao = data.get('data_admissao') or datetime.today().strftime(
            '%Y-%m-%d'
        )
        try:
            data_admissao = datetime.strptime(data_admissao, '%Y-%m-%d').date()
        except ValueError:
            return {'erro': 'Formato de data de admissão inválido.'}, 400

        novo = Funcionario(
            nome=data['nome'],
            cpf=data['cpf'],
            email=data['email'],
            senha=generate_password_hash(data['senha']),
            data_nascimento=data_nascimento,
            matricula=data['matricula'],
            cargo=data['cargo'],
            setor=data.get('setor'),
            data_admissao=data_admissao,
        )

        try:
            criado = container.usuario_service.create_funcionario(novo)
        except ValueError as exc:
            return {'erro': str(exc)}, 400
        except Exception as exc:  # noqa: BLE001
            logger.exception('Erro ao criar funcionário')
            return {'erro': f'Erro interno do servidor: {exc}'}, 500

        logger.info(
            'Admin ID %s (%s) CRIOU o funcionário ID %s (%s).',
            admin.id, admin.nome, criado.id, criado.nome,
        )
        return _serialize_funcionario(criado), 201


@funcionarios_ns.route('/<int:id>')
class FuncionarioResource(Resource):
    def get(self, id):
        func = container.usuario_service.get_funcionario_by_id(id)
        if not func:
            return {'erro': 'Funcionário não encontrado.'}, 404
        return _serialize_funcionario(func), 200

    @funcionarios_ns.expect(funcionario_input_model)
    def put(self, id):
        admin, erro = _get_admin_from_header()
        if erro:
            return {'erro': erro}, 403

        data = request.get_json() or {}
        if not data:
            return {'erro': 'Dados não fornecidos.'}, 400

        func = container.usuario_service.get_funcionario_by_id(id)
        if not func:
            return {'erro': 'Funcionário não encontrado.'}, 404

        if 'email' in data and data['email'] != func.email:
            if not _is_valid_email(data['email']):
                return {'erro': 'Formato de e-mail inválido.'}, 400

        if 'data_nascimento' in data and data['data_nascimento']:
            try:
                data_nasc = datetime.strptime(
                    data['data_nascimento'], '%Y-%m-%d'
                ).date()
            except ValueError:
                return {'erro': 'Formato de data de nascimento inválido.'}, 400
            if _calculate_age(data_nasc) < 18:
                return {'erro': 'A nova idade seria menor que 18 anos.'}, 400
            data['data_nascimento'] = data_nasc

        if 'data_admissao' in data and data['data_admissao']:
            try:
                data['data_admissao'] = datetime.strptime(
                    data['data_admissao'], '%Y-%m-%d'
                ).date()
            except ValueError:
                return {'erro': 'Formato de data de admissão inválido.'}, 400

        if data.get('senha'):
            data['senha'] = generate_password_hash(data['senha'])

        try:
            atualizado = container.usuario_service.update_usuario(id, data)
        except ValueError as exc:
            return {'erro': str(exc)}, 400
        except Exception as exc:  # noqa: BLE001
            logger.exception('Erro ao atualizar funcionário')
            return {'erro': f'Erro interno: {exc}'}, 500

        if not atualizado:
            return {'erro': 'Funcionário não encontrado.'}, 404

        logger.info(
            'Admin ID %s (%s) ATUALIZOU o funcionário ID %s.',
            admin.id, admin.nome, id,
        )
        return _serialize_funcionario(atualizado), 200

    def delete(self, id):
        admin, erro = _get_admin_from_header()
        if erro:
            return {'erro': erro}, 403

        func = container.usuario_service.get_funcionario_by_id(id)
        if not func:
            return {'erro': 'Funcionário não encontrado.'}, 404

        if admin.id == func.id:
            return {
                'erro': 'Um administrador não pode excluir ou inativar a si mesmo.'
            }, 400

        # Bloqueia exclusão do último admin
        if func.cargo and func.cargo.lower() == 'administrador':
            todos = container.usuario_service.list_funcionarios()
            total_admins = sum(
                1 for f in todos
                if f.cargo and f.cargo.lower() == 'administrador'
            )
            if total_admins <= 1:
                return {
                    'erro': 'Não é possível remover o último administrador do sistema.'
                }, 400

        try:
            removido = container.usuario_service.delete_usuario(id)
        except Exception as exc:  # noqa: BLE001
            logger.exception('Erro ao excluir funcionário')
            return {'erro': f'Erro ao excluir funcionário: {exc}'}, 500

        if not removido:
            return {'erro': 'Funcionário não encontrado.'}, 404
        logger.warning(
            'Admin ID %s (%s) EXCLUIU o funcionário ID %s.',
            admin.id, admin.nome, id,
        )
        return {'mensagem': 'Funcionário excluído/inativado com sucesso.'}, 200
