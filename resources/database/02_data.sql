-- =========================================
-- USUARIOS
-- =========================================

INSERT INTO usuario (nome, cpf, email, senha, data_nascimento) VALUES
('João Silva', '111.111.111-11', 'joao@retrohub.com', 'hash123', '1995-05-10'),
('Maria Souza', '222.222.222-22', 'maria@retrohub.com', 'hash123', '1992-03-22'),
('Pedro Gamer', '333.333.333-33', 'pedro@retrohub.com', 'hash123', '2000-07-15'),
('Ana Funcionaria', '444.444.444-44', 'ana@retrohub.com', 'hash123', '1988-11-02');

-- =========================================
-- CLIENTES / FUNCIONARIO
-- =========================================

INSERT INTO cliente (id_usuario, dados_pagamento) VALUES
(1, 'Cartão Visa'),
(2, 'Pix'),
(3, 'Cartão Master');

INSERT INTO funcionario (id_usuario, matricula, cargo) VALUES
(4, 'FUNC001', 'Atendente');

-- =========================================
-- JOGOS
-- =========================================

INSERT INTO jogo (titulo, descricao, plataforma, genero, classificacao, valor_venda, valor_diaria_aluguel) VALUES
('Super Mario World', 'Clássico do SNES', 'SNES', 'Plataforma', 'Livre', 150.00, 10.00),
('The Legend of Zelda', 'Aventura épica', 'NES', 'Aventura', '10+', 200.00, 12.00),
('Street Fighter II', 'Luta arcade clássica', 'Arcade', 'Luta', '12+', 120.00, 8.00),
('Sonic the Hedgehog', 'Velocidade e nostalgia', 'Mega Drive', 'Plataforma', 'Livre', 130.00, 9.00);

-- =========================================
-- MIDIAS
-- =========================================

-- Física
INSERT INTO midia_fisica (id_jogo, codigo_barras, estado_conservacao, quantidade) VALUES
(1, 'BARCODE001', 'BOM', 3),
(2, 'BARCODE002', 'EXCELENTE', 2),
(4, 'BARCODE003', 'REGULAR', 1);

-- Digital
INSERT INTO midia_digital (id_jogo, chave_ativacao, data_expiracao) VALUES
(3, 'KEY-STREET-001', '2030-01-01');

-- =========================================
-- RESERVA
-- =========================================

INSERT INTO reserva (id_cliente, id_jogo, status) VALUES
(1, 2, 'ATIVA');

-- =========================================
-- TRANSACOES
-- =========================================

-- Venda concluída
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario) VALUES
(150.00, 'CONCLUIDA', 1, 4);

-- Aluguel ativo
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario) VALUES
(16.00, 'CONCLUIDA', 2, 4);

-- Aluguel atrasado
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario) VALUES
(24.00, 'CONCLUIDA', 3, 4);

-- Reserva convertida em aluguel
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario) VALUES
(12.00, 'CONCLUIDA', 1, 4);

-- =========================================
-- VENDA
-- =========================================

INSERT INTO venda (id_transacao, status) VALUES
(1, 'FINALIZADA');

-- =========================================
-- ALUGUEIS
-- =========================================

-- aluguel ativo
INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status) VALUES
(2, 2, CURRENT_DATE + INTERVAL '2 days', 'ATIVO');

-- aluguel atrasado
INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status) VALUES
(3, 3, CURRENT_DATE - INTERVAL '2 days', 'ATRASADO');

-- aluguel vindo de reserva
INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status, id_reserva) VALUES
(4, 1, CURRENT_DATE + INTERVAL '1 day', 'ATIVO', 1);

-- =========================================
-- ITENS
-- =========================================

INSERT INTO item_transacao (id_transacao, id_jogo, quantidade, valor_unitario) VALUES
(1, 1, 1, 150.00),
(2, 3, 1, 8.00),
(3, 4, 1, 8.00),
(4, 2, 1, 12.00);

-- =========================================
-- COMPROVANTES
-- =========================================

INSERT INTO comprovante (id_transacao, tipo, codigo_rastreio) VALUES
(1, 'VENDA', 'TRACK001'),
(2, 'ALUGUEL', 'TRACK002'),
(3, 'ALUGUEL', 'TRACK003'),
(4, 'ALUGUEL', 'TRACK004');

-- =========================================
-- MULTA
-- =========================================

INSERT INTO multa (id_aluguel, dias_atraso, valor, status) VALUES
(3, 2, 10.00, 'PENDENTE');

-- =========================================
-- AVALIACOES
-- =========================================

INSERT INTO avaliacao (id_transacao, nota, comentario) VALUES
(1, 5, 'Clássico incrível!'),
(2, 4, 'Muito divertido'),
(3, 3, 'Bom, mas atrasou a devolução 😅');