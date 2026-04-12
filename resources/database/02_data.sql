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
(10, 'RATCHET001', 'Atendente', 'Logística', '2002-11-04'); -- Clank (Assistente)


-- =========================================
-- CLIENTES (Personagens que consomem jogos)
-- =========================================

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
(30, 'Dojo - Hadouken Coins', '1987-08-30', 'regular'),           -- Ryu
(31, 'Dojo - Shoryuken Gold', '1987-08-30', 'regular'),           -- Ken Masters
(32, 'Spinning Bird Kick - Visa', '1991-03-01', 'premium');       -- Chun-Li


-- =========================================
-- JOGOS (Catálogo - Vitrine)
-- =========================================

INSERT INTO jogo (titulo, descricao, plataforma, genero, classificacao, valor_venda, valor_diaria_aluguel) VALUES
('Metal Gear Solid', 'Infiltração tática com Solid Snake', 'PS1', 'Ação', '16+', 199.90, 9.90),
('Halo: Combat Evolved', 'Master Chief salva a humanidade', 'Xbox', 'FPS', '16+', 149.90, 7.90),
('God of War', 'Kratos enfrenta os deuses nórdicos', 'PS5', 'Ação', '18+', NULL, 12.90),
('Metal Gear Solid 3: Snake Eater', 'A origem de Naked Snake e The Boss', 'PS2', 'Stealth', '16+', 89.90, 5.90),
('Halo 4', 'Cortana e Chief em nova aventura', 'Xbox 360', 'FPS', '16+', NULL, 6.90),
('Final Fight', 'Mike Haggar luta para salvar sua filha', 'SNES', 'Beat em up', '12+', 49.90, NULL),
('Final Fantasy VII', 'Tifa e Cloud no RPG clássico', 'PS1', 'RPG', '12+', 199.90, 8.90),
('Super Mario Bros', 'Luigi e Mario salvam a princesa', 'NES', 'Plataforma', 'Livre', NULL, 4.90),
('Ratchet & Clank', 'Clank ajuda Ratchet em missões', 'PS2', 'Ação', '10+', 79.90, NULL),
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
('Assassin''s Creed II', 'Ezio Auditore na Renascença Italiana', 'PS3', 'Ação', '16+', 79.90, 4.90),
('Crash Bandicoot 4: It''s About Time', 'Crash em nova aventura', 'PS4', 'Plataforma', 'Livre', 149.90, 6.90),
('Spyro Reignited Trilogy', 'Spyro em 3 jogos remasterizados', 'PS4', 'Aventura', 'Livre', 129.90, 5.90),
('DOOM Eternal', 'Doomguy contra demônios', 'PS4', 'FPS', '18+', 99.90, 6.90),
('Silent Hill 2', 'Pyramid Head e o terror psicológico', 'PS2', 'Survival Horror', '18+', 299.90, 12.90),
('Street Fighter II', 'Luta arcade clássica', 'Arcade', 'Luta', '12+', 120.00, 8.00),
('The Legend of Zelda: Ocarina of Time', 'Aventura épica de Link', 'N64', 'Aventura', '10+', 250.00, 10.00),
('Pokémon Red', 'Colete todos os 151 pokémon', 'Game Boy', 'RPG', 'Livre', 300.00, 8.00),
('Castlevania: Symphony of the Night', 'Alucard e o castelo de Drácula', 'PS1', 'Ação', '14+', 180.00, 7.00),
('Shadow of the Colossus', '16 colossos para derrubar', 'PS2', 'Aventura', '12+', 120.00, 6.00),
('Mortal Kombat 11', 'Liu Kang e o torneio mortal', 'PS4', 'Luta', '18+', 99.90, 7.90),
('Mario Kart 8 Deluxe', 'Corrida maluca com os personagens da Nintendo', 'Switch', 'Corrida', 'Livre', 299.90, 9.90),
('Need for Speed: Heat', 'Corrida de rua e perseguição policial', 'PS4', 'Corrida', '14+', 129.90, 6.90),
('Grand Theft Auto V', 'Trevor, Franklin e Michael em Los Santos', 'PS4', 'Ação', '18+', 99.90, 7.90),
('Street Fighter V', 'Ryu, Ken e Chun-Li no torneio definitivo', 'PS4', 'Luta', '12+', 79.90, 5.90);


-- =========================================
-- EXEMPLARES (1 Jogo -> N Exemplares)
-- =========================================

INSERT INTO exemplar (id, id_jogo, tipo_midia) VALUES
-- Mídias Físicas
(1, 1, 'FISICA'),
(2, 2, 'FISICA'),
(4, 4, 'FISICA'),
(6, 6, 'FISICA'),
(7, 7, 'FISICA'),
(10, 10, 'FISICA'),
(12, 12, 'FISICA'),
(16, 16, 'FISICA'),
(17, 17, 'FISICA'),
(19, 19, 'FISICA'),
(20, 20, 'FISICA'),
(21, 21, 'FISICA'),
(22, 22, 'FISICA'),
(23, 23, 'FISICA'),
(24, 24, 'FISICA'),
(25, 25, 'FISICA'),
(26, 26, 'FISICA'),
(27, 27, 'FISICA'),
(28, 28, 'FISICA'),
(29, 29, 'FISICA'),
(30, 30, 'FISICA'),
(31, 31, 'FISICA'),
(32, 32, 'FISICA'),
(33, 33, 'FISICA'),
(34, 34, 'FISICA'),
(35, 34, 'FISICA'), -- Segunda cópia física de SFV para não cruzar aluguel ao mesmo tempo!

-- Mídias Digitais
(103, 3, 'DIGITAL'),
(105, 5, 'DIGITAL'),
(108, 8, 'DIGITAL'),
(111, 11, 'DIGITAL'),
(113, 13, 'DIGITAL'),
(114, 14, 'DIGITAL'),
(115, 15, 'DIGITAL'),
(118, 18, 'DIGITAL'),
(133, 33, 'DIGITAL'),
(134, 34, 'DIGITAL');


-- =========================================
-- MIDIAS FISICAS E DIGITAIS
-- =========================================

INSERT INTO midia_fisica (id_exemplar, codigo_barras, estado_conservacao) VALUES
(1, 'MGS001-BR', 'EXCELENTE'),
(2, 'HALO001-BR', 'EXCELENTE'),
(4, 'MGS302-BR', 'BOM'),
(6, 'FFIGHT01-BR', 'REGULAR'),
(7, 'FFVII01-BR', 'EXCELENTE'),
(10, 'TOMB01-BR', 'BOM'),
(12, 'RE301-BR', 'REGULAR'),
(16, 'METROID01-BR', 'EXCELENTE'),
(17, 'WITCHER01-BR', 'BOM'),
(19, 'TLOU01-BR', 'EXCELENTE'),
(20, 'AC02-BR', 'BOM'),
(21, 'CRASH04-BR', 'EXCELENTE'),
(22, 'SPYRO-BR', 'BOM'),
(23, 'DOOM-BR', 'EXCELENTE'),
(24, 'SH02-BR', 'REGULAR'),
(25, 'SF02-BR', 'EXCELENTE'),
(26, 'ZELDA64-BR', 'BOM'),
(27, 'POKEMONRED-BR', 'REGULAR'),
(28, 'CASTLE-BR', 'EXCELENTE'),
(29, 'SHADOW-BR', 'BOM'),
(30, 'MK11-BR', 'EXCELENTE'),
(31, 'MARIOKART-BR', 'EXCELENTE'),
(32, 'NFS-BR', 'BOM'),
(33, 'GTA5-BR', 'EXCELENTE'),
(34, 'SF5-BR', 'EXCELENTE'),
(35, 'SF5-BR-2', 'BOM');

INSERT INTO midia_digital (id_exemplar, chave_ativacao, data_expiracao) VALUES
(103, 'GOW-KRATOS-2026-001', '2030-12-31'),
(105, 'HALO4-CORTANA-002', '2030-12-31'),
(108, 'MARIO-LUIGI-003', '2030-12-31'),
(111, 'UNCHARTED-DRAKE-004', '2030-12-31'),
(113, 'FFVII-CLOUD-0045', '2030-12-31'),
(114, 'SONIC-FRONTIERS-005', '2030-12-31'),
(115, 'MARIO-ODYSSEY-006', '2030-12-31'),
(118, 'RDR2-ARTHUR-007', '2030-12-31'),
(133, 'GTA5-TREVOR-008', '2030-12-31'),
(134, 'SF5-RYU-009', '2030-12-31');


-- =========================================
-- RESERVAS
-- =========================================

INSERT INTO reserva (id_cliente, id_jogo, status, data_reserva, data_expiracao) VALUES
(11, 10, 'ATIVA', CURRENT_DATE, CURRENT_DATE + INTERVAL '2 days'),
(14, 13, 'ATIVA', CURRENT_DATE, CURRENT_DATE + INTERVAL '2 days'),
(18, 17, 'ATIVA', CURRENT_DATE, CURRENT_DATE + INTERVAL '2 days'),
(12, 11, 'CANCELADA', CURRENT_DATE - INTERVAL '5 days', CURRENT_DATE - INTERVAL '3 days'),
(13, 12, 'ATIVA', CURRENT_DATE, CURRENT_DATE + INTERVAL '1 day'),
(15, 14, 'ATIVA', CURRENT_DATE, CURRENT_DATE + INTERVAL '2 days'),
(30, 34, 'ATIVA', CURRENT_DATE, CURRENT_DATE + INTERVAL '3 days');


-- =========================================
-- TRANSACOES
-- =========================================

INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao) VALUES
(150.00, 'CONCLUIDA', 16, 1, CURRENT_DATE - INTERVAL '15 days'), -- venda
(17.80, 'CONCLUIDA', 15, 7, CURRENT_DATE - INTERVAL '5 days'), --aluguel
(29.70, 'CONCLUIDA', 1, 4, CURRENT_DATE - INTERVAL '10 days'), --aluguel
(299.90, 'CONCLUIDA', 3, 2, CURRENT_DATE - INTERVAL '20 days'), --venda
(26.70, 'CONCLUIDA', 8, 8, CURRENT_DATE - INTERVAL '3 days'), --aluguel
(19.80, 'CONCLUIDA', 9, 9, CURRENT_DATE - INTERVAL '2 days'), --aluguel
(99.90, 'CONCLUIDA', 24, 1, CURRENT_DATE - INTERVAL '8 days'), --venda
(13.80, 'CONCLUIDA', 2, 2, CURRENT_DATE - INTERVAL '1 day'), --aluguel
(6.90, 'CONCLUIDA', 11, 7, CURRENT_DATE), --aluguel
(25.80, 'CONCLUIDA', 25, 8, CURRENT_DATE - INTERVAL '4 days'), --aluguel
(79.90, 'CONCLUIDA', 21, 9, CURRENT_DATE - INTERVAL '12 days'), --venda
(13.80, 'CONCLUIDA', 22, 10, CURRENT_DATE - INTERVAL '6 days'),
(7.90, 'CONCLUIDA', 17, 7, CURRENT_DATE - INTERVAL '1 day'),
(8.00, 'CONCLUIDA', 26, 7, CURRENT_DATE - INTERVAL '10 days'),
(9.90, 'CONCLUIDA', 27, 9, CURRENT_DATE - INTERVAL '7 days'),
(15.80, 'CONCLUIDA', 28, 1, CURRENT_DATE - INTERVAL '30 days'),
(4140.00, 'CONCLUIDA', 29, 10, CURRENT_DATE - INTERVAL '600 days'),
(15.90, 'CONCLUIDA', 30, 7, CURRENT_DATE - INTERVAL '3 days'),
(15.90, 'CONCLUIDA', 31, 8, CURRENT_DATE - INTERVAL '2 days'),
(79.90, 'CONCLUIDA', 32, 9, CURRENT_DATE - INTERVAL '5 days'); --venda


-- =========================================
-- VENDAS
-- =========================================

INSERT INTO venda (id_transacao, status, data_confirmacao) VALUES
(1, 'FINALIZADA', CURRENT_DATE - INTERVAL '15 days'),
(4, 'FINALIZADA', CURRENT_DATE - INTERVAL '20 days'),
(7, 'FINALIZADA', CURRENT_DATE - INTERVAL '8 days'),
(11, 'FINALIZADA', CURRENT_DATE - INTERVAL '12 days'),
(20, 'FINALIZADA', CURRENT_DATE - INTERVAL '5 days');


-- =========================================
-- ALUGUEIS
-- =========================================

INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status, data_inicio, data_prevista_devolucao) VALUES
(2, 2, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '5 days', CURRENT_DATE - INTERVAL '3 days'),
(3, 3, NULL, 'ATRASADO', CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE - INTERVAL '7 days'),
(5, 3, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '3 days', CURRENT_DATE + INTERVAL '1 day'),
(6, 2, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '2 days', CURRENT_DATE),
(8, 2, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '1 day', CURRENT_DATE),
(9, 1, NULL, 'ATIVO', CURRENT_DATE, CURRENT_DATE + INTERVAL '1 day'),
(10, 3, NULL, 'ATRASADO', CURRENT_DATE - INTERVAL '4 days', CURRENT_DATE - INTERVAL '1 day'),
(12, 2, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '6 days', CURRENT_DATE - INTERVAL '4 days'),
(13, 1, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '1 day', CURRENT_DATE),
(14, 1, CURRENT_DATE - INTERVAL '9 days', 'FINALIZADO', CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE - INTERVAL '9 days'),
(15, 1, CURRENT_DATE - INTERVAL '6 days', 'FINALIZADO', CURRENT_DATE - INTERVAL '7 days', CURRENT_DATE - INTERVAL '6 days'),
(16, 2, NULL, 'ATRASADO', CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE - INTERVAL '28 days'),
(17, 600, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '600 days', CURRENT_DATE - INTERVAL '0 days'),
(18, 3, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '3 days', CURRENT_DATE),
(19, 2, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '2 days', CURRENT_DATE);


-- =========================================
-- ITENS DAS TRANSAÇÕES (Apontam para EXEMPLARES)
-- =========================================

INSERT INTO item_transacao (id_transacao, id_exemplar, valor_unitario) VALUES
(1, 1, 150.00),     -- Mario World (fisico 1)
(2, 114, 8.90),     -- Sonic Frontiers (digital 114)
(3, 1, 9.90),       -- MGS (fisico 1)
(4, 103, 299.90),   -- GOW (digital 103)
(5, 113, 8.90),     -- FFVII Remake (digital 113)
(6, 115, 9.90),     -- Mario Odyssey (digital 115)
(7, 23, 99.90),     -- Doom Eternal (fisico 23)
(8, 105, 6.90),     -- Halo 4 (digital 105)
(9, 10, 6.90),      -- Tomb Raider (fisico 10)
(10, 24, 12.90),    -- Silent Hill 2 (fisico 24)
(11, 20, 79.90),    -- AC II (fisico 20)
(12, 21, 6.90),     -- Crash (fisico 21)
(13, 16, 7.90),     -- Metroid (fisico 16)
(14, 6, 8.00),      -- Final Fight (fisico 6)
(15, 31, 9.90),     -- Mario Kart (fisico 31)
(16, 33, 7.90),     -- GTA V (fisico 33)
(17, 32, 6.90),     -- Need for Speed (fisico 32)
(18, 34, 5.90),     -- SFV (fisico 34 - locação Ryu)
(19, 35, 5.90),     -- SFV (fisico 35 - locação Ken - cópia 2 para não dar conflito)
(20, 34, 79.90);    -- SFV (fisico 34 - venda Chun Li, assume-se que ela comprou a cópia que o Ryu devolveu no futuro ou simulado rs)


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
(14, 'ALUGUEL', 'TRACK-LIUKANG-014', CURRENT_DATE - INTERVAL '10 days'),
(15, 'ALUGUEL', 'TRACK-CRANKY-015', CURRENT_DATE - INTERVAL '7 days'),
(16, 'ALUGUEL', 'TRACK-TREVOR-016', CURRENT_DATE - INTERVAL '30 days'),
(17, 'ALUGUEL', 'TRACK-FRANKLIN-017', CURRENT_DATE - INTERVAL '600 days'),
(18, 'ALUGUEL', 'TRACK-RYU-018', CURRENT_DATE - INTERVAL '3 days'),
(19, 'ALUGUEL', 'TRACK-KEN-019', CURRENT_DATE - INTERVAL '2 days'),
(20, 'VENDA', 'TRACK-CHUNLI-020', CURRENT_DATE - INTERVAL '5 days');


-- =========================================
-- MULTAS
-- =========================================

INSERT INTO multa (id_aluguel, dias_atraso, valor, status, data_calculo) VALUES
(3, 3, 29.70, 'PENDENTE', CURRENT_DATE - INTERVAL '7 days'),
(10, 3, 38.70, 'PENDENTE', CURRENT_DATE - INTERVAL '1 day'),
(12, 2, 13.80, 'PAGO', CURRENT_DATE - INTERVAL '4 days'),
(16, 30, 237.00, 'PENDENTE', CURRENT_DATE - INTERVAL '28 days');


-- =========================================
-- AVALIACOES
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
(14, 2, 'Que jogo violento! Final Fight tem muita porradaria. Na minha época, lutávamos com honra no torneio de Mortal Kombat. - Liu Kang', CURRENT_DATE - INTERVAL '9 days'),
(15, 3, 'Isso é uma macacada! Na minha época, a gente subia em construção e salvava donzela. Hoje é só corridinha... - Cranky Kong', CURRENT_DATE - INTERVAL '6 days'),
(16, 5, 'LOS SANTOS É MINHA CASA! MELHOR JOGO DO MUNDO! Tô com o jogo há 30 dias e não vou devolver nunca mais! - Trevor Philips', CURRENT_DATE - INTERVAL '29 days'),
(18, 5, 'SHORYUKEN! O caminho do guerreiro é infinito. Ken, você está preparado para nossa revanche? - Ryu', CURRENT_DATE - INTERVAL '2 days'),
(19, 5, 'HADOUKEN! Ryu, você ainda não me superou! Vamos lutar qualquer hora. - Ken Masters', CURRENT_DATE - INTERVAL '1 day'),
(20, 5, 'SPINNING BIRD KICK! Finalmente tenho meu próprio jogo. Agora posso treinar a qualquer hora. - Chun-Li', CURRENT_DATE - INTERVAL '4 days');
