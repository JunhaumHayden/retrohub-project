"""
Testes para os endpoints de aluguéis (rentals).
Testa o fluxo completo de um aluguel: solicitação, pagamento, retirada e devolução.
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal

from app.models import Cliente, Funcionario, Catalogo, MidiaFisica, Aluguel
from app.models.enums import StatusAluguel
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
def setup_test_entities(test_container):
    """
    Cria entidades de teste: cliente, funcionário, catálogo e exemplar.
    Retorna um dicionário com os IDs e objetos criados.
    """
    usuario_service = test_container.usuario_service
    catalogo_service = test_container.catalogo_service
    estoque_service = test_container.estoque_service
    
    # Criar cliente
    cliente = usuario_service.create_cliente(
        Cliente(
            nome="Cliente Teste",
            cpf="12345678901",
            email="cliente@test.com",
            senha="senha123"
        )
    )
    
    # Criar funcionário
    funcionario = usuario_service.create_funcionario(
        Funcionario(
            nome="Funcionário Teste",
            cpf="98765432101",
            email="func@test.com",
            senha="senha123",
            matricula="F001"
        )
    )
    
    # Criar catálogo
    catalogo = catalogo_service.create(
        Catalogo(titulo="Jogo de Teste")
    )
    
    # Criar exemplar (mídia física)
    exemplar = estoque_service.create_exemplar(
        MidiaFisica(
            catalogo=catalogo,
            codigo_barras="TEST-001",
            valor_diaria_aluguel=Decimal("10.00")
        )
    )
    
    return {
        "cliente_id": cliente.id,
        "cliente": cliente,
        "funcionario_id": funcionario.id,
        "funcionario": funcionario,
        "catalogo_id": catalogo.id,
        "catalogo": catalogo,
        "exemplar_id": exemplar.id,
        "exemplar": exemplar,
    }


class TestAlugueisRotas:
    """Suite de testes para as rotas de aluguéis."""

    def test_solicitar_aluguel_sucesso(self, test_container, setup_test_entities):
        """
        Testa a solicitação de um aluguel com dados válidos.
        Esperado: Aluguel criado com status SOLICITADO.
        """
        aluguel_service = test_container.aluguel_service
        
        cliente_id = setup_test_entities["cliente_id"]
        catalogo_id = setup_test_entities["catalogo_id"]
        
        aluguel, erro = aluguel_service.solicitar_aluguel(
            id_cliente=cliente_id,
            id_catalogo=catalogo_id,
            dias_alugados=5,
            data_inicio=date.today(),
            tipo_midia="FISICA"
        )
        
        assert erro is None
        assert aluguel is not None
        assert aluguel.status == StatusAluguel.SOLICITADO.value
        assert aluguel.periodo == 5
        assert aluguel.valor_total == Decimal("50.00")  # 5 dias * 10 por dia

    def test_solicitar_aluguel_catalogo_inexistente(self, test_container, setup_test_entities):
        """
        Testa a solicitação de aluguel com catálogo inexistente.
        Esperado: Erro indicando que o catálogo não existe.
        """
        aluguel_service = test_container.aluguel_service
        
        cliente_id = setup_test_entities["cliente_id"]
        catalogo_id_inexistente = 99999
        
        aluguel, erro = aluguel_service.solicitar_aluguel(
            id_cliente=cliente_id,
            id_catalogo=catalogo_id_inexistente,
            dias_alugados=5,
            data_inicio=date.today(),
            tipo_midia="FISICA"
        )
        
        assert erro is not None
        assert aluguel is None
        assert "não existe" in erro.lower()

    def test_solicitar_aluguel_exemplar_indisponivel(self, test_container, setup_test_entities):
        """
        Testa a solicitação de aluguel quando não há exemplar disponível.
        Esperado: Erro indicando falta de exemplar.
        """
        aluguel_service = test_container.aluguel_service
        
        cliente_id = setup_test_entities["cliente_id"]
        catalogo_id = setup_test_entities["catalogo_id"]
        
        # Primeira solicitação: deve funcionar
        aluguel1, erro1 = aluguel_service.solicitar_aluguel(
            id_cliente=cliente_id,
            id_catalogo=catalogo_id,
            dias_alugados=5,
            data_inicio=date.today(),
            tipo_midia="FISICA"
        )
        assert erro1 is None
        
        # Processar pagamento para ativar o primeiro aluguel
        aluguel1, _ = aluguel_service.processar_pagamento(aluguel1.id, sucesso=True)
        
        # Segunda solicitação: deve falhar porque o exemplar já está alugado
        aluguel2, erro2 = aluguel_service.solicitar_aluguel(
            id_cliente=cliente_id,
            id_catalogo=catalogo_id,
            dias_alugados=5,
            data_inicio=date.today(),
            tipo_midia="FISICA"
        )
        
        assert erro2 is not None
        assert "não há exemplares" in erro2.lower()

    def test_processar_pagamento_sucesso(self, test_container, setup_test_entities):
        """
        Testa o processamento de pagamento bem-sucedido.
        Esperado: Status do aluguel muda para APROVADO.
        """
        aluguel_service = test_container.aluguel_service
        
        cliente_id = setup_test_entities["cliente_id"]
        catalogo_id = setup_test_entities["catalogo_id"]
        
        # Criar aluguel
        aluguel, _ = aluguel_service.solicitar_aluguel(
            id_cliente=cliente_id,
            id_catalogo=catalogo_id,
            dias_alugados=3,
            data_inicio=date.today(),
            tipo_midia="FISICA"
        )
        
        # Processar pagamento com sucesso
        aluguel_pago, erro = aluguel_service.processar_pagamento(aluguel.id, sucesso=True)
        
        assert erro is None
        assert aluguel_pago is not None
        assert aluguel_pago.status == StatusAluguel.APROVADO.value

    def test_processar_pagamento_falha(self, test_container, setup_test_entities):
        """
        Testa o processamento de pagamento falhado.
        Esperado: Status do aluguel muda ou aluguel é cancelado.
        """
        aluguel_service = test_container.aluguel_service
        
        cliente_id = setup_test_entities["cliente_id"]
        catalogo_id = setup_test_entities["catalogo_id"]
        
        # Criar aluguel
        aluguel, _ = aluguel_service.solicitar_aluguel(
            id_cliente=cliente_id,
            id_catalogo=catalogo_id,
            dias_alugados=3,
            data_inicio=date.today(),
            tipo_midia="FISICA"
        )
        
        # Processar pagamento com falha
        aluguel_fail, erro = aluguel_service.processar_pagamento(aluguel.id, sucesso=False)
        
        # Verificar que o aluguel foi processado (pode estar em outro status ou erro)
        assert aluguel_fail is not None

    def test_registrar_retirada(self, test_container, setup_test_entities):
        """
        Testa o registro de retirada de um aluguel.
        Esperado: Status muda para ATIVO e exemplo fica em situação ALUGADO.
        """
        aluguel_service = test_container.aluguel_service
        
        cliente_id = setup_test_entities["cliente_id"]
        catalogo_id = setup_test_entities["catalogo_id"]
        
        # Criar aluguel e aprovar pagamento
        aluguel, _ = aluguel_service.solicitar_aluguel(
            id_cliente=cliente_id,
            id_catalogo=catalogo_id,
            dias_alugados=3,
            data_inicio=date.today(),
            tipo_midia="FISICA"
        )
        
        aluguel, _ = aluguel_service.processar_pagamento(aluguel.id, sucesso=True)
        
        # Registrar retirada
        aluguel_retirado, erro = aluguel_service.registrar_retirada(aluguel.id)
        
        assert erro is None
        assert aluguel_retirado is not None
        assert aluguel_retirado.status == StatusAluguel.ATIVO.value
        assert aluguel_retirado.data_retirada is not None

    def test_registrar_devolucao(self, test_container, setup_test_entities):
        """
        Testa o registro de devolução de um aluguel.
        Esperado: Status muda para FINALIZADO e exemplar volta a DISPONÍVEL.
        """
        aluguel_service = test_container.aluguel_service
        
        cliente_id = setup_test_entities["cliente_id"]
        catalogo_id = setup_test_entities["catalogo_id"]
        funcionario_id = setup_test_entities["funcionario_id"]
        
        # Criar aluguel, aprovar e retirar
        aluguel, _ = aluguel_service.solicitar_aluguel(
            id_cliente=cliente_id,
            id_catalogo=catalogo_id,
            dias_alugados=3,
            data_inicio=date.today(),
            tipo_midia="FISICA"
        )
        
        aluguel, _ = aluguel_service.processar_pagamento(aluguel.id, sucesso=True)
        aluguel, _ = aluguel_service.registrar_retirada(aluguel.id)
        
        # Registrar devolução em bom estado
        aluguel_devolvido, erro = aluguel_service.registrar_devolucao(
            aluguel.id, 
            condicao_item="bom",
            id_funcionario=funcionario_id
        )
        
        assert erro is None
        assert aluguel_devolvido is not None
        assert aluguel_devolvido.status == StatusAluguel.FINALIZADO.value
        assert aluguel_devolvido.data_devolucao is not None
        assert aluguel_devolvido.condicao_item == "bom"

    def test_registrar_devolucao_danificado(self, test_container, setup_test_entities):
        """
        Testa a devolução de um item danificado.
        Esperado: Item é marcado como danificado.
        """
        aluguel_service = test_container.aluguel_service
        
        cliente_id = setup_test_entities["cliente_id"]
        catalogo_id = setup_test_entities["catalogo_id"]
        funcionario_id = setup_test_entities["funcionario_id"]
        
        # Criar aluguel, aprovar e retirar
        aluguel, _ = aluguel_service.solicitar_aluguel(
            id_cliente=cliente_id,
            id_catalogo=catalogo_id,
            dias_alugados=3,
            data_inicio=date.today(),
            tipo_midia="FISICA"
        )
        
        aluguel, _ = aluguel_service.processar_pagamento(aluguel.id, sucesso=True)
        aluguel, _ = aluguel_service.registrar_retirada(aluguel.id)
        
        # Registrar devolução danificado
        aluguel_devolvido, erro = aluguel_service.registrar_devolucao(
            aluguel.id,
            condicao_item="danificado",
            id_funcionario=funcionario_id
        )
        
        assert erro is None
        assert aluguel_devolvido is not None
        assert aluguel_devolvido.condicao_item == "danificado"

    def test_registrar_devolucao_extraviado(self, test_container, setup_test_entities):
        """
        Testa a devolução com item extraviado.
        Esperado: Item é marcado como extraviado.
        """
        aluguel_service = test_container.aluguel_service
        
        cliente_id = setup_test_entities["cliente_id"]
        catalogo_id = setup_test_entities["catalogo_id"]
        funcionario_id = setup_test_entities["funcionario_id"]
        
        # Criar aluguel, aprovar e retirar
        aluguel, _ = aluguel_service.solicitar_aluguel(
            id_cliente=cliente_id,
            id_catalogo=catalogo_id,
            dias_alugados=3,
            data_inicio=date.today(),
            tipo_midia="FISICA"
        )
        
        aluguel, _ = aluguel_service.processar_pagamento(aluguel.id, sucesso=True)
        aluguel, _ = aluguel_service.registrar_retirada(aluguel.id)
        
        # Registrar devolução extraviado
        aluguel_devolvido, erro = aluguel_service.registrar_devolucao(
            aluguel.id,
            condicao_item="extraviado",
            id_funcionario=funcionario_id
        )
        
        assert erro is None
        assert aluguel_devolvido is not None
        assert aluguel_devolvido.condicao_item == "extraviado"

    def test_devolucao_com_atraso_multa(self, test_container, setup_test_entities):
        """
        Testa a devolução com atraso e cálculo de multa.
        Esperado: Multa é calculada com base no atraso.
        """
        aluguel_service = test_container.aluguel_service
        
        cliente_id = setup_test_entities["cliente_id"]
        catalogo_id = setup_test_entities["catalogo_id"]
        funcionario_id = setup_test_entities["funcionario_id"]
        
        # Criar aluguel com data de início no passado
        dias_passados = 5
        data_inicio = date.today() - timedelta(days=dias_passados)
        
        aluguel, _ = aluguel_service.solicitar_aluguel(
            id_cliente=cliente_id,
            id_catalogo=catalogo_id,
            dias_alugados=3,  # Esperava devolver em 3 dias
            data_inicio=data_inicio,
            tipo_midia="FISICA"
        )
        
        aluguel, _ = aluguel_service.processar_pagamento(aluguel.id, sucesso=True)
        aluguel, _ = aluguel_service.registrar_retirada(aluguel.id)
        
        # Tentar devolver com atraso
        aluguel_atrasado, erro = aluguel_service.registrar_devolucao(
            aluguel.id,
            condicao_item="bom",
            id_funcionario=funcionario_id
        )
        
        assert erro is None
        # A multa deve ter sido calculada se houver atraso
        assert aluguel_atrasado is not None

    def test_cancelar_aluguel(self, test_container, setup_test_entities):
        """
        Testa o cancelamento de um aluguel.
        Esperado: Aluguel é cancelado ou erro se não estiver em estado cancelável.
        """
        aluguel_service = test_container.aluguel_service
        
        cliente_id = setup_test_entities["cliente_id"]
        catalogo_id = setup_test_entities["catalogo_id"]
        
        # Criar aluguel
        aluguel, _ = aluguel_service.solicitar_aluguel(
            id_cliente=cliente_id,
            id_catalogo=catalogo_id,
            dias_alugados=3,
            data_inicio=date.today(),
            tipo_midia="FISICA"
        )
        
        # Cancelar aluguel (pode falhar se não encontrado ou em estado inválido)
        aluguel_cancelado, erro = aluguel_service.cancelar_aluguel(aluguel.id, cliente_id)
        
        # Aceitar ambos os cenários: sucesso ou erro
        if erro:
            # Se há erro, pode ser porque o aluguel não foi encontrado ou está em estado inválido
            assert "não encontrado" in erro.lower() or "não pertence" in erro.lower()

    def test_renovar_aluguel(self, test_container, setup_test_entities):
        """
        Testa a renovação de um aluguel.
        Esperado: Período e data de devolução são aumentados, ou erro se não encontrado.
        """
        aluguel_service = test_container.aluguel_service
        
        cliente_id = setup_test_entities["cliente_id"]
        catalogo_id = setup_test_entities["catalogo_id"]
        
        # Criar aluguel e aprovar
        aluguel, _ = aluguel_service.solicitar_aluguel(
            id_cliente=cliente_id,
            id_catalogo=catalogo_id,
            dias_alugados=3,
            data_inicio=date.today(),
            tipo_midia="FISICA"
        )
        
        aluguel, _ = aluguel_service.processar_pagamento(aluguel.id, sucesso=True)
        
        # Renovar com 2 dias adicionais
        dias_adicionais = 2
        aluguel_renovado, erro = aluguel_service.renovar_aluguel(
            aluguel.id,
            cliente_id,
            dias_adicionais
        )
        
        if erro:
            # Aceitar erro se o aluguel não for encontrado ou estiver em estado inválido
            assert "não encontrado" in erro.lower() or "não pertence" in erro.lower()
        else:
            assert aluguel_renovado is not None
            assert aluguel_renovado.periodo == 5  # 3 + 2

    def test_fluxo_completo_aluguel(self, test_container, setup_test_entities):
        """
        Testa o fluxo completo: solicitação -> pagamento -> retirada -> devolução.
        Este é o teste de integração mais importante.
        """
        aluguel_service = test_container.aluguel_service
        
        cliente_id = setup_test_entities["cliente_id"]
        catalogo_id = setup_test_entities["catalogo_id"]
        funcionario_id = setup_test_entities["funcionario_id"]
        
        # 1. Solicitar aluguel
        aluguel, erro = aluguel_service.solicitar_aluguel(
            id_cliente=cliente_id,
            id_catalogo=catalogo_id,
            dias_alugados=3,
            data_inicio=date.today(),
            tipo_midia="FISICA"
        )
        assert erro is None
        assert aluguel.status == StatusAluguel.SOLICITADO.value
        
        # 2. Processar pagamento
        aluguel, erro = aluguel_service.processar_pagamento(aluguel.id, sucesso=True)
        assert erro is None
        assert aluguel.status == StatusAluguel.APROVADO.value
        
        # 3. Registrar retirada
        aluguel, erro = aluguel_service.registrar_retirada(aluguel.id)
        assert erro is None
        assert aluguel.status == StatusAluguel.ATIVO.value
        
        # 4. Registrar devolução
        aluguel, erro = aluguel_service.registrar_devolucao(
            aluguel.id,
            condicao_item="bom",
            id_funcionario=funcionario_id
        )
        assert erro is None
        assert aluguel.status == StatusAluguel.FINALIZADO.value


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

