import pytest
from datetime import date, timedelta
from app.models.transacao.aluguel.aluguel import Aluguel
from app.models.enums import StatusAluguel

def test_fluxo_de_estado_feliz_do_aluguel():
    """Testa o 'caminho feliz' do fluxo de estados de um aluguel."""
    # 1. Inicia como SOLICITADO
    aluguel = Aluguel(status=StatusAluguel.SOLICITADO.value)
    assert aluguel.status == StatusAluguel.SOLICITADO.value

    # 2. Processa pagamento com sucesso -> APROVADO
    aluguel.processar_pagamento(sucesso=True)
    assert aluguel.status == StatusAluguel.APROVADO.value

    # 3. Registra retirada -> ATIVO
    aluguel.registrar_retirada()
    assert aluguel.status == StatusAluguel.ATIVO.value
    
    # 4. Finaliza o aluguel -> FINALIZADO
    aluguel.finalizar_aluguel()
    assert aluguel.status == StatusAluguel.FINALIZADO.value

def test_fluxo_de_cancelamento_pagamento_recusado():
    """Testa o cancelamento quando o pagamento é recusado após falha."""
    aluguel = Aluguel(status=StatusAluguel.SOLICITADO.value)

    aluguel.processar_pagamento(sucesso=False)
    assert aluguel.status == StatusAluguel.PROCESSANDO_PAGAMENTO.value

    aluguel.pagamento_recusado()
    assert aluguel.status == StatusAluguel.CANCELADO.value


def test_fluxo_pagamento_falha_permite_retentativa():
    """Falha no pagamento mantém o aluguel em processamento para nova tentativa."""
    aluguel = Aluguel(status=StatusAluguel.SOLICITADO.value)

    aluguel.processar_pagamento(sucesso=False)
    assert aluguel.status == StatusAluguel.PROCESSANDO_PAGAMENTO.value

    aluguel.processar_pagamento(sucesso=True)
    assert aluguel.status == StatusAluguel.APROVADO.value


def test_fluxo_atrasado_processar_pagamento():
    """Aluguel atrasado pode processar pagamento da multa e voltar ao ativo."""
    aluguel = Aluguel(status=StatusAluguel.ATRASADO.value)

    aluguel.processar_pagamento(sucesso=True)
    assert aluguel.status == StatusAluguel.ATIVO.value


def test_verificar_atraso_transiciona_para_atrasado():
    aluguel = Aluguel(
        status=StatusAluguel.ATIVO.value,
        data_prevista_devolucao=date.today() - timedelta(days=1),
    )

    aluguel.verificar_atraso()
    assert aluguel.status == StatusAluguel.ATRASADO.value

def test_fluxo_de_cancelamento_pelo_cliente():
    """Testa o cancelamento pelo cliente antes do início."""
    aluguel = Aluguel(
        status=StatusAluguel.SOLICITADO.value,
        data_inicio=date.today() + timedelta(days=2) # Data futura
    )
    
    aluguel.cancelar_aluguel()
    assert aluguel.status == StatusAluguel.CANCELADO.value

def test_transicoes_de_estado_invalidas():
    """Testa se transições inválidas levantam ValueError."""
    
    # Não pode registrar retirada de um aluguel solicitado
    aluguel_solicitado = Aluguel(status=StatusAluguel.SOLICITADO.value)
    with pytest.raises(ValueError, match="Transição de estado inválida"):
        aluguel_solicitado.registrar_retirada()

    # Não pode cancelar um aluguel ativo
    aluguel_ativo = Aluguel(status=StatusAluguel.ATIVO.value)
    with pytest.raises(ValueError, match="Não é possível cancelar um aluguel ativo"):
        aluguel_ativo.cancelar_aluguel()
        
    # Não pode renovar um aluguel atrasado
    aluguel_atrasado = Aluguel(status=StatusAluguel.ATRASADO.value)
    with pytest.raises(ValueError, match="Não é possível renovar um aluguel atrasado"):
        aluguel_atrasado.renovar_aluguel(dias_adicionais=5)

    # Não pode fazer nada em um aluguel finalizado
    aluguel_finalizado = Aluguel(status=StatusAluguel.FINALIZADO.value)
    with pytest.raises(ValueError, match="Transição de estado inválida"):
        aluguel_finalizado.registrar_retirada()
