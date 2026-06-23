"""
Testes para os endpoints de clientes.
Testa o fluxo completo de clientes: cadastro, listagem, atualização e exclusão.
"""
import pytest
from datetime import date, timedelta

from app.models import Cliente
from app.container.container import Container


@pytest.fixture(scope="function")
def app_client(test_container):
    """Cria um cliente Flask para testes HTTP."""
    from app import create_app
    import os
    os.environ['APP_MODE'] = 'sqlite'
    
    test_config = {
        'db_type': 'sqlite',
        'db_url': 'sqlite:///:memory:'
    }
    app = create_app(test_config=test_config)
    app.config['TESTING'] = True
    
    with app.app_context():
        yield app.test_client()


class TestClientesRotas:
    """Suite de testes para as rotas de clientes."""

    def test_cadastrar_cliente_sucesso(self, app_client):
        """
        Testa o cadastro de um cliente com dados válidos.
        Esperado: Cliente criado com sucesso e status 201.
        """
        data = {
            'nome': 'Cliente Teste',
            'cpf': '12345678901',
            'email': 'cliente@test.com',
            'senha': 'senha123',
            'data_nascimento': '2000-01-01'
        }
        
        response = app_client.post('/api/clientes/cadastro', json=data)
        
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['nome'] == 'Cliente Teste'
        assert response_data['cpf'] == '12345678901'
        assert response_data['email'] == 'cliente@test.com'
        assert 'id' in response_data

    def test_cadastrar_cliente_email_invalido(self, app_client):
        """
        Testa o cadastro de um cliente com email inválido.
        Esperado: Erro de validação e status 400.
        """
        data = {
            'nome': 'Cliente Teste',
            'cpf': '12345678901',
            'email': 'email-invalido',
            'senha': 'senha123',
            'data_nascimento': '2000-01-01'
        }
        
        response = app_client.post('/api/clientes/cadastro', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'erro' in response_data
        assert 'Formato de e-mail inválido' in response_data['erro']

    def test_cadastrar_cliente_idade_insuficiente(self, app_client):
        """
        Testa o cadastro de um cliente com idade menor que 18 anos.
        Esperado: Erro de validação e status 400.
        """
        data = {
            'nome': 'Cliente Teste',
            'cpf': '12345678901',
            'email': 'cliente@test.com',
            'senha': 'senha123',
            'data_nascimento': '2015-01-01'  # Menor de 18 anos
        }
        
        response = app_client.post('/api/clientes/cadastro', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'erro' in response_data
        assert 'pelo menos 18 anos' in response_data['erro']

    def test_cadastrar_cliente_cpf_duplicado(self, app_client, test_container):
        """
        Testa o cadastro de um cliente com CPF já existente.
        Esperado: Erro de validação e status 400.
        """
        usuario_service = test_container.usuario_service
        
        # Criar primeiro cliente
        cliente1 = usuario_service.create_cliente(
            Cliente(
                nome='Cliente 1',
                cpf='12345678901',
                email='cliente1@test.com',
                senha='senha123',
                data_nascimento=date(2000, 1, 1)
            )
        )
        
        # Tentar criar segundo cliente com mesmo CPF
        data = {
            'nome': 'Cliente 2',
            'cpf': '12345678901',
            'email': 'cliente2@test.com',
            'senha': 'senha123',
            'data_nascimento': '2000-01-01'
        }
        
        response = app_client.post('/api/clientes/cadastro', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'erro' in response_data
        assert 'CPF' in response_data['erro']

    def test_cadastrar_cliente_email_duplicado(self, app_client, test_container):
        """
        Testa o cadastro de um cliente com email já existente.
        Esperado: Erro de validação e status 400.
        """
        usuario_service = test_container.usuario_service
        
        # Criar primeiro cliente
        cliente1 = usuario_service.create_cliente(
            Cliente(
                nome='Cliente 1',
                cpf='12345678901',
                email='cliente@test.com',
                senha='senha123',
                data_nascimento=date(2000, 1, 1)
            )
        )
        
        # Tentar criar segundo cliente com mesmo email
        data = {
            'nome': 'Cliente 2',
            'cpf': '98765432101',
            'email': 'cliente@test.com',
            'senha': 'senha123',
            'data_nascimento': '2000-01-01'
        }
        
        response = app_client.post('/api/clientes/cadastro', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'erro' in response_data
        assert 'Email' in response_data['erro']

    def test_listar_clientes(self, app_client, test_container):
        """
        Testa a listagem de todos os clientes.
        Esperado: Lista de clientes com status 200.
        """
        usuario_service = test_container.usuario_service
        
        # Criar alguns clientes
        usuario_service.create_cliente(
            Cliente(
                nome='Cliente 1',
                cpf='12345678901',
                email='cliente1@test.com',
                senha='senha123',
                data_nascimento=date(2000, 1, 1)
            )
        )
        usuario_service.create_cliente(
            Cliente(
                nome='Cliente 2',
                cpf='98765432101',
                email='cliente2@test.com',
                senha='senha123',
                data_nascimento=date(2000, 1, 1)
            )
        )
        
        response = app_client.get('/api/clientes')
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert isinstance(response_data, list)
        assert len(response_data) >= 2

    def test_get_cliente_by_id(self, app_client, test_container):
        """
        Testa a busca de um cliente por ID.
        Esperado: Cliente encontrado com status 200.
        """
        usuario_service = test_container.usuario_service
        
        cliente = usuario_service.create_cliente(
            Cliente(
                nome='Cliente Teste',
                cpf='12345678901',
                email='cliente@test.com',
                senha='senha123',
                data_nascimento=date(2000, 1, 1)
            )
        )
        
        response = app_client.get(f'/api/clientes/{cliente.id}')
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['id'] == cliente.id
        assert response_data['nome'] == 'Cliente Teste'

    def test_get_cliente_by_id_nao_encontrado(self, app_client):
        """
        Testa a busca de um cliente com ID inexistente.
        Esperado: Erro com status 404.
        """
        response = app_client.get('/api/clientes/99999')
        
        assert response.status_code == 404
        response_data = response.get_json()
        assert 'erro' in response_data

    def test_atualizar_cliente_sucesso(self, app_client, test_container):
        """
        Testa a atualização de um cliente com dados válidos.
        Esperado: Cliente atualizado com sucesso e status 200.
        """
        usuario_service = test_container.usuario_service
        
        cliente = usuario_service.create_cliente(
            Cliente(
                nome='Cliente Teste',
                cpf='12345678901',
                email='cliente@test.com',
                senha='senha123',
                data_nascimento=date(2000, 1, 1)
            )
        )
        
        data = {
            'nome': 'Cliente Atualizado',
            'email': 'novo@test.com'
        }
        
        response = app_client.put(f'/api/clientes/{cliente.id}', json=data)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['nome'] == 'Cliente Atualizado'
        assert response_data['email'] == 'novo@test.com'

    def test_atualizar_cliente_email_invalido(self, app_client, test_container):
        """
        Testa a atualização de um cliente com email inválido.
        Esperado: Erro de validação e status 400.
        """
        usuario_service = test_container.usuario_service
        
        cliente = usuario_service.create_cliente(
            Cliente(
                nome='Cliente Teste',
                cpf='12345678901',
                email='cliente@test.com',
                senha='senha123',
                data_nascimento=date(2000, 1, 1)
            )
        )
        
        data = {
            'email': 'email-invalido'
        }
        
        response = app_client.put(f'/api/clientes/{cliente.id}', json=data)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'erro' in response_data
        assert 'Formato de e-mail inválido' in response_data['erro']

    def test_atualizar_cliente_nao_encontrado(self, app_client):
        """
        Testa a atualização de um cliente com ID inexistente.
        Esperado: Erro com status 404.
        """
        data = {
            'nome': 'Cliente Atualizado'
        }
        
        response = app_client.put('/api/clientes/99999', json=data)
        
        assert response.status_code == 404
        response_data = response.get_json()
        assert 'erro' in response_data

    def test_deletar_cliente_sucesso(self, app_client, test_container):
        """
        Testa a exclusão de um cliente.
        Esperado: Cliente excluído com sucesso e status 200.
        """
        usuario_service = test_container.usuario_service
        
        cliente = usuario_service.create_cliente(
            Cliente(
                nome='Cliente Teste',
                cpf='12345678901',
                email='cliente@test.com',
                senha='senha123',
                data_nascimento=date(2000, 1, 1)
            )
        )
        
        response = app_client.delete(f'/api/clientes/{cliente.id}')
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert 'mensagem' in response_data

    def test_deletar_cliente_nao_encontrado(self, app_client):
        """
        Testa a exclusão de um cliente com ID inexistente.
        Esperado: Erro com status 404.
        """
        response = app_client.delete('/api/clientes/99999')
        
        assert response.status_code == 404
        response_data = response.get_json()
        assert 'erro' in response_data
