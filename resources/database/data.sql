-- =========================================
-- RESET (opcional - se precisar recriar tudo)
-- =========================================
/*
TRUNCATE TABLE avaliacao, multa, comprovante, item_transacao, aluguel, venda, transacao, reserva, midia_fisica, midia_digital, exemplar, catalogo, cliente, funcionario, usuario RESTART IDENTITY CASCADE;
*/

-- =========================================
-- USUARIOS (Com campo tipo corrigido)
-- =========================================
INSERT INTO usuario (nome, cpf, email, senha, data_nascimento, tipo) VALUES
-- Administradores (Funcionários)
('Solid Snake', '111.111.111-11', 'snake@metalgear.com', 'hash123', '1972-06-12', 'funcionario'),
('Rachel Teller', '222.222.222-22', 'chief@nfsunderground2.com', 'hash123', '2511-03-07', 'funcionario'),
('Luigi', '333.333.333-33', 'luigi@smw.com', 'hash123', '2005-11-22', 'funcionario'),

-- Gerentes/Atendentes (Funcionários)
('Major Zero', '444.444.444-44', 'zero@metalgear.com', 'hash123', '1950-09-13', 'funcionario'),
('The Boss', '555.555.555-55', 'boss@metalgear.com', 'hash123', '1927-09-10', 'funcionario'),
('Mike Haggar', '666.666.666-66', 'haggar@finalfight.com', 'hash123', '1962-04-18', 'funcionario'),


-- Clientes Premium
('Sam Fisher', '777.777.777-77', 'fisher@splintercell.com', 'hash123', '2001-11-07', 'cliente'),
('Tifa Lockhart', '888.888.888-88', 'tifa@finalfantasy.com', 'hash123', '1987-05-03', 'cliente'),  -- ← É cliente!
('Kratos', '999.999.999-99', 'kratos@godofwar.com', 'hash123', '2005-11-22', 'cliente'),  -- ← É cliente!
('Kung Lao', '123.456.789-00', 'kunglao@mortalkombat.com', 'hash123', '2002-11-04', 'cliente'),
('Lara Croft', '101.202.303-44', 'lara@tombraider.com', 'hash123', '1968-02-14', 'cliente'),
('Nathan Drake', '202.303.404-55', 'drake@uncharted.com', 'hash123', '1976-10-19', 'cliente'),
('Jill Valentine', '303.404.505-66', 'jill@residentevil.com', 'hash123', '1974-11-30', 'cliente'),
('Cloud Strife', '404.505.606-77', 'cloud@retrohub.com', 'hash123', '1986-08-11', 'cliente'),
('Sonic', '505.606.707-88', 'sonic@retrohub.com', 'hash123', '1991-06-23', 'cliente'),
('Mario', '606.707.808-99', 'mario@smw.com', 'hash123', '1981-07-09', 'cliente'),
('Samus Aran', '707.808.909-00', 'samus@retrohub.com', 'hash123', '1986-08-06', 'cliente'),
('Geralt of Rivia', '808.909.010-11', 'geralt@retrohub.com', 'hash123', '1990-05-18', 'cliente'),
('Arthur Morgan', '909.010.121-22', 'arthur@retrohub.com', 'hash123', '1899-05-05', 'cliente'),
('Ellie Williams', '010.121.232-33', 'ellie@retrohub.com', 'hash123', '2013-06-14', 'cliente'),

-- Clientes casuais
('Ezio Auditore', '111.212.333-44', 'ezio@assassinscreed.com', 'hash123', '1459-06-24', 'cliente'),
('Crash Bandicoot', '212.323.444-55', 'crash@retrohub.com', 'hash123', '1996-09-09', 'cliente'),
('Spyro', '313.434.555-66', 'spyro@retrohub.com', 'hash123', '1998-09-10', 'cliente'),
('Doomguy', '414.545.666-77', 'doom@retrohub.com', 'hash123', '1993-12-10', 'cliente'),
('Pyramid Head', '515.656.777-88', 'pyramid@retrohub.com', 'hash123', '2001-09-24', 'cliente'),

-- NOVOS PERSONAGENS (Easter eggs)
('Liu Kang', '616.767.888-99', 'liukang@mortalkombat.com', 'hash123', '1992-10-08', 'cliente'),
('Cranky Kong', '717.878.999-00', 'cranky@donkeykong.com', 'hash123', '1981-07-09', 'cliente'),
('Trevor Philips', '818.989.000-11', 'trevor@gta.com', 'hash123', '1965-01-01', 'cliente'),
('Franklin Clinton', '919.090.111-22', 'franklin@gta.com', 'hash123', '1988-06-01', 'cliente'),
('Ryu', '020.131.242-33', 'ryu@streetfighter.com', 'hash123', '1987-08-30', 'cliente'),
('Ken Masters', '121.242.353-44', 'ken@streetfighter.com', 'hash123', '1987-08-30', 'cliente'),
('Chun-Li', '222.353.464-55', 'chunli@streetfighter.com', 'hash123', '1991-03-01', 'cliente');


-- =========================================
-- FUNCIONARIOS (Apenas usuários com tipo='funcionario')
-- =========================================
INSERT INTO funcionario (id_usuario, matricula, cargo, setor, data_admissao) VALUES
(1, 'FOX001', 'Administrador', 'TI', '1998-09-03'),      -- Solid Snake
(2, 'NFS001', 'Administrador', 'TI', '2004-11-15'),      -- Rachel Teller
(3, 'MUSHROOM001', 'Atendente', 'Estoque', '1983-09-13'),-- Luigi
(4, 'FOX002', 'Gerente', 'Operações', '1964-10-12'),     -- Major Zero
(5, 'FOX003', 'Gerente', 'RH', '1942-06-13'),            -- The Boss
(6, 'METRO001', 'Atendente', 'Vendas', '1989-12-11');    -- Mike Haggar


-- =========================================
-- CLIENTES (Apenas usuários com tipo='cliente')
-- =========================================
INSERT INTO cliente (id_usuario, dados_pagamento, tipo_cliente) VALUES
-- Personagens que são SOMENTE clientes (não funcionários)
(7, 'Créditos Echelon', 'regular'),                       -- Sam Fisher
(8, 'Gil (Final Fantasy)', 'regular'),                    -- Tifa
(9, 'Ouro de Esparta', 'premium'),                        -- Kratos
(10, 'Chapeu de Kung Lao', 'regular'),                    -- Kung Lao
(11, 'Cartão Black - Visa Infinite', 'premium'),          -- Lara Croft
(12, 'Cartão Platinum - Mastercard', 'premium'),          -- Nathan Drake
(13, 'Pix - Chave aleatória', 'regular'),                 -- Jill Valentine
(14, 'Bitcoin Wallet', 'premium'),                        -- Cloud Strife
(15, 'Ouriço Cash', 'regular'),                           -- Sonic
(16, 'Estrelas do Mario', 'premium'),                     -- Mario
(17, 'Cartão Metroid - Visa', 'regular'),                 -- Samus Aran
(18, 'Moedas de Ouro', 'premium'),                        -- Geralt
(19, 'Dólar do Faroeste', 'regular'),                     -- Arthur Morgan
(20, 'Cartão Ellie - Mastercard', 'premium'),             -- Ellie Williams
(21, 'Carteira dos Assassinos', 'regular'),               -- Ezio Auditore
(22, 'Fruta Wumpa', 'regular'),                           -- Crash Bandicoot
(23, 'Joias de Dragão', 'regular'),                       -- Spyro
(24, 'BFG Division - Dinheiro', 'premium'),               -- Doomguy
(25, 'Almas Perdidas', 'regular'),                        -- Pyramid Head
(26, 'Fireball Fists - Dragon Coin', 'regular'),          -- Liu Kang
(27, 'Barris de Ouro', 'regular'),                        -- Cranky Kong
(28, 'Dinheiro Sujo - Off Shore', 'regular'),             -- Trevor Philips
(29, 'Garagem de Carros', 'premium'),                     -- Franklin Clinton
(30, 'Dojo - Hadouken Coins', 'regular'),                 -- Ryu
(31, 'Dojo - Shoryuken Gold', 'regular'),                 -- Ken Masters
(32, 'Spinning Bird Kick - Visa', 'premium');             -- Chun-Li


-- =========================================
-- CATALOGO (antigo jogo)
-- =========================================
INSERT INTO catalogo (id, titulo, descricao, plataforma, genero, classificacao, valor_venda, valor_diaria_aluguel, ativo) VALUES
(1, 'Metal Gear Solid', 'Infiltração tática com Solid Snake', 'PS1', 'Ação', '16+', 199.90, 9.90, true),
(2, 'Halo: Combat Evolved', 'Master Chief salva a humanidade', 'Xbox', 'FPS', '16+', 149.90, 7.90, true),
(3, 'God of War', 'Kratos enfrenta os deuses nórdicos', 'PS5', 'Ação', '18+', NULL, 12.90, true),
(4, 'Metal Gear Solid 3: Snake Eater', 'A origem de Naked Snake e The Boss', 'PS2', 'Stealth', '16+', 89.90, 5.90, true),
(5, 'Halo 4', 'Cortana e Chief em nova aventura', 'Xbox 360', 'FPS', '16+', NULL, 6.90, true),
(6, 'Final Fight', 'Mike Haggar luta para salvar sua filha', 'SNES', 'Beat em up', '12+', 49.90, NULL, true),
(7, 'Final Fantasy VII', 'Tifa e Cloud no RPG clássico', 'PS1', 'RPG', '12+', 199.90, 8.90, true),
(8, 'Super Mario Bros', 'Luigi e Mario salvam a princesa', 'NES', 'Plataforma', 'Livre', NULL, 4.90, true),
(9, 'Ratchet & Clank', 'Clank ajuda Ratchet em missões', 'PS2', 'Ação', '10+', 79.90, NULL, true),
(10, 'Tomb Raider', 'Lara Croft explora tumbas antigas', 'PS4', 'Aventura', '16+', 129.90, 6.90, true),
(11, 'Uncharted 4: A Thief''s End', 'Nathan Drake em busca de tesouros', 'PS4', 'Aventura', '16+', NULL, 7.90, true),
(12, 'Resident Evil 3', 'Jill Valentine enfrenta Nemesis', 'PS1', 'Survival Horror', '18+', 89.90, 5.90, true),
(13, 'Final Fantasy VII Remake', 'Cloud Strife em alta definição', 'PS5', 'RPG', '12+', 249.90, NULL, true),
(14, 'Sonic Frontiers', 'Sonic em mundo aberto', 'Switch', 'Aventura', 'Livre', NULL, 8.90, true),
(15, 'Super Mario Odyssey', 'Mario viaja pelo mundo', 'Switch', 'Plataforma', 'Livre', 299.90, 9.90, true),
(16, 'Metroid Dread', 'Samus Aran em missão mortal', 'Switch', 'Ação', '12+', NULL, 7.90, true),
(17, 'The Witcher 3: Wild Hunt', 'Geralt caça monstros', 'PS4', 'RPG', '18+', 99.90, 5.90, true),
(18, 'Red Dead Redemption 2', 'Arthur Morgan no faroeste', 'PS4', 'Ação', '18+', 149.90, NULL, true),
(19, 'The Last of Us Part II', 'Ellie em busca de vingança', 'PS4', 'Aventura', '18+', 199.90, 8.90, true),
(20, 'Assassin''s Creed II', 'Ezio Auditore na Renascença Italiana', 'PS3', 'Ação', '16+', 79.90, 4.90, true),
(21, 'Crash Bandicoot 4: It''s About Time', 'Crash em nova aventura', 'PS4', 'Plataforma', 'Livre', 149.90, 6.90, true),
(22, 'Spyro Reignited Trilogy', 'Spyro em 3 jogos remasterizados', 'PS4', 'Aventura', 'Livre', 129.90, 5.90, true),
(23, 'DOOM Eternal', 'Doomguy contra demônios', 'PS4', 'FPS', '18+', 99.90, 6.90, true),
(24, 'Silent Hill 2', 'Pyramid Head e o terror psicológico', 'PS2', 'Survival Horror', '18+', 299.90, 12.90, true),
(25, 'Street Fighter II', 'Luta arcade clássica', 'Arcade', 'Luta', '12+', 120.00, 8.00, true),
(26, 'The Legend of Zelda: Ocarina of Time', 'Aventura épica de Link', 'N64', 'Aventura', '10+', 250.00, 10.00, true),
(27, 'Pokémon Red', 'Colete todos os 151 pokémon', 'Game Boy', 'RPG', 'Livre', 300.00, 8.00, true),
(28, 'Castlevania: Symphony of the Night', 'Alucard e o castelo de Drácula', 'PS1', 'Ação', '14+', 180.00, 7.00, true),
(29, 'Shadow of the Colossus', '16 colossos para derrubar', 'PS2', 'Aventura', '12+', 120.00, 6.00, true),
(30, 'Mortal Kombat 11', 'Liu Kang e o torneio mortal', 'PS4', 'Luta', '18+', 99.90, 7.90, true),
(31, 'Mario Kart 8 Deluxe', 'Corrida maluca com os personagens da Nintendo', 'Switch', 'Corrida', 'Livre', 299.90, 9.90, true),
(32, 'Need for Speed: Heat', 'Corrida de rua e perseguição policial', 'PS4', 'Corrida', '14+', 129.90, 6.90, true),
(33, 'Grand Theft Auto V', 'Trevor, Franklin e Michael em Los Santos', 'PS4', 'Ação', '18+', 99.90, 7.90, true),
(34, 'Street Fighter V', 'Ryu, Ken e Chun-Li no torneio definitivo', 'PS4', 'Luta', '12+', 79.90, 5.90, true);

-- Reset sequence
SELECT setval('catalogo_id_seq', 34, true);


-- =========================================
-- EXEMPLARES (com tipo_midia corrigido)
-- =========================================
INSERT INTO exemplar (id, id_catalogo, tipo_midia) VALUES
-- Mídias Físicas (1-35)
(1, 1, 'FISICA'),
(2, 2, 'FISICA'),
(3, 3, 'FISICA'),
(4, 4, 'FISICA'),
(5, 5, 'FISICA'),
(6, 6, 'FISICA'),
(7, 7, 'FISICA'),
(8, 8, 'FISICA'),
(9, 9, 'FISICA'),
(10, 10, 'FISICA'),
(11, 11, 'FISICA'),
(12, 12, 'FISICA'),
(13, 13, 'FISICA'),
(14, 14, 'FISICA'),
(15, 15, 'FISICA'),
(16, 16, 'FISICA'),
(17, 17, 'FISICA'),
(18, 18, 'FISICA'),
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
(35, 34, 'FISICA'),  -- Segunda cópia do SFV

-- Mídias Digitais (103-134)
(103, 3, 'DIGITAL'),
(104, 4, 'DIGITAL'),
(105, 5, 'DIGITAL'),
(106, 6, 'DIGITAL'),
(107, 7, 'DIGITAL'),
(108, 8, 'DIGITAL'),
(109, 9, 'DIGITAL'),
(110, 10, 'DIGITAL'),
(111, 11, 'DIGITAL'),
(112, 12, 'DIGITAL'),
(113, 13, 'DIGITAL'),
(114, 14, 'DIGITAL'),
(115, 15, 'DIGITAL'),
(116, 16, 'DIGITAL'),
(117, 17, 'DIGITAL'),
(118, 18, 'DIGITAL'),
(119, 19, 'DIGITAL'),
(120, 20, 'DIGITAL'),
(121, 21, 'DIGITAL'),
(122, 22, 'DIGITAL'),
(123, 23, 'DIGITAL'),
(124, 24, 'DIGITAL'),
(125, 25, 'DIGITAL'),
(126, 26, 'DIGITAL'),
(127, 27, 'DIGITAL'),
(128, 28, 'DIGITAL'),
(129, 29, 'DIGITAL'),
(130, 30, 'DIGITAL'),
(131, 31, 'DIGITAL'),
(132, 32, 'DIGITAL'),
(133, 33, 'DIGITAL'),
(134, 34, 'DIGITAL');

-- Reset sequence
SELECT setval('exemplar_id_seq', 134, true);


-- =========================================
-- MIDIAS FISICAS
-- =========================================
INSERT INTO midia_fisica (id_exemplar, codigo_barras, estado_conservacao) VALUES
(1, 'MGS001-BR', 'EXCELENTE'),
(2, 'HALO001-BR', 'EXCELENTE'),
(3, 'GOW001-BR', 'EXCELENTE'),
(4, 'MGS302-BR', 'BOM'),
(5, 'HALO401-BR', 'BOM'),
(6, 'FFIGHT01-BR', 'REGULAR'),
(7, 'FFVII01-BR', 'EXCELENTE'),
(8, 'SMARIO01-BR', 'BOM'),
(9, 'RATCHET01-BR', 'EXCELENTE'),
(10, 'TOMB01-BR', 'BOM'),
(11, 'UNCHARTED01-BR', 'EXCELENTE'),
(12, 'RE301-BR', 'REGULAR'),
(13, 'FFVIIR01-BR', 'EXCELENTE'),
(14, 'SONICF01-BR', 'BOM'),
(15, 'MARIOOD01-BR', 'EXCELENTE'),
(16, 'METROID01-BR', 'EXCELENTE'),
(17, 'WITCHER01-BR', 'BOM'),
(18, 'RDR201-BR', 'EXCELENTE'),
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


-- =========================================
-- MIDIAS DIGITAIS
-- =========================================
INSERT INTO midia_digital (id_exemplar, chave_ativacao, data_expiracao) VALUES
(103, 'GOW-KRATOS-2026-001', '2030-12-31'),
(104, 'MGS3-SNAKE-002', '2030-12-31'),
(105, 'HALO4-CORTANA-003', '2030-12-31'),
(106, 'FIGHT-HAGGAR-004', '2030-12-31'),
(107, 'FFVII-CLOUD-005', '2030-12-31'),
(108, 'MARIO-LUIGI-006', '2030-12-31'),
(109, 'RATCHET-CLANK-007', '2030-12-31'),
(110, 'TOMB-LARA-008', '2030-12-31'),
(111, 'UNCHARTED-DRAKE-009', '2030-12-31'),
(112, 'RE3-JILL-010', '2030-12-31'),
(113, 'FFVII-CLOUD-011', '2030-12-31'),
(114, 'SONIC-FRONTIERS-012', '2030-12-31'),
(115, 'MARIO-ODYSSEY-013', '2030-12-31'),
(116, 'METROID-SAMUS-014', '2030-12-31'),
(117, 'WITCHER-GERALT-015', '2030-12-31'),
(118, 'RDR2-ARTHUR-016', '2030-12-31'),
(119, 'TLOU-ELLIE-017', '2030-12-31'),
(120, 'AC2-EZIO-018', '2030-12-31'),
(121, 'CRASH-WUMPA-019', '2030-12-31'),
(122, 'SPYRO-DRAGON-020', '2030-12-31'),
(123, 'DOOM-SLAYER-021', '2030-12-31'),
(124, 'SILENT-PYRAMID-022', '2030-12-31'),
(125, 'SF2-RYU-023', '2030-12-31'),
(126, 'ZELDA-LINK-024', '2030-12-31'),
(127, 'POKEMON-ASH-025', '2030-12-31'),
(128, 'CASTLE-ALUCARD-026', '2030-12-31'),
(129, 'COLOSSUS-WANDER-027', '2030-12-31'),
(130, 'MK11-LIUKANG-028', '2030-12-31'),
(131, 'MARIOKART-MARIO-029', '2030-12-31'),
(132, 'NFS-RACHEL-030', '2030-12-31'),
(133, 'GTA5-TREVOR-031', '2030-12-31'),
(134, 'SF5-RYU-032', '2030-12-31');


-- =========================================
-- RESERVAS (id_jogo → id_catalogo)
-- =========================================
INSERT INTO reserva (id_cliente, id_catalogo, status, data_reserva, data_expiracao) VALUES
((SELECT id_usuario FROM cliente WHERE id_usuario = 11), 10, 'ATIVA', CURRENT_DATE, CURRENT_DATE + INTERVAL '2 days'),
((SELECT id_usuario FROM cliente WHERE id_usuario = 14), 13, 'ATIVA', CURRENT_DATE, CURRENT_DATE + INTERVAL '2 days'),
((SELECT id_usuario FROM cliente WHERE id_usuario = 18), 17, 'ATIVA', CURRENT_DATE, CURRENT_DATE + INTERVAL '2 days'),
((SELECT id_usuario FROM cliente WHERE id_usuario = 12), 11, 'CANCELADA', CURRENT_DATE - INTERVAL '5 days', CURRENT_DATE - INTERVAL '3 days'),
((SELECT id_usuario FROM cliente WHERE id_usuario = 13), 12, 'ATIVA', CURRENT_DATE, CURRENT_DATE + INTERVAL '1 day'),
((SELECT id_usuario FROM cliente WHERE id_usuario = 15), 14, 'ATIVA', CURRENT_DATE, CURRENT_DATE + INTERVAL '2 days'),
((SELECT id_usuario FROM cliente WHERE id_usuario = 30), 34, 'ATIVA', CURRENT_DATE, CURRENT_DATE + INTERVAL '3 days');


-- =========================================
-- TRANSACOES (com tipo corrigido)
-- =========================================
INSERT INTO transacao (valor_total, status, id_cliente, id_funcionario, data_transacao, tipo) VALUES
-- Vendas (id_cliente deve existir em cliente)
(150.00, 'CONCLUIDA', 16, 1, CURRENT_DATE - INTERVAL '15 days', 'VENDA'),     -- Mario (16 é cliente ✅)
(299.90, 'CONCLUIDA', 9, 2, CURRENT_DATE - INTERVAL '20 days', 'VENDA'),      -- Kratos (3 é cliente ✅)
(99.90, 'CONCLUIDA', 24, 1, CURRENT_DATE - INTERVAL '8 days', 'VENDA'),       -- Doomguy (24 é cliente ✅)
(79.90, 'CONCLUIDA', 21, 3, CURRENT_DATE - INTERVAL '12 days', 'VENDA'),      -- Ezio (21 é cliente ✅)
(79.90, 'CONCLUIDA', 32, 4, CURRENT_DATE - INTERVAL '5 days', 'VENDA'),       -- Chun-Li (32 é cliente ✅)

-- Aluguéis
(17.80, 'CONCLUIDA', 15, 5, CURRENT_DATE - INTERVAL '5 days', 'ALUGUEL'),     -- Sonic (15 é cliente ✅)
(6.90, 'CONCLUIDA', 11, 6, CURRENT_DATE, 'ALUGUEL'),                          -- Lara (11 é cliente ✅)
(13.80, 'CONCLUIDA', 22, 2, CURRENT_DATE - INTERVAL '6 days', 'ALUGUEL'),    -- Crash (22 é cliente ✅)
(7.90, 'CONCLUIDA', 17, 1, CURRENT_DATE - INTERVAL '1 day', 'ALUGUEL'),       -- Samus (17 é cliente ✅)
(8.00, 'CONCLUIDA', 26, 4, CURRENT_DATE - INTERVAL '10 days', 'ALUGUEL'),     -- Liu Kang (26 é cliente ✅)
(9.90, 'CONCLUIDA', 27, 3, CURRENT_DATE - INTERVAL '7 days', 'ALUGUEL'),      -- Cranky Kong (27 é cliente ✅)
(15.80, 'CONCLUIDA', 28, 1, CURRENT_DATE - INTERVAL '30 days', 'ALUGUEL'),    -- Trevor (28 é cliente ✅)
(4140.00, 'CONCLUIDA', 29, 1, CURRENT_DATE - INTERVAL '600 days', 'ALUGUEL'), -- Franklin (29 é cliente ✅)
(15.90, 'CONCLUIDA', 30, 6, CURRENT_DATE - INTERVAL '3 days', 'ALUGUEL');     -- Ryu (30 é cliente ✅)

-- Reset sequence
SELECT setval('transacao_id_seq', 20, true);


-- =========================================
-- VENDAS
-- =========================================
INSERT INTO venda (id_transacao, status, data_confirmacao) VALUES
(1, 'FINALIZADA', CURRENT_DATE - INTERVAL '15 days'),
(2, 'FINALIZADA', CURRENT_DATE - INTERVAL '20 days'),
(3, 'FINALIZADA', CURRENT_DATE - INTERVAL '8 days'),
(4, 'FINALIZADA', CURRENT_DATE - INTERVAL '12 days'),
(5, 'FINALIZADA', CURRENT_DATE - INTERVAL '5 days');


-- =========================================
-- ALUGUEIS (com id_reserva correto)
-- =========================================
INSERT INTO aluguel (id_transacao, periodo, data_devolucao, status, data_inicio, data_prevista_devolucao, id_reserva) VALUES
(6, 2, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '5 days', CURRENT_DATE - INTERVAL '3 days', NULL),
(7, 3, NULL, 'ATRASADO', CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE - INTERVAL '7 days', NULL),
(8, 3, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '3 days', CURRENT_DATE + INTERVAL '1 day', NULL),
(9, 2, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '2 days', CURRENT_DATE, NULL),
(10, 1, CURRENT_DATE - INTERVAL '6 days', 'FINALIZADO', CURRENT_DATE - INTERVAL '7 days', CURRENT_DATE - INTERVAL '6 days', NULL),
(11, 2, NULL, 'ATRASADO', CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE - INTERVAL '28 days', NULL),
(12, 2, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '2 days', CURRENT_DATE, NULL),
(13, 600, NULL, 'ATIVO', CURRENT_DATE - INTERVAL '600 days', CURRENT_DATE - INTERVAL '0 days', NULL),
(14, 1, CURRENT_DATE - INTERVAL '9 days', 'FINALIZADO', CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE - INTERVAL '9 days', NULL);


-- =========================================
-- ITENS TRANSACAO (com id_exemplar)
-- =========================================
INSERT INTO item_transacao (id_transacao, id_exemplar, valor_unitario) VALUES
(1, 8, 150.00),      -- Mario - Super Mario Bros (fisico 8)
(2, 114, 8.90),      -- Sonic - Sonic Frontiers (digital 114)
(3, 1, 9.90),        -- Snake - MGS (fisico 1)
(4, 103, 299.90),    -- Kratos - GOW (digital 103)
(5, 113, 8.90),      -- Tifa - FFVII Remake (digital 113)
(6, 115, 9.90),      -- Luigi - Mario Odyssey (digital 115)
(7, 23, 99.90),      -- Doomguy - DOOM (fisico 23)
(8, 105, 6.90),      -- Master Chief - Halo 4 (digital 105)
(9, 10, 6.90),       -- Lara - Tomb Raider (fisico 10)
(10, 24, 12.90),     -- Pyramid Head - SH2 (fisico 24)
(11, 20, 79.90),     -- Ezio - AC2 (fisico 20)
(12, 21, 6.90),      -- Crash - Crash 4 (fisico 21)
(13, 32, 6.90),      -- Franklin - NFS (fisico 32)
(14, 6, 8.00);       -- Liu Kang - Final Fight (fisico 6)


-- =========================================
-- COMPROVANTES
-- =========================================
INSERT INTO comprovante (id_transacao, tipo, codigo_rastreio, data_envio, tipo_comprovante) VALUES
(1, 'VENDA', 'TRACK-MARIO-001', CURRENT_DATE - INTERVAL '15 days', 'VENDA'),
(2, 'VENDA', 'TRACK-KRATOS-004', CURRENT_DATE - INTERVAL '20 days', 'VENDA'),
(3, 'VENDA', 'TRACK-DOOM-007', CURRENT_DATE - INTERVAL '8 days', 'VENDA'),
(4, 'VENDA', 'TRACK-EZIO-011', CURRENT_DATE - INTERVAL '12 days', 'VENDA'),
(5, 'ALUGUEL', 'TRACK-SONIC-002', CURRENT_DATE - INTERVAL '5 days', 'ALUGUEL'),
(6, 'ALUGUEL', 'TRACK-SNAKE-003', CURRENT_DATE - INTERVAL '10 days', 'ALUGUEL'),
(7, 'ALUGUEL', 'TRACK-TIFA-005', CURRENT_DATE - INTERVAL '3 days', 'ALUGUEL'),
(8, 'ALUGUEL', 'TRACK-LUIGI-006', CURRENT_DATE - INTERVAL '2 days', 'ALUGUEL'),
(9, 'ALUGUEL', 'TRACK-CHIEF-008', CURRENT_DATE - INTERVAL '1 day', 'ALUGUEL'),
(10, 'ALUGUEL', 'TRACK-LARA-009', CURRENT_DATE, 'ALUGUEL'),
(11, 'ALUGUEL', 'TRACK-PYRAMID-010', CURRENT_DATE - INTERVAL '4 days', 'ALUGUEL'),
(12, 'ALUGUEL', 'TRACK-CRASH-012', CURRENT_DATE - INTERVAL '6 days', 'ALUGUEL'),
(13, 'ALUGUEL', 'TRACK-SAMUS-013', CURRENT_DATE - INTERVAL '1 day', 'ALUGUEL'),
(14, 'ALUGUEL', 'TRACK-LIUKANG-014', CURRENT_DATE - INTERVAL '10 days', 'ALUGUEL');


-- =========================================
-- MULTAS
-- =========================================
INSERT INTO multa (id_aluguel, dias_atraso, valor, status, data_calculo) VALUES
(6, 3, 29.70, 'PENDENTE', CURRENT_DATE - INTERVAL '7 days'),
(7, 3, 38.70, 'PENDENTE', CURRENT_DATE - INTERVAL '1 day'),
(8, 2, 13.80, 'PAGO', CURRENT_DATE - INTERVAL '4 days'),
(13, 600, 237.00, 'PENDENTE', CURRENT_DATE - INTERVAL '28 days');


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
(14, 2, 'Que jogo violento! Final Fight tem muita porradaria. Na minha época, lutávamos com honra no torneio de Mortal Kombat. - Liu Kang', CURRENT_DATE - INTERVAL '9 days');