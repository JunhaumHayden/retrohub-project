"""
Testes para os endpoints de funcionários.
Testa o fluxo completo de funcionários: cadastro, listagem, atualização e exclusão.
"""
import pytest
from datetime import date

from app.models import Funcionario
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


@pytest.fixture
def admin_funcionario(test_container):
    """Cria um funcionário administrador para testes."""
    usuario_service = test_container.usuario_service
    
    admin = usuario_service.create_funcionario(
        Funcionario(
            nome='Admin Teste',
            cpf='12345678901',
            email='admin@test.com',
            senha='senha123',
            matricula='ADM001',
            cargo='Administrador',
            data_nascimento=date(1990, 1, 1)
        )
    )
    return admin


class TestFuncionariosRotas:
    """Suite de testes para as rotas de funcionários."""

    def test_cadastrar_funcionario_sucesso(self, app_client, admin_funcionario):
        """
        Testa o cadastro de um funcionário com dados válidos.
        Esperado: Funcionário criado com sucesso e status 201.
        """
        data = {
            'nome': 'Funcionario Teste',
            'cpf': '98765432101',
            'email': 'func@test.com',
            'senha': 'senha123',
            'matricula': 'F001',
            'cargo': 'Vendedor',
            'data_nascimento': '2000-01-01'
        }
        
        headers = {'X-Admin-Id': str(admin_funcionario.id)}
        response = app_client.post('/api/funcionarios', json=data, headers=headers)
        
        assert response.status_code == 201
        response_data = response.get_json()
        assert response_data['nome'] == 'Funcionario Teste'
        assert response_data['cpf'] == '98765432101'
        assert response_data['email'] == 'func@test.com'
        assert response_data['matricula'] == 'F001'
        assert 'id' in response_data

    def test_cadastrar_funcionario_sem_header_admin(self, app_client):
        """
        Testa o cadastro de um funcionário sem header X-Admin-Id.
        Esperado: Erro de permissão e status 403.
        """
        data = {
            'nome': 'Funcionario Teste',
            'cpf': '98765432101',
            'email': 'func@test.com',
            'senha': 'senha123',
            'matricula': 'F001',
            'cargo': 'Vendedor',
            'data_nascimento': '2000-01-01'
        }
        
        response = app_client.post('/api/funcionarios', json=data)
        
        assert response.status_code == 403
        response_data = response.get_json()
        assert 'erro' in response_data
        assert 'X-Admin-Id' in response_data['erro']

    def test_cadastrar_funcionario_email_invalido(self, app_client, admin_funcionario):
        """
        Testa o cadastro de um funcionário com email inválido.
        Esperado: Erro de validação e status 400.
        """
        data = {
            'nome': 'Funcionario Teste',
            'cpf': '98765432101',
            'email': 'email-invalido',
            'senha': 'senha123',
            'matricula': 'F001',
            'cargo': 'Vendedor',
            'data_nascimento': '2000-01-01'
        }
        
        headers = {'X-Admin-Id': str(admin_funcionario.id)}
        response = app_client.post('/api/funcionarios', json=data, headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'erro' in response_data
        assert 'Formato de e-mail inválido' in response_data['erro']

    def test_cadastrar_funcionario_idade_insuficiente(self, app_client, admin_funcionario):
        """
        Testa o cadastro de um funcionário com idade menor que 18 anos.
        Esperado: Erro de validação e status 400.
        """
        data = {
            'nome': 'Funcionario Teste',
            'cpf': '98765432101',
            'email': 'func@test.com',
            'senha': 'senha123',
            'matricula': 'F001',
            'cargo': 'Vendedor',
            'data_nascimento': '2015-01-01'  # Menor de 18 anos
        }
        
        headers = {'X-Admin-Id': str(admin_funcionario.id)}
        response = app_client.post('/api/funcionarios', json=data, headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'erro' in response_data
        assert 'pelo menos 18 anos' in response_data['erro']

    def test_cadastrar_funcionario_cpf_duplicado(self, app_client, admin_funcionario, test_container):
        """
        Testa o cadastro de um funcionário com CPF já existente.
        Esperado: Erro de validação e status 400.
        """
        usuario_service = test_container.usuario_service
        
        # Criar primeiro funcionário
        func1 = usuario_service.create_funcionario(
            Funcionario(
                nome='Funcionario 1',
                cpf='98765432101',
                email='func1@test.com',
                senha='senha123',
                matricula='F001',
                cargo='Vendedor',
                data_nascimento=date(2000, 1, 1)
            )
        )
        
        # Tentar criar segundo funcionário com mesmo CPF
        data = {
            'nome': 'Funcionario 2',
            'cpf': '98765432101',
            'email': 'func2@test.com',
            'senha': 'senha123',
            'matricula': 'F002',
            'cargo': 'Vendedor',
            'data_nascimento': '2000-01-01'
        }
        
        headers = {'X-Admin-Id': str(admin_funcionario.id)}
        response = app_client.post('/api/funcionarios', json=data, headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'erro' in response_data
        assert 'CPF' in response_data['erro']

    def test_cadastrar_funcionario_matricula_duplicado(self, app_client, admin_funcionario, test_container):
        """
        Testa o cadastro de um funcionário com matrícula já existente.
        Esperado: Erro de validação e status 400.
        """
        usuario_service = test_container.usuario_service
        
        # Criar primeiro funcionário
        func1 = usuario_service.create_funcionario(
            Funcionario(
                nome='Funcionario 1',
                cpf='98765432101',
                email='func1@test.com',
                senha='senha123',
                matricula='F001',
                cargo='Vendedor',
                data_nascimento=date(2000, 1, 1)
            )
        )
        
        # Tentar criar segundo funcionário com mesma matrícula
        data = {
            'nome': 'Funcionario 2',
            'cpf': '87654321098',
            'email': 'func2@test.com',
            'senha': 'senha123',
            'matricula': 'F001',
            'cargo': 'Vendedor',
            'data_nascimento': '2000-01-01'
        }
        
        headers = {'X-Admin-Id': str(admin_funcionario.id)}
        response = app_client.post('/api/funcionarios', json=data, headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'erro' in response_data
        assert 'Matrícula' in response_data['erro']

    def test_listar_funcionarios(self, app_client, test_container):
        """
        Testa a listagem de todos os funcionários.
        Esperado: Lista de funcionários com status 200.
        """
        usuario_service = test_container.usuario_service
        
        # Criar alguns funcionários
        usuario_service.create_funcionario(
            Funcionario(
                nome='Funcionario 1',
                cpf='12345678901',
                email='func1@test.com',
                senha='senha123',
                matricula='F001',
                cargo='Vendedor',
                data_nascimento=date(2000, 1, 1)
            )
        )
        usuario_service.create_funcionario(
            Funcionario(
                nome='Funcionario 2',
                cpf='98765432101',
                email='func2@test.com',
                senha='senha123',
                matricula='F002',
                cargo='Gerente',
                data_nascimento=date(2000, 1, 1)
            )
        )
        
        response = app_client.get('/api/funcionarios')
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert isinstance(response_data, list)
        assert len(response_data) >= 2

    def test_get_funcionario_by_id(self, app_client, test_container):
        """
        Testa a busca de um funcionário por ID.
        Esperado: Funcionário encontrado com status 200.
        """
        usuario_service = test_container.usuario_service
        
        funcionario = usuario_service.create_funcionario(
            Funcionario(
                nome='Funcionario Teste',
                cpf='12345678901',
                email='func@test.com',
                senha='senha123',
                matricula='F001',
                cargo='Vendedor',
                data_nascimento=date(2000, 1, 1)
            )
        )
        
        response = app_client.get(f'/api/funcionarios/{funcionario.id}')
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['id'] == funcionario.id
        assert response_data['nome'] == 'Funcionario Teste'

    def test_get_funcionario_by_id_nao_encontrado(self, app_client):
        """
        Testa a busca de um funcionário com ID inexistente.
        Esperado: Erro com status 404.
        """
        response = app_client.get('/api/funcionarios/99999')
        
        assert response.status_code == 404
        response_data = response.get_json()
        assert 'erro' in response_data

    def test_atualizar_funcionario_sucesso(self, app_client, admin_funcionario, test_container):
        """
        Testa a atualização de um funcionário com dados válidos.
        Esperado: Funcionário atualizado com sucesso e status 200.
        """
        usuario_service = test_container.usuario_service
        
        funcionario = usuario_service.create_funcionario(
            Funcionario(
                nome='Funcionario Teste',
                cpf='98765432101',
                email='func@test.com',
                senha='senha123',
                matricula='F001',
                cargo='Vendedor',
                data_nascimento=date(2000, 1, 1)
            )
        )
        
        data = {
            'nome': 'Funcionario Atualizado',
            'cargo': 'Gerente'
        }
        
        headers = {'X-Admin-Id': str(admin_funcionario.id)}
        response = app_client.put(f'/api/funcionarios/{funcionario.id}', json=data, headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['nome'] == 'Funcionario Atualizado'
        assert response_data['cargo'] == 'Gerente'

    def test_atualizar_funcionario_sem_header_admin(self, app_client, test_container):
        """
        Testa a atualização de um funcionário sem header X-Admin-Id.
        Esperado: Erro de permissão e status 403.
        """
        usuario_service = test_container.usuario_service
        
        funcionario = usuario_service.create_funcionario(
            Funcionario(
                nome='Funcionario Teste',
                cpf='98765432101',
                email='func@test.com',
                senha='senha123',
                matricula='F001',
                cargo='Vendedor',
                data_nascimento=date(2000, 1, 1)
            )
        )
        
        data = {
            'nome': 'Funcionario Atualizado'
        }
        
        response = app_client.put(f'/api/funcionarios/{funcionario.id}', json=data)
        
        assert response.status_code == 403
        response_data = response.get_json()
        assert 'erro' in response_data
        assert 'X-Admin-Id' in response_data['erro']

    def test_atualizar_funcionario_nao_encontrado(self, app_client, admin_funcionario):
        """
        Testa a atualização de um funcionário com ID inexistente.
        Esperado: Erro com status 404.
        """
        data = {
            'nome': 'Funcionario Atualizado'
        }
        
        headers = {'X-Admin-Id': str(admin_funcionario.id)}
        response = app_client.put('/api/funcionarios/99999', json=data, headers=headers)
        
        assert response.status_code == 404
        response_data = response.get_json()
        assert 'erro' in response_data

    def test_rebaixar_ultimo_admin(self, app_client, test_container):
        """
        Testa a tentativa de rebaixar o último administrador.
        Esperado: Erro de validação e status 400.
        """
        usuario_service = test_container.usuario_service
        
        # Criar único admin
        admin = usuario_service.create_funcionario(
            Funcionario(
                nome='Admin Único',
                cpf='12345678901',
                email='admin@test.com',
                senha='senha123',
                matricula='ADM001',
                cargo='Administrador',
                data_nascimento=date(1990, 1, 1)
            )
        )
        
        data = {
            'cargo': 'Vendedor'
        }
        
        headers = {'X-Admin-Id': str(admin.id)}
        response = app_client.put(f'/api/funcionarios/{admin.id}', json=data, headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'erro' in response_data
        assert 'último administrador' in response_data['erro']

    def test_deletar_funcionario_sucesso(self, app_client, admin_funcionario, test_container):
        """
        Testa a exclusão de um funcionário.
        Esperado: Funcionário excluído com sucesso e status 200.
        """
        usuario_service = test_container.usuario_service
        
        funcionario = usuario_service.create_funcionario(
            Funcionario(
                nome='Funcionario Teste',
                cpf='98765432101',
                email='func@test.com',
                senha='senha123',
                matricula='F001',
                cargo='Vendedor',
                data_nascimento=date(2000, 1, 1)
            )
        )
        
        headers = {'X-Admin-Id': str(admin_funcionario.id)}
        response = app_client.delete(f'/api/funcionarios/{funcionario.id}', headers=headers)
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert 'mensagem' in response_data

    def test_deletar_funcionario_sem_header_admin(self, app_client, test_container):
        """
        Testa a exclusão de um funcionário sem header X-Admin-Id.
        Esperado: Erro de permissão e status 403.
        """
        usuario_service = test_container.usuario_service
        
        funcionario = usuario_service.create_funcionario(
            Funcionario(
                nome='Funcionario Teste',
                cpf='98765432101',
                email='func@test.com',
                senha='senha123',
                matricula='F001',
                cargo='Vendedor',
                data_nascimento=date(2000, 1, 1)
            )
        )
        
        response = app_client.delete(f'/api/funcionarios/{funcionario.id}')
        
        assert response.status_code == 403
        response_data = response.get_json()
        assert 'erro' in response_data
        assert 'X-Admin-Id' in response_data['erro']

    def test_deletar_funcionario_nao_encontrado(self, app_client, admin_funcionario):
        """
        Testa a exclusão de um funcionário com ID inexistente.
        Esperado: Erro com status 404.
        """
        headers = {'X-Admin-Id': str(admin_funcionario.id)}
        response = app_client.delete('/api/funcionarios/99999', headers=headers)
        
        assert response.status_code == 404
        response_data = response.get_json()
        assert 'erro' in response_data

    def test_deletar_ultimo_admin(self, app_client, test_container):
        """
        Testa a tentativa de excluir o último administrador.
        Esperado: Erro de validação e status 400.
        """
        usuario_service = test_container.usuario_service
        
        # Criar único admin
        admin = usuario_service.create_funcionario(
            Funcionario(
                nome='Admin Único',
                cpf='12345678901',
                email='admin@test.com',
                senha='senha123',
                matricula='ADM001',
                cargo='Administrador',
                data_nascimento=date(1990, 1, 1)
            )
        )
        
        headers = {'X-Admin-Id': str(admin.id)}
        response = app_client.delete(f'/api/funcionarios/{admin.id}', headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'erro' in response_data
        assert 'último administrador' in response_data['erro']

    def test_auto_exclusao_admin(self, app_client, test_container):
        """
        Testa a tentativa de um administrador se excluir.
        Esperado: Erro de validação e status 400.
        """
        usuario_service = test_container.usuario_service
        
        # Criar admin
        admin = usuario_service.create_funcionario(
            Funcionario(
                nome='Admin Teste',
                cpf='12345678901',
                email='admin@test.com',
                senha='senha123',
                matricula='ADM001',
                cargo='Administrador',
                data_nascimento=date(1990, 1, 1)
            )
        )
        
        headers = {'X-Admin-Id': str(admin.id)}
        response = app_client.delete(f'/api/funcionarios/{admin.id}', headers=headers)
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'erro' in response_data
        assert 'não pode excluir a si mesmo' in response_data['erro']
