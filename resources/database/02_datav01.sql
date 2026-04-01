-- Inserir dados na tabela 'usuario'
-- As senhas devem ser criptografadas na aplicação real, aqui usamos texto plano para demonstração.
INSERT INTO usuario (nome, cpf, email, senha, data_nascimento) VALUES
('João da Silva', '111.111.111-11', 'joao.silva@email.com', 'senha123', '1990-05-15'),
('Maria Oliveira', '222.222.222-22', 'maria.oliveira@email.com', 'senha456', '1988-11-20'),
('Carlos Pereira', '333.333.333-33', 'carlos.pereira@email.com', 'senha789', '1995-02-10');

-- Inserir dados na tabela 'cliente' (associado a 'usuario')
-- João da Silva (id=1) e Maria Oliveira (id=2) são clientes
INSERT INTO cliente (id_usuario, dados_pagamento) VALUES
(1, 'Cartão de Crédito **** 1234'),
(2, 'PayPal');

-- Inserir dados na tabela 'funcionario' (associado a 'usuario')
-- Carlos Pereira (id=3) é um funcionário
INSERT INTO funcionario (id_usuario, matricula, cargo) VALUES
(3, 'FUNC-001', 'Gerente de Loja');

-- Inserir dados na tabela 'jogo'
INSERT INTO jogo (titulo, descricao, plataforma, genero, classificacao, valor_venda, valor_diaria_aluguel) VALUES
('Super Mario World', 'Aventura clássica no Super Nintendo.', 'Super Nintendo', 'Plataforma', 'Livre', 150.00, 5.00),
('The Legend of Zelda: Ocarina of Time', 'RPG de ação épico para Nintendo 64.', 'Nintendo 64', 'Aventura/RPG', 'Livre', 200.00, 7.50),
('Street Fighter II', 'Jogo de luta icônico.', 'Arcade/Super Nintendo', 'Luta', '12 anos', 120.00, 4.00);

-- Inserir dados na tabela 'midia_fisica' (associado a 'jogo')
-- Temos cópias físicas de todos os jogos
INSERT INTO midia_fisica (id_jogo, codigo_barras, estado_conservacao, quantidade) VALUES
(1, '7890123456789', 'Bom', 5),
(2, '7890123456790', 'Excelente', 3),
(3, '7890123456791', 'Razoável', 10);

-- Exemplo de uma transação de aluguel para o cliente João da Silva
INSERT INTO transacao (valor_total, id_cliente, id_funcionario) VALUES (12.50, 1, 3);
INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status) VALUES (1, 5, CURRENT_DATE + 5, 'Ativo');
INSERT INTO item_transacao (id_transacao, id_jogo, quantidade, valor_unitario) VALUES (1, 1, 1, 5.00), (1, 3, 1, 7.50);
