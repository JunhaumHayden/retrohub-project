import re
from datetime import datetime
from flask import request
from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

from app.models import Cliente, Usuario
from app.database.factories.database_manager import DatabaseManager
from app.database.MockDataSource import MockDataSource

# Criar namespace para clientes
clientes_ns = Namespace('clientes', description='Operações relacionadas aos clientes', path='/api/clientes')

# Modelos para documentação Swagger
cliente_model = clientes_ns.model('Cliente', {
    'id': fields.Integer(description='ID do cliente'),
    'nome': fields.String(description='Nome do cliente'),
    'cpf': fields.String(description='CPF do cliente'),
    'email': fields.String(description='Email do cliente'),
    'data_cadastro': fields.Date(description='Data de cadastro'),
    'data_nascimento': fields.Date(description='Data de nascimento'),
    'dados_pagamento': fields.String(description='Dados de pagamento')
})

cliente_input_model = clientes_ns.model('ClienteInput', {
    'nome': fields.String(required=True, description='Nome do cliente'),
    'cpf': fields.String(required=True, description='CPF do cliente'),
    'email': fields.String(required=True, description='Email do cliente'),
    'senha': fields.String(required=True, description='Senha do cliente'),
    'data_nascimento': fields.String(required=True, description='Data de nascimento (YYYY-MM-DD)'),
    'dados_pagamento': fields.String(description='Dados de pagamento')
})

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def calculate_age(birthdate):
    today = datetime.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

def serialize_cliente(cliente: Cliente):
    """Função utilitária para serializar um objeto Cliente."""
    return {
        "id": cliente.id,
        "nome": cliente.nome,
        "cpf": cliente.cpf,
        "email": cliente.email,
        "data_cadastro": cliente.data_cadastro.isoformat() if cliente.data_cadastro else None,
        "data_nascimento": cliente.data_nascimento.isoformat() if cliente.data_nascimento else None,
        "dados_pagamento": cliente.dados_pagamento
    }

# ==========================================
# CREATE (C)
# ==========================================
@clientes_ns.route('/cadastro')
class CadastroClienteResource(Resource):
    @clientes_ns.expect(cliente_input_model)
    def post(self):
        data = request.get_json()

        if not data:
            return {"erro": "Dados não fornecidos."}, 400

        required_fields = ['nome', 'cpf', 'email', 'senha', 'data_nascimento']
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
            return {"erro": "O cliente deve ter pelo menos 18 anos."}, 400

        session = DatabaseManager.get_session()
        
        try:
            email_exists = session.query(Usuario).filter_by(email=data['email']).first()
            if email_exists:
                return {"erro": "E-mail já cadastrado."}, 400
                
            cpf_exists = session.query(Usuario).filter_by(cpf=data['cpf']).first()
            if cpf_exists:
                return {"erro": "CPF já cadastrado."}, 400

            senha_hash = generate_password_hash(data['senha'])

            novo_cliente = Cliente(
                nome=data['nome'],
                cpf=data['cpf'],
                email=data['email'],
                senha=senha_hash,
                data_nascimento=data_nascimento,
                dados_pagamento=data.get('dados_pagamento')
            )

            session.add(novo_cliente)
            session.commit()

            return serialize_cliente(novo_cliente), 201

        except IntegrityError as e:
            session.rollback()
            return {"erro": "Conflito de dados: E-mail ou CPF já existentes."}, 400
        except Exception as e:
            session.rollback()
            return {"erro": f"Erro interno do servidor: {str(e)}"}, 500
        finally:
            session.close()

# ==========================================
# READ ALL (R) - Lista todos os clientes
# ==========================================
@clientes_ns.route('/')
class ListaClientesResource(Resource):
    def get(self):
        try:
            clientes = MockDataSource.get_all(Cliente)
            # Retorna a lista mapeando todos os clientes usando a função serializadora
            return [serialize_cliente(c) for c in clientes], 200
        except Exception as e:
            return {"erro": f"Erro ao buscar clientes: {str(e)}"}, 500

# ==========================================
# READ ONE (R) - Busca cliente por ID
# UPDATE (U) - Atualiza os dados de um cliente  
# DELETE (D) - Exclui um cliente
# ==========================================
@clientes_ns.route('/<int:id>')
class ClienteResource(Resource):
    def get(self, id):
        """Busca cliente por ID"""
        try:
            cliente = MockDataSource.get_by_id(Cliente, id)
            if not cliente:
                return {"erro": "Cliente não encontrado."}, 404
            
            return serialize_cliente(cliente), 200
        except Exception as e:
            return {"erro": f"Erro ao buscar cliente: {str(e)}"}, 500

    @clientes_ns.expect(cliente_input_model)
    def put(self, id):
        """Atualiza os dados de um cliente"""
        data = request.get_json()
        if not data:
            return {"erro": "Dados não fornecidos."}, 400

        session = DatabaseManager.get_session()
        try:
            cliente = session.query(Cliente).get(id)
            if not cliente:
                return {"erro": "Cliente não encontrado."}, 404

            # Valida unicidade de email se estiver sendo alterado
            if 'email' in data and data['email'] != cliente.email:
                if not is_valid_email(data['email']):
                    return {"erro": "Formato de e-mail inválido."}, 400
                
                email_exists = session.query(Usuario).filter_by(email=data['email']).first()
                if email_exists:
                    return {"erro": "E-mail já cadastrado por outro usuário."}, 400
                cliente.email = data['email']

            # Atualiza os outros campos permitidos
            if 'nome' in data:
                cliente.nome = data['nome']
            
            if 'dados_pagamento' in data:
                cliente.dados_pagamento = data['dados_pagamento']

            if 'senha' in data and data['senha']:
                cliente.senha = generate_password_hash(data['senha'])
                
            if 'data_nascimento' in data:
                try:
                    data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
                    if calculate_age(data_nascimento) < 18:
                        return {"erro": "A nova idade seria menor que 18 anos."}, 400
                    cliente.data_nascimento = data_nascimento
                except ValueError:
                    return {"erro": "Formato de data de nascimento inválido."}, 400

            # O CPF geralmente não deve ser alterado (regra de negócio comum), 
            # mas se quiser permitir, precisaria adicionar a checagem de unicidade igual ao e-mail.

            session.commit()
            return serialize_cliente(cliente), 200

        except IntegrityError as e:
            session.rollback()
            return {"erro": "Conflito de dados no banco de dados."}, 400
        except Exception as e:
            session.rollback()
            return {"erro": f"Erro interno: {str(e)}"}, 500
        finally:
            session.close()

    def delete(self, id):
        """Exclui um cliente"""
        session = DatabaseManager.get_session()
        try:
            cliente = session.query(Cliente).get(id)
            if not cliente:
                return {"erro": "Cliente não encontrado."}, 404

            session.delete(cliente)
            session.commit()
            
            return {"mensagem": "Cliente excluído com sucesso."}, 200
            
        except IntegrityError as e:
            session.rollback()
            return {"erro": "Não é possível excluir o cliente pois existem transações ou dependências ligadas a ele."}, 400
        except Exception as e:
            session.rollback()
            return {"erro": f"Erro ao excluir cliente: {str(e)}"}, 500
        finally:
            session.close()
