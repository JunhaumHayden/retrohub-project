"""Rotas REST para o recurso Cliente.

Refatorado para utilizar o `Container` de injeção de dependências e o
`UsuarioService`, removendo o acoplamento com o ORM (SQLAlchemy) e com o
`DatabaseManager`. A camada de persistência fica delegada ao serviço, que
internamente usa `MockDataSource` quando ``USE_MOCK_DB=True``.
"""

import logging
import re
from datetime import datetime

from flask import request
from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash

from app.container.container import container
from app.models import Cliente

clientes_ns = Namespace(
    'clientes',
    description='Operações relacionadas aos clientes',
    path='/api/clientes',
)

cliente_model = clientes_ns.model('Cliente', {
    'id': fields.Integer(description='ID do cliente'),
    'nome': fields.String(description='Nome do cliente'),
    'cpf': fields.String(description='CPF do cliente'),
    'email': fields.String(description='Email do cliente'),
    'data_cadastro': fields.Date(description='Data de cadastro'),
    'data_nascimento': fields.Date(description='Data de nascimento'),
    'dados_pagamento': fields.String(description='Dados de pagamento'),
})

cliente_input_model = clientes_ns.model('ClienteInput', {
    'nome': fields.String(required=True, description='Nome do cliente'),
    'cpf': fields.String(required=True, description='CPF do cliente'),
    'email': fields.String(required=True, description='Email do cliente'),
    'senha': fields.String(required=True, description='Senha do cliente'),
    'data_nascimento': fields.String(
        required=True, description='Data de nascimento (YYYY-MM-DD)'
    ),
    'dados_pagamento': fields.String(description='Dados de pagamento'),
})

logger = logging.getLogger(__name__)


def _is_valid_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def _calculate_age(birthdate) -> int:
    today = datetime.today().date()
    return (
        today.year
        - birthdate.year
        - ((today.month, today.day) < (birthdate.month, birthdate.day))
    )


def _serialize_cliente(cliente: Cliente) -> dict:
    return {
        'id': cliente.id,
        'nome': cliente.nome,
        'cpf': cliente.cpf,
        'email': cliente.email,
        'data_cadastro': (
            cliente.data_cadastro.isoformat() if cliente.data_cadastro else None
        ),
        'data_nascimento': (
            cliente.data_nascimento.isoformat() if cliente.data_nascimento else None
        ),
        'dados_pagamento': getattr(cliente, 'dados_pagamento', None),
        'tipo_cliente': getattr(cliente, 'tipo_cliente', None),
    }


@clientes_ns.route('/cadastro')
class CadastroClienteResource(Resource):
    @clientes_ns.expect(cliente_input_model)
    def post(self):
        data = request.get_json() or {}

        required = ['nome', 'cpf', 'email', 'senha', 'data_nascimento']
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
            return {'erro': 'O cliente deve ter pelo menos 18 anos.'}, 400

        novo_cliente = Cliente(
            nome=data['nome'],
            cpf=data['cpf'],
            email=data['email'],
            senha=generate_password_hash(data['senha']),
            data_nascimento=data_nascimento,
            dados_pagamento=data.get('dados_pagamento'),
        )

        try:
            criado = container.usuario_service.create_cliente(novo_cliente)
        except ValueError as exc:
            return {'erro': str(exc)}, 400
        except Exception as exc:  # noqa: BLE001 - fallback de segurança
            logger.exception('Erro ao cadastrar cliente')
            return {'erro': f'Erro interno do servidor: {exc}'}, 500

        return _serialize_cliente(criado), 201


@clientes_ns.route('/')
class ListaClientesResource(Resource):
    def get(self):
        try:
            clientes = container.usuario_service.list_clientes()
            return [_serialize_cliente(c) for c in clientes], 200
        except Exception as exc:  # noqa: BLE001
            logger.exception('Erro ao listar clientes')
            return {'erro': f'Erro ao buscar clientes: {exc}'}, 500


@clientes_ns.route('/<int:id>')
class ClienteResource(Resource):
    def get(self, id):
        cliente = container.usuario_service.get_cliente_by_id(id)
        if not cliente:
            return {'erro': 'Cliente não encontrado.'}, 404
        return _serialize_cliente(cliente), 200

    @clientes_ns.expect(cliente_input_model)
    def put(self, id):
        data = request.get_json() or {}
        if not data:
            return {'erro': 'Dados não fornecidos.'}, 400

        cliente = container.usuario_service.get_cliente_by_id(id)
        if not cliente:
            return {'erro': 'Cliente não encontrado.'}, 404

        if 'email' in data and data['email'] != cliente.email:
            if not _is_valid_email(data['email']):
                return {'erro': 'Formato de e-mail inválido.'}, 400

        if 'data_nascimento' in data and data['data_nascimento']:
            try:
                data_nascimento = datetime.strptime(
                    data['data_nascimento'], '%Y-%m-%d'
                ).date()
            except ValueError:
                return {'erro': 'Formato de data de nascimento inválido.'}, 400
            if _calculate_age(data_nascimento) < 18:
                return {'erro': 'A nova idade seria menor que 18 anos.'}, 400
            data['data_nascimento'] = data_nascimento

        if data.get('senha'):
            data['senha'] = generate_password_hash(data['senha'])

        try:
            atualizado = container.usuario_service.update_usuario(id, data)
        except ValueError as exc:
            return {'erro': str(exc)}, 400
        except Exception as exc:  # noqa: BLE001
            logger.exception('Erro ao atualizar cliente')
            return {'erro': f'Erro interno: {exc}'}, 500

        if not atualizado:
            return {'erro': 'Cliente não encontrado.'}, 404
        return _serialize_cliente(atualizado), 200

    def delete(self, id):
        try:
            removido = container.usuario_service.delete_usuario(id)
        except Exception as exc:  # noqa: BLE001
            logger.exception('Erro ao excluir cliente')
            return {'erro': f'Erro ao excluir cliente: {exc}'}, 500

        if not removido:
            return {'erro': 'Cliente não encontrado.'}, 404
        return {'mensagem': 'Cliente excluído com sucesso.'}, 200
