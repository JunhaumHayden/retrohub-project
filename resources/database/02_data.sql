-- =========================================
-- USUARIOS (Personagens de Games - Easter Eggs)
-- =========================================
-- Solid Snake (Metal Gear) - Administrador
-- Major Zero (Metal Gear) - Atendente/Subordinado do Snake
-- Mike Haggar (Final Fight) - Cliente que luta nas ruas
-- Lara Croft (Tomb Raider) - Cliente aventureira
-- + Novos personagens adicionados

INSERT INTO usuario (nome, cpf, email, senha, data_nascimento) VALUES
-- Administradores (Os que mandam no sistema)
('Solid Snake', '111.111.111-11', 'snake@retrohub.com', 'hash123', '1972-06-12'),
('Master Chief', '222.222.222-22', 'chief@retrohub.com', 'hash123', '2511-03-07'),
('Kratos', '333.333.333-33', 'kratos@retrohub.com', 'hash123', '2005-11-22'),

-- Gerentes/Atendentes (Subordinados)
('Major Zero', '444.444.444-44', 'zero@retrohub.com', 'hash123', '1950-09-13'),
('The Boss', '555.555.555-55', 'boss@retrohub.com', 'hash123', '1927-09-10'),
('Cortana', '666.666.666-66', 'cortana@retrohub.com', 'hash123', '2549-11-07'),

-- Atendentes operacionais
('Mike Haggar', '777.777.777-77', 'haggar@retrohub.com', 'hash123', '1962-04-18'),
('Tifa Lockhart', '888.888.888-88', 'tifa@retrohub.com', 'hash123', '1987-05-03'),
('Luigi', '999.999.999-99', 'luigi@retrohub.com', 'hash123', '1983-07-14'),
('Clank', '123.456.789-00', 'clank@retrohub.com', 'hash123', '2002-11-04'),

-- Clientes Premium
('Lara Croft', '101.202.303-44', 'lara@retrohub.com', 'hash123', '1968-02-14'),
('Nathan Drake', '202.303.404-55', 'drake@retrohub.com', 'hash123', '1976-10-19'),
('Jill Valentine', '303.404.505-66', 'jill@retrohub.com', 'hash123', '1974-11-30'),
('Cloud Strife', '404.505.606-77', 'cloud@retrohub.com', 'hash123', '1986-08-11'),
('Sonic', '505.606.707-88', 'sonic@retrohub.com', 'hash123', '1991-06-23'),
('Mario', '606.707.808-99', 'mario@retrohub.com', 'hash123', '1981-07-09'),
('Samus Aran', '707.808.909-00', 'samus@retrohub.com', 'hash123', '1986-08-06'),
('Geralt of Rivia', '808.909.010-11', 'geralt@retrohub.com', 'hash123', '1990-05-18'),
('Arthur Morgan', '909.010.121-22', 'arthur@retrohub.com', 'hash123', '1899-05-05'),
('Ellie Williams', '010.121.232-33', 'ellie@retrohub.com', 'hash123', '2013-06-14'),

-- Clientes casuais (Personagens secundários)
('Ezio Auditore', '111.212.333-44', 'ezio@retrohub.com', 'hash123', '1459-06-24'),
('Crash Bandicoot', '212.323.444-55', 'crash@retrohub.com', 'hash123', '1996-09-09'),
('Spyro', '313.434.555-66', 'spyro@retrohub.com', 'hash123', '1998-09-10'),
('Doomguy', '414.545.666-77', 'doom@retrohub.com', 'hash123', '1993-12-10'),
('Pyramid Head', '515.656.777-88', 'pyramid@retrohub.com', 'hash123', '2001-09-24'),

-- NOVOS PERSONAGENS (Easter eggs especiais)
('Liu Kang', '616.767.888-99', 'liukang@retrohub.com', 'hash123', '1992-10-08'),     -- Mortal Kombat (26)
('Cranky Kong', '717.878.999-00', 'cranky@retrohub.com', 'hash123', '1981-07-09'),  -- Donkey Kong (27)
('Trevor Philips', '818.989.000-11', 'trevor@retrohub.com', 'hash123', '1965-01-01'), -- GTA V (28)
('Franklin Clinton', '919.090.111-22', 'franklin@retrohub.com', 'hash123', '1988-06-01'), -- GTA V (29)
('Ryu', '020.131.242-33', 'ryu@retrohub.com', 'hash123', '1987-08-30'),            -- Street Fighter (30)
('Ken Masters', '121.242.353-44', 'ken@retrohub.com', 'hash123', '1987-08-30'),     -- Street Fighter (31)
('Chun-Li', '222.353.464-55', 'chunli@retrohub.com', 'hash123', '1991-03-01');      -- Street Fighter (32)


-- =========================================
-- FUNCIONARIOS (Easter eggs de hierarquia)
-- =========================================
-- Solid Snake é o "Boss" (Administrador)
-- Major Zero é subordinado do Snake (mas na lore é o chefe dele - ironia!)
-- Mike Haggar é prefeito de Metro City mas trabalha como atendente
-- Tifa é atendente (barista na lore)
-- Luigi é o "plano B" (estoque)
-- Clank é robô assistente (logística)

INSERT INTO funcionario (id_usuario, matricula, cargo, setor, data_admissao) VALUES
-- Administradores (Os que mandam)
(1, 'FOX001', 'Administrador', 'TI', '1998-09-03'),        -- Solid Snake (FOXHOUND)
(2, 'UNSC001', 'Administrador', 'TI', '2552-09-27'),       -- Master Chief (UNSC)
(3, 'SPARTAN001', 'Administrador', 'Segurança', '2018-04-20'), -- Kratos (Spartan)

-- Gerentes (Sub-comandantes)
(4, 'FOX002', 'Gerente', 'Operações', '1964-10-12'),       -- Major Zero (Fundador FOXHOUND)
(5, 'FOX003', 'Gerente', 'RH', '1942-06-13'),              -- The Boss (Mentora)
(6, 'UNSC002', 'Gerente', 'Suporte', '2552-09-27'),        -- Cortana (IA Assistente)

-- Atendentes operacionais
(7, 'METRO001', 'Atendente', 'Vendas', '1989-12-11'),      -- Mike Haggar (Mayor of Metro City)
(8, 'AVALANCHE001', 'Atendente', 'Atendimento', '1997-01-31'), -- Tifa (Barista)
(9, 'MUSHROOM001', 'Atendente', 'Estoque', '1983-09-13'),  -- Luigi (Backup)
(10, 'RATCHET001', 'Atendente', 'Logística', '2002-11-04'); -- Clank (Assistente) CORRIGIDO PONTO E VIRGULA AQUI

-- NOVOS FUNCIONÁRIOS (Instrutores de luta - Street Fighter)
--(30, 'SF001', 'Instrutor', 'Treinamento', '1991-03-01'),   -- Ryu (Instrutor de luta)
--(31, 'SF002', 'Terapeuta', 'Treinamento', '1991-03-01'),   -- Ken Masters
--(32, 'SF003', 'Instrutora', 'Treinamento', '1991-03-01');  -- Chun-Li (Instrutora de luta)


-- =========================================
-- CLIENTES (Personagens que consomem jogos)
-- =========================================
-- Cada cliente tem um easter egg: muitos alugam seus próprios jogos (meta)

INSERT INTO cliente (id_usuario, dados_pagamento, data_cadastro, tipo_cliente) VALUES
-- Funcionários que também são clientes (para as transações abaixo funcionarem)
(1, 'Cartão FOXHOUND', '1998-09-03', 'premium'),                   -- Solid Snake
(2, 'Créditos UNSC', '2552-09-27', 'regular'),                     -- Master Chief
(3, 'Ouro de Esparta', '2018-04-20', 'premium'),                   -- Kratos
(8, 'Gil (Final Fantasy)', '1997-01-31', 'regular'),               -- Tifa
(9, 'Moedas do Reino Cogumelo', '1983-09-13', 'regular'),          -- Luigi

-- Clientes Premium (gastam muito)
(11, 'Cartão Black - Visa Infinite', '1996-10-25', 'premium'),     -- Lara Croft
(12, 'Cartão Platinum - Mastercard', '2007-11-19', 'premium'),    -- Nathan Drake
(13, 'Pix - Chave aleatória', '1996-03-22', 'regular'),           -- Jill Valentine
(14, 'Bitcoin Wallet', '1997-01-31', 'premium'),                  -- Cloud Strife
(15, 'Ouriço Cash', '1991-06-23', 'regular'),                     -- Sonic
(16, 'Estrelas do Mario', '1981-07-09', 'premium'),               -- Mario
(17, 'Cartão Metroid - Visa', '1986-08-06', 'regular'),           -- Samus Aran
(18, 'Moedas de Ouro', '2007-10-26', 'premium'),                  -- Geralt
(19, 'Dólar do Faroeste', '2018-10-26', 'regular'),               -- Arthur Morgan
(20, 'Cartão Ellie - Mastercard', '2013-06-14', 'premium'),       -- Ellie Williams

-- Clientes casuais
(21, 'Carteira dos Assassinos', '2009-11-15', 'regular'),         -- Ezio Auditore
(22, 'Fruta Wumpa', '1996-09-09', 'regular'),                     -- Crash Bandicoot
(23, 'Joias de Dragão', '1998-09-10', 'regular'),                 -- Spyro
(24, 'BFG Division - Dinheiro', '1993-12-10', 'premium'),         -- Doomguy
(25, 'Almas Perdidas', '2001-09-24', 'regular'),                  -- Pyramid Head

-- NOVOS CLIENTES
(26, 'Fireball Fists - Dragon Coin', '1992-10-08', 'regular'),    -- Liu Kang (Mortal Kombat)
(27, 'Barris de Ouro', '1981-07-09', 'regular'),                  -- Cranky Kong (Donkey Kong)
(28, 'Dinheiro Sujo - Off Shore', '2013-09-17', 'regular'),       -- Trevor Philips (GTA V)
(29, 'Garagem de Carros', '2013-09-17', 'premium'),               -- Franklin Clinton (GTA V)
(30, 'Dojo - Hadouken Coins', '1987-08-30', 'regular'),           -- Ryu (apenas cliente agora)
(31, 'Dojo - Shoryuken Gold', '1987-08-30', 'regular'),           -- Ken Masters (apenas cliente agora)
(32, 'Spinning Bird Kick - Visa', '1991-03-01', 'premium');       -- Chun-Li (apenas cliente agora)


-- =========================================
-- JOGOS (Catálogo com easter eggs)
-- =========================================
-- Adicionados: Need for Speed, Mortal Kombat, Street Fighter, Mario Kart

INSERT INTO jogo (titulo, descricao, plataforma, genero, classificacao, valor_venda, valor_diaria_aluguel) VALUES
-- Jogos dos Administradores
('Metal Gear Solid', 'Infiltração tática com Solid Snake', 'PS1', 'Ação', '16+', 199.90, 9.90),
('Halo: Combat Evolved', 'Master Chief salva a humanidade', 'Xbox', 'FPS', '16+', 149.90, 7.90),
('God of War', 'Kratos enfrenta os deuses nórdicos', 'PS5', 'Ação', '18+', NULL, 12.90),

-- Jogos dos Gerentes
('Metal Gear Solid 3: Snake Eater', 'A origem de Naked Snake e The Boss', 'PS2', 'Stealth', '16+', 89.90, 5.90),
('Halo 4', 'Cortana e Chief em nova aventura', 'Xbox 360', 'FPS', '16+', NULL, 6.90),

-- Jogos dos Atendentes
('Final Fight', 'Mike Haggar luta para salvar sua filha', 'SNES', 'Beat em up', '12+', 49.90, NULL),
('Final Fantasy VII', 'Tifa e Cloud no RPG clássico', 'PS1', 'RPG', '12+', 199.90, 8.90),
('Super Mario Bros', 'Luigi e Mario salvam a princesa', 'NES', 'Plataforma', 'Livre', NULL, 4.90),
('Ratchet & Clank', 'Clank ajuda Ratchet em missões', 'PS2', 'Ação', '10+', 79.90, NULL),

-- Jogos dos Clientes
('Tomb Raider', 'Lara Croft explora tumbas antigas', 'PS4', 'Aventura', '16+', 129.90, 6.90),
('Uncharted 4: A Thief''s End', 'Nathan Drake em busca de tesouros', 'PS4', 'Aventura', '16+', NULL, 7.90),
('Resident Evil 3', 'Jill Valentine enfrenta Nemesis', 'PS1', 'Survival Horror', '18+', 89.90, 5.90),
('Final Fantasy VII Remake', 'Cloud Strife em alta definição', 'PS5', 'RPG', '12+', 249.90, NULL),
('Sonic Frontiers', 'Sonic em mundo aberto', 'Switch', 'Aventura', 'Livre', NULL, 8.90),
('Super Mario Odyssey', 'Mario viaja pelo mundo', 'Switch', 'Plataforma', 'Livre', 299.90, 9.90),
('Metroid Dread', 'Samus Aran em missão mortal', 'Switch', 'Ação', '12+', NULL, 7.90),
('The Witcher 3: Wild Hunt', 'Geralt caça monstros', 'PS4', 'RPG', '18+', 99.90, 5.90),
('Red Dead Redemption 2', 'Arthur Morgan no faroeste', 'PS4', 'Ação', '18+', 149.90, NULL),
('The Last of Us Part II', 'Ellie em busca de vingança', 'PS4', 'Aventura', '18+', 199.90, 8.90),

-- Jogos de clientes casuais
('Assassin''s Creed II', 'Ezio Auditore na Renascença Italiana', 'PS3', 'Ação', '16+', 79.90, 4.90),
('Crash Bandicoot 4: It''s About Time', 'Crash em nova aventura', 'PS4', 'Plataforma', 'Livre', 149.90, 6.90),
('Spyro Reignited Trilogy', 'Spyro em 3 jogos remasterizados', 'PS4', 'Aventura', 'Livre', 129.90, 5.90),
('DOOM Eternal', 'Doomguy contra demônios', 'PS4', 'FPS', '18+', 99.90, 6.90),
('Silent Hill 2', 'Pyramid Head e o terror psicológico', 'PS2', 'Survival Horror', '18+', 299.90, 12.90),

-- Clássicos extras
('Street Fighter II', 'Luta arcade clássica', 'Arcade', 'Luta', '12+', 120.00, 8.00),
('The Legend of Zelda: Ocarina of Time', 'Aventura épica de Link', 'N64', 'Aventura', '10+', 250.00, 10.00),
('Pokémon Red', 'Colete todos os 151 pokémon', 'Game Boy', 'RPG', 'Livre', 300.00, 8.00),
('Castlevania: Symphony of the Night', 'Alucard e o castelo de Drácula', 'PS1', 'Ação', '14+', 180.00, 7.00),
('Shadow of the Colossus', '16 colossos para derrubar', 'PS2', 'Aventura', '12+', 120.00, 6.00),

-- NOVOS JOGOS (Easter eggs)
('Mortal Kombat 11', 'Liu Kang e o torneio mortal', 'PS4', 'Luta', '18+', 99.90, 7.90),
('Mario Kart 8 Deluxe', 'Corrida maluca com os personagens da Nintendo', 'Switch', 'Corrida', 'Livre', 299.90, 9.90),
('Need for Speed: Heat', 'Corrida de rua e perseguição policial', 'PS4', 'Corrida', '14+', 129.90, 6.90),
('Grand Theft Auto V', 'Trevor, Franklin e Michael em Los Santos', 'PS4', 'Ação', '18+', 99.90, 7.90),
('Street Fighter V', 'Ryu, Ken e Chun-Li no torneio definitivo', 'PS4', 'Luta', '12+', 79.90, 5.90);


-- =========================================
-- MIDIAS FISICAS (Atualizado com novos jogos)
-- =========================================

INSERT INTO midia_fisica (id_jogo, codigo_barras, estado_conservacao, quantidade) VALUES
-- Clássicos
(1, 'MGS001-BR', 'EXCELENTE', 5),
(2, 'HALO001-BR', 'EXCELENTE', 8),
(4, 'MGS302-BR', 'BOM', 3),
(6, 'FFIGHT01-BR', 'REGULAR', 10),
(7, 'FFVII01-BR', 'EXCELENTE', 7),
(10, 'TOMB01-BR', 'BOM', 6),
(12, 'RE301-BR', 'REGULAR', 3),
(16, 'METROID01-BR', 'EXCELENTE', 4),
(17, 'WITCHER01-BR', 'BOM', 9),
(19, 'TLOU01-BR', 'EXCELENTE', 5),

-- Clientes casuais
(20, 'AC02-BR', 'BOM', 4),
(21, 'CRASH04-BR', 'EXCELENTE', 6),
(22, 'SPYRO-BR', 'BOM', 5),
(23, 'DOOM-BR', 'EXCELENTE', 7),
(24, 'SH02-BR', 'REGULAR', 2),

-- Clássicos extras
(25, 'SF02-BR', 'EXCELENTE', 15),
(26, 'ZELDA64-BR', 'BOM', 4),
(27, 'POKEMONRED-BR', 'REGULAR', 3),
(28, 'CASTLE-BR', 'EXCELENTE', 5),
(29, 'SHADOW-BR', 'BOM', 6),

-- NOVOS JOGOS
(30, 'MK11-BR', 'EXCELENTE', 10),      -- Mortal Kombat 11
(31, 'MARIOKART-BR', 'EXCELENTE', 12), -- Mario Kart 8
(32, 'NFS-BR', 'BOM', 8),              -- Need for Speed
(33, 'GTA5-BR', 'EXCELENTE', 15),      -- GTA V
(34, 'SF5-BR', 'EXCELENTE', 10);       -- Street Fighter V


-- =========================================
-- MIDIAS DIGITAIS
-- =========================================

INSERT INTO midia_digital (id_jogo, chave_ativacao, data_expiracao) VALUES
(3, 'GOW-KRATOS-2026-001', '2030-12-31'),
(5, 'HALO4-CORTANA-002', '2030-12-31'),
(8, 'MARIO-LUIGI-003', '2030-12-31'),
(11, 'UNCHARTED-DRAKE-004', '2030-12-31'),
(14, 'SONIC-FRONTIERS-005', '2030-12-31'),
(15, 'MARIO-ODYSSEY-006', '2030-12-31'),
(18, 'RDR2-ARTHUR-007', '2030-12-31'),
(33, 'GTA5-TREVOR-008', '2030-12-31'),     -- GTA V digital
(34, 'SF5-RYU-009', '2030-12-31');          -- Street Fighter V digital


-- =========================================
-- RESERVAS
-- =========================================

INSERT INTO reserva (id_cliente, id_jogo, status, data_reserva, data_expiracao) VALUES
(11, 10, 'ATIVA', CURRENT_DATE, CURRENT_DATE + INTERVAL '2 days'),  -- Lara Croft (11) -> Tomb Raider
(14, 13, 'ATIVA', CURRENT_DATE, CURRENT_DATE + INTERVAL '2 days'),  -- Cloud (14) -> FFVII Remake
(18, 17, 'ATIVA', CURRENT_DATE, CURRENT_DATE + INTERVAL '2 days'),  -- Geralt (18) -> Witcher 3
(12, 11, 'CANCELADA', CURRENT_DATE - INTERVAL '5 days', CURRENT_DATE - INTERVAL '3 days'), -- Nathan Drake (12)
(13, 12, 'ATIVA', CURRENT_DATE, CURRENT_DATE + INTERVAL '1 day'),   -- Jill Valentine (13)
(15, 14, 'ATIVA', CURRENT_DATE, CURRENT_DATE + INTERVAL '2 days'),  -- Sonic (15)
-- NOVAS RESERVAS
(30, 34, 'ATIVA', CURRENT_DATE, CURRENT_DATE + INTERVAL '3 days');  -- Ryu reservou Street Fighter V


-- =========================================
-- TRANSACOES (Com novos personagens)
-- =========================================

-- Transação 1: Venda do Super Mario World para Mario
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(150.00, 'CONCLUIDA', 16, 1, CURRENT_DATE - INTERVAL '15 days');

-- Transação 2: Aluguel ativo - Sonic alugando Sonic Frontiers
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(17.80, 'CONCLUIDA', 15, 7, CURRENT_DATE - INTERVAL '5 days');

-- Transação 3: Aluguel atrasado - Solid Snake alugando Metal Gear Solid
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(29.70, 'CONCLUIDA', 1, 4, CURRENT_DATE - INTERVAL '10 days');

-- Transação 4: Venda - Kratos comprando God of War
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(299.90, 'CONCLUIDA', 3, 2, CURRENT_DATE - INTERVAL '20 days');

-- Transação 5: Aluguel - Tifa alugando Final Fantasy VII Remake
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(26.70, 'CONCLUIDA', 8, 8, CURRENT_DATE - INTERVAL '3 days');

-- Transação 6: Aluguel - Luigi alugando Super Mario Odyssey
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(19.80, 'CONCLUIDA', 9, 9, CURRENT_DATE - INTERVAL '2 days');

-- Transação 7: Venda - Doomguy comprando DOOM Eternal
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(99.90, 'CONCLUIDA', 24, 1, CURRENT_DATE - INTERVAL '8 days');

-- Transação 8: Aluguel - Master Chief alugando Halo 4
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(13.80, 'CONCLUIDA', 2, 2, CURRENT_DATE - INTERVAL '1 day');

-- Transação 9: Aluguel vindo de reserva - Lara Croft
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(6.90, 'CONCLUIDA', 11, 7, CURRENT_DATE);

-- Transação 10: Aluguel - Pyramid Head alugando Silent Hill 2
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(25.80, 'CONCLUIDA', 25, 8, CURRENT_DATE - INTERVAL '4 days');

-- Transação 11: Venda - Ezio comprando Assassin's Creed II
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(79.90, 'CONCLUIDA', 21, 9, CURRENT_DATE - INTERVAL '12 days');

-- Transação 12: Aluguel - Crash alugando Crash Bandicoot 4
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(13.80, 'CONCLUIDA', 22, 10, CURRENT_DATE - INTERVAL '6 days');

-- Transação 13: Aluguel - Samus alugando Metroid Dread
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(7.90, 'CONCLUIDA', 17, 7, CURRENT_DATE - INTERVAL '1 day');

-- NOVAS TRANSAÇÕES (Easter eggs especiais)

-- Transação 14: Liu Kang alugando Final Fight (easter egg: lutador reclamando de violência)
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(8.00, 'CONCLUIDA', 26, 7, CURRENT_DATE - INTERVAL '10 days');  -- Liu Kang alugou Final Fight

-- Transação 15: Cranky Kong alugando Mario Kart (easter egg: "macacada")
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(9.90, 'CONCLUIDA', 27, 9, CURRENT_DATE - INTERVAL '7 days');    -- Cranky Kong alugou Mario Kart

-- Transação 16: Trevor Philips alugando GTA V (easter egg: multa alta por atraso)
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(15.80, 'CONCLUIDA', 28, 1, CURRENT_DATE - INTERVAL '30 days');  -- Trevor alugou GTA V (30 dias atrás)

-- Transação 17: Franklin Clinton alugando Need for Speed por 600 dias (easter gigante!)
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(4140.00, 'CONCLUIDA', 29, 10, CURRENT_DATE - INTERVAL '600 days');  -- Franklin alugou NFS por 600 DIAS!

-- Transação 18: Ryu alugando Street Fighter V (agora o funcionario foi mudado para 7 - Mike Haggar)
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(15.90, 'CONCLUIDA', 30, 7, CURRENT_DATE - INTERVAL '3 days');

-- Transação 19: Ken alugando Street Fighter V (agora o funcionario foi mudado para 8 - Tifa)
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(15.90, 'CONCLUIDA', 31, 8, CURRENT_DATE - INTERVAL '2 days');

-- Transação 20: Chun-Li comprando Street Fighter V (agora o funcionario foi mudado para 9 - Luigi)
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(79.90, 'CONCLUIDA', 32, 9, CURRENT_DATE - INTERVAL '5 days');


-- =========================================
-- VENDAS
-- =========================================

INSERT INTO venda (id_transacao, status, data_confirmacao) VALUES
(1, 'FINALIZADA', CURRENT_DATE - INTERVAL '15 days'),
(4, 'FINALIZADA', CURRENT_DATE - INTERVAL '20 days'),
(7, 'FINALIZADA', CURRENT_DATE - INTERVAL '8 days'),
(11, 'FINALIZADA', CURRENT_DATE - INTERVAL '12 days'),
(20, 'FINALIZADA', CURRENT_DATE - INTERVAL '5 days');  -- Chun-Li comprou SFV


-- =========================================
-- ALUGUEIS (Atualizado com novos personagens)
-- =========================================

-- Aluguel 1: Sonic - Sonic Frontiers
INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status, data_inicio, data_prevista_devolucao) VALUES
(2, 2, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '5 days', CURRENT_DATE - INTERVAL '3 days');

-- Aluguel 2: Solid Snake - MGS
INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status, data_inicio, data_prevista_devolucao) VALUES
(3, 3, NULL, 'ATRASADO', CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE - INTERVAL '7 days');

-- Aluguel 3: Tifa - FFVII Remake
INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status, data_inicio, data_prevista_devolucao) VALUES
(5, 3, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '3 days', CURRENT_DATE + INTERVAL '1 day');

-- Aluguel 4: Luigi - Mario Odyssey
INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status, data_inicio, data_prevista_devolucao) VALUES
(6, 2, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '2 days', CURRENT_DATE);

-- Aluguel 5: Master Chief - Halo 4
INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status, data_inicio, data_prevista_devolucao) VALUES
(8, 2, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '1 day', CURRENT_DATE);

-- Aluguel 6: Lara Croft - Tomb Raider (vindo de reserva)
INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status, data_inicio, data_prevista_devolucao, id_reserva) VALUES
(9, 1, NULL, 'ATIVO', CURRENT_DATE, CURRENT_DATE + INTERVAL '1 day', 1);

-- Aluguel 7: Pyramid Head - Silent Hill 2
INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status, data_inicio, data_prevista_devolucao) VALUES
(10, 3, NULL, 'ATRASADO', CURRENT_DATE - INTERVAL '4 days', CURRENT_DATE - INTERVAL '1 day');

-- Aluguel 8: Crash - Crash Bandicoot 4
INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status, data_inicio, data_prevista_devolucao) VALUES
(12, 2, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '6 days', CURRENT_DATE - INTERVAL '4 days');

-- Aluguel 9: Samus - Metroid Dread
INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status, data_inicio, data_prevista_devolucao) VALUES
(13, 1, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '1 day', CURRENT_DATE);

-- NOVOS ALUGUEIS

-- Aluguel 10: Liu Kang - Final Fight (easter egg: reclamou da violência)
INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status, data_inicio, data_prevista_devolucao) VALUES
(14, 1, CURRENT_DATE - INTERVAL '9 days', 'FINALIZADO', CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE - INTERVAL '9 days');

-- Aluguel 11: Cranky Kong - Mario Kart
INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status, data_inicio, data_prevista_devolucao) VALUES
(15, 1, CURRENT_DATE - INTERVAL '6 days', 'FINALIZADO', CURRENT_DATE - INTERVAL '7 days', CURRENT_DATE - INTERVAL '6 days');

-- Aluguel 12: Trevor Philips - GTA V (MUITO atrasado - 30 dias!)
INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status, data_inicio, data_prevista_devolucao) VALUES
(16, 2, NULL, 'ATRASADO', CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE - INTERVAL '28 days');

-- Aluguel 13: Franklin Clinton - Need for Speed (600 DIAS de aluguel!)
INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status, data_inicio, data_prevista_devolucao) VALUES
(17, 600, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '600 days', CURRENT_DATE - INTERVAL '0 days');  -- Vence hoje!

-- Aluguel 14: Ryu - Street Fighter V
INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status, data_inicio, data_prevista_devolucao) VALUES
(18, 3, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '3 days', CURRENT_DATE);

-- Aluguel 15: Ken - Street Fighter V
INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status, data_inicio, data_prevista_devolucao) VALUES
(19, 2, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '2 days', CURRENT_DATE);


-- =========================================
-- ITENS DAS TRANSAÇÕES
-- =========================================

INSERT INTO item_transacao (id_transacao, id_jogo, quantidade, valor_unitario) VALUES
(1, 1, 1, 150.00),
(2, 14, 1, 8.90),
(3, 1, 1, 9.90),
(4, 3, 1, 299.90),
(5, 13, 1, 8.90),
(6, 15, 1, 9.90),
(7, 23, 1, 99.90),
(8, 5, 1, 6.90),
(9, 10, 1, 6.90),
(10, 24, 1, 12.90),
(11, 20, 1, 79.90),
(12, 21, 1, 6.90),
(13, 16, 1, 7.90),

-- NOVOS ITENS
(14, 6, 1, 8.00),    -- Liu Kang - Final Fight
(15, 31, 1, 9.90),   -- Cranky Kong - Mario Kart
(16, 33, 1, 7.90),   -- Trevor Philips - GTA V
(17, 32, 1, 6.90),   -- Franklin Clinton - Need for Speed
(18, 34, 1, 5.90),   -- Ryu - Street Fighter V
(19, 34, 1, 5.90),   -- Ken - Street Fighter V
(20, 34, 1, 79.90);  -- Chun-Li - Street Fighter V (compra)


-- =========================================
-- COMPROVANTES
-- =========================================

INSERT INTO comprovante (id_transacao, tipo, codigo_rastreio, data_envio) VALUES
(1, 'VENDA', 'TRACK-MARIO-001', CURRENT_DATE - INTERVAL '15 days'),
(2, 'ALUGUEL', 'TRACK-SONIC-002', CURRENT_DATE - INTERVAL '5 days'),
(3, 'ALUGUEL', 'TRACK-SNAKE-003', CURRENT_DATE - INTERVAL '10 days'),
(4, 'VENDA', 'TRACK-KRATOS-004', CURRENT_DATE - INTERVAL '20 days'),
(5, 'ALUGUEL', 'TRACK-TIFA-005', CURRENT_DATE - INTERVAL '3 days'),
(6, 'ALUGUEL', 'TRACK-LUIGI-006', CURRENT_DATE - INTERVAL '2 days'),
(7, 'VENDA', 'TRACK-DOOM-007', CURRENT_DATE - INTERVAL '8 days'),
(8, 'ALUGUEL', 'TRACK-CHIEF-008', CURRENT_DATE - INTERVAL '1 day'),
(9, 'ALUGUEL', 'TRACK-LARA-009', CURRENT_DATE),
(10, 'ALUGUEL', 'TRACK-PYRAMID-010', CURRENT_DATE - INTERVAL '4 days'),
(11, 'VENDA', 'TRACK-EZIO-011', CURRENT_DATE - INTERVAL '12 days'),
(12, 'ALUGUEL', 'TRACK-CRASH-012', CURRENT_DATE - INTERVAL '6 days'),
(13, 'ALUGUEL', 'TRACK-SAMUS-013', CURRENT_DATE - INTERVAL '1 day'),

-- NOVOS COMPROVANTES
(14, 'ALUGUEL', 'TRACK-LIUKANG-014', CURRENT_DATE - INTERVAL '10 days'),
(15, 'ALUGUEL', 'TRACK-CRANKY-015', CURRENT_DATE - INTERVAL '7 days'),
(16, 'ALUGUEL', 'TRACK-TREVOR-016', CURRENT_DATE - INTERVAL '30 days'),
(17, 'ALUGUEL', 'TRACK-FRANKLIN-017', CURRENT_DATE - INTERVAL '600 days'),  -- 600 dias atrás!
(18, 'ALUGUEL', 'TRACK-RYU-018', CURRENT_DATE - INTERVAL '3 days'),
(19, 'ALUGUEL', 'TRACK-KEN-019', CURRENT_DATE - INTERVAL '2 days'),
(20, 'VENDA', 'TRACK-CHUNLI-020', CURRENT_DATE - INTERVAL '5 days');


-- =========================================
-- MULTAS (Novas multas: Trevor com multa altíssima)
-- =========================================

-- Multa para Solid Snake
INSERT INTO multa (id_aluguel, dias_atraso, valor, status, data_calculo) VALUES
(3, 3, 29.70, 'PENDENTE', CURRENT_DATE - INTERVAL '7 days');

-- Multa para Pyramid Head
INSERT INTO multa (id_aluguel, dias_atraso, valor, status, data_calculo) VALUES
(10, 3, 38.70, 'PENDENTE', CURRENT_DATE - INTERVAL '1 day');

-- Multa para Crash
INSERT INTO multa (id_aluguel, dias_atraso, valor, status, data_calculo) VALUES
(12, 2, 13.80, 'PAGO', CURRENT_DATE - INTERVAL '4 days');

-- NOVA MULTA: Trevor Philips (30 dias de atraso - multa GIGANTE!)
-- Cálculo: 30 dias atraso * (7.90 * 0.10) = 30 * 0.79 = R$ 23.70 de multa
INSERT INTO multa (id_aluguel, dias_atraso, valor, status, data_calculo) VALUES
(16, 30, 237.00, 'PENDENTE', CURRENT_DATE - INTERVAL '28 days');

-- Multa para Franklin? Ele alugou por 600 dias, mas devolveu no prazo (vence hoje)
-- Sem multa para Franklin - ele é responsável!


-- =========================================
-- AVALIACOES (Comentários hilários dos novos personagens)
-- =========================================

INSERT INTO avaliacao (id_transacao, nota, comentario, data_avaliacao) VALUES
(1, 5, 'Clássico incrível! Mario é foda! - Mario', CURRENT_DATE - INTERVAL '14 days'),
(2, 4, 'Muito divertido, mas podia ser mais rápido! - Sonic', CURRENT_DATE - INTERVAL '4 days'),
(3, 5, 'Kept you waiting, huh? - Solid Snake', CURRENT_DATE - INTERVAL '9 days'),
(4, 5, 'BOY! Excelente jogo! - Kratos', CURRENT_DATE - INTERVAL '19 days'),
(5, 4, 'O Cloud ficou lindo em 4K! - Tifa', CURRENT_DATE - INTERVAL '2 days'),
(6, 3, 'Por que eu sou sempre o player 2? - Luigi', CURRENT_DATE - INTERVAL '1 day'),
(7, 5, 'RIP AND TEAR! - Doomguy', CURRENT_DATE - INTERVAL '7 days'),
(8, 4, 'Cortana, me ajuda aqui... - Master Chief', CURRENT_DATE - INTERVAL '1 day'),
(10, 5, 'In my restless dreams, I see that town... Silent Hill - Pyramid Head', CURRENT_DATE - INTERVAL '3 days'),
(11, 5, 'Requiescat in pace. - Ezio Auditore', CURRENT_DATE - INTERVAL '11 days'),
(12, 4, 'Whoa! That was fun! - Crash Bandicoot', CURRENT_DATE - INTERVAL '5 days'),
(13, 5, 'Another planet saved. - Samus Aran', CURRENT_DATE - INTERVAL '1 day'),

-- NOVAS AVALIAÇÕES (Easter eggs puros)

-- Liu Kang avalia Final Fight: "muito violento" (IRONIA: ele é de Mortal Kombat, jogo ultra violento!)
(14, 2, 'Que jogo violento! Final Fight tem muita porradaria. Na minha época, lutávamos com honra no torneio de Mortal Kombat. - Liu Kang', CURRENT_DATE - INTERVAL '9 days'),

-- Cranky Kong avalia Mario Kart: "macacada" (trocadilho infame)
(15, 3, 'Isso é uma macacada! Na minha época, a gente subia em construção e salvava donzela. Hoje é só corridinha... - Cranky Kong', CURRENT_DATE - INTERVAL '6 days'),

-- Trevor Philips avalia GTA V (ele é personagem do jogo!)
(16, 5, 'LOS SANTOS É MINHA CASA! MELHOR JOGO DO MUNDO! Tô com o jogo há 30 dias e não vou devolver nunca mais! - Trevor Philips', CURRENT_DATE - INTERVAL '29 days'),

-- Ryu avalia Street Fighter V
(18, 5, 'SHORYUKEN! O caminho do guerreiro é infinito. Ken, você está preparado para nossa revanche? - Ryu', CURRENT_DATE - INTERVAL '2 days'),

-- Ken responde Ryu (indiretamente)
(19, 5, 'HADOUKEN! Ryu, você ainda não me superou! Vamos lutar qualquer hora. - Ken Masters', CURRENT_DATE - INTERVAL '1 day'),

-- Chun-Li avalia a compra do SFV
(20, 5, 'SPINNING BIRD KICK! Finalmente tenho meu próprio jogo. Agora posso treinar a qualquer hora. - Chun-Li', CURRENT_DATE - INTERVAL '4 days');


-- =========================================
-- RESUMO DOS NOVOS EASTER EGGS IMPLEMENTADOS
-- =========================================
/*
🎮 NOVOS EASTER EGGS ESPECIAIS:

1. LIU KANG (Mortal Kombat) → Alugou FINAL FIGHT e reclamou da violência!
   - IRONIA: Liu Kang é de Mortal Kombat, jogo famoso pela violência extrema (fatalities!)
   - Nota 2/5: "Que jogo violento! Na minha época lutávamos com honra" 🤣

2. CRANKY KONG (Donkey Kong) → Alugou MARIO KART e disse que é uma "macacada"
   - Trocadilho infame com a palavra "macacada" (coisa de macaco / bagunça)
   - Nota 3/5: "Isso é uma macacada! Na minha época a gente subia em construção..."

3. TREVOR PHILIPS (GTA V) → Multa GIGANTE por atraso (30 dias)
   - Multa calculada: R$ 237,00 (30 dias × R$ 0,79/dia)
   - Comentário: "Tô com o jogo há 30 dias e não vou devolver nunca mais!"
   - Status: PENDENTE (Trevor não paga multa nunca)

4. FRANKLIN CLINTON (GTA V) → Aluguel de NEED FOR SPEED por 600 DIAS!
   - Registro mais longo da história da locadora
   - Valor total: R$ 4.140,00 (600 × R$ 6,90)
   - Data de vencimento: HOJE (depois de 600 dias)
   - Franklin é um cliente premium responsável (sem multa)

5. STREET FIGHTER TRIO (Ryu, Ken, Chun-Li)
   - Ryu e Ken são funcionários (instrutores) mas também clientes
   - Ryu alugou SFV com ele mesmo como funcionário (meta!)
   - Ken alugou para rivalizar com Ryu
   - Chun-Li COMPROU o jogo (ela quer ter o jogo oficial)
   - Comentários com falas clássicas: SHORYUKEN, HADOUKEN, SPINNING BIRD KICK

6. EASTER EGG DO FRANKLIN:
   - Código de rastreio: TRACK-FRANKLIN-017
   - Há 600 dias atrás (quase 2 anos!)
   - Jogo: Need for Speed (velocidade, carros - perfeito para ele)

7. EASTER EGG DO TREVOR:
   - Multa mais alta do sistema: R$ 237,00
   - Comentário mais caótico: "não vou devolver nunca mais"
   - Personagem mais problemático da base

8. PIADA DO CRANKY KONG:
   - "macacada" é um trocadilho que os fãs de Donkey Kong adoram
   - Referência ao fato de que Cranky Kong é o Donkey Kong original do arcade

9. PIADA DO LIU KANG:
   - Mortal Kombat é MUITO mais violento que Final Fight
   - Liu Kang reclamando de violência é hipocrisia pura (easter egg meta)

10. TRIO STREET FIGHTER:
    - Instrutores de luta na loja (funcionários)
    - Ryu dando aula e alugando o jogo para treinar
    - Ken como rival eterno
    - Chun-Li como a mais dedicada (comprou o jogo)
*/