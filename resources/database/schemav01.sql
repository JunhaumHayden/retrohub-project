-- Drop existing tables to start fresh
DROP TABLE IF EXISTS transacao, item_transacao, comprovante, multa, aluguel, reserva, avaliacao, midia_fisica, midia_digital, jogo, cliente, funcionario, usuario CASCADE;

-- Tabela Usuario
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    data_cadastro DATE DEFAULT CURRENT_DATE,
    data_nascimento DATE
);

-- Tabela Cliente
CREATE TABLE cliente (
    id_usuario INTEGER PRIMARY KEY REFERENCES usuario(id),
    dados_pagamento VARCHAR(255)
);

-- Tabela Funcionario
CREATE TABLE funcionario (
    id_usuario INTEGER PRIMARY KEY REFERENCES usuario(id),
    matricula VARCHAR(50) NOT NULL UNIQUE,
    cargo VARCHAR(100)
);

-- Tabela Jogo
CREATE TABLE jogo (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT,
    plataforma VARCHAR(100),
    status BOOLEAN DEFAULT true,
    genero VARCHAR(100),
    classificacao VARCHAR(50),
    valor_venda NUMERIC(10, 2),
    valor_diaria_aluguel NUMERIC(10, 2)
);

-- Tabela MidiaFisica (herda de Jogo)
CREATE TABLE midia_fisica (
    id_jogo INTEGER PRIMARY KEY REFERENCES jogo(id),
    codigo_barras VARCHAR(255) UNIQUE,
    estado_conservacao VARCHAR(100),
    quantidade INTEGER DEFAULT 1
);

-- Tabela MidiaDigital (herda de Jogo)
CREATE TABLE midia_digital (
    id_jogo INTEGER PRIMARY KEY REFERENCES jogo(id),
    chave_ativacao VARCHAR(255) UNIQUE,
    data_expiracao DATE
);

-- Tabela Transacao
CREATE TABLE transacao (
    id SERIAL PRIMARY KEY,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valor_total NUMERIC(10, 2),
    id_cliente INTEGER REFERENCES cliente(id_usuario),
    id_funcionario INTEGER REFERENCES funcionario(id_usuario)
);

-- Tabela Venda (herda de Transacao)
CREATE TABLE venda (
    id_transacao INTEGER PRIMARY KEY REFERENCES transacao(id),
    status VARCHAR(100)
);

-- Tabela Aluguel (herda de Transacao)
CREATE TABLE aluguel (
    id_transacao INTEGER PRIMARY KEY REFERENCES transacao(id),
    periodo INTEGER,
    data_devolucao DATE,
    status VARCHAR(100)
);

-- Tabela ItemTransacao
CREATE TABLE item_transacao (
    id SERIAL PRIMARY KEY,
    id_transacao INTEGER REFERENCES transacao(id),
    id_jogo INTEGER REFERENCES jogo(id),
    quantidade INTEGER,
    valor_unitario NUMERIC(10, 2)
);

-- Tabela Comprovante
CREATE TABLE comprovante (
    id SERIAL PRIMARY KEY,
    id_transacao INTEGER REFERENCES transacao(id),
    tipo VARCHAR(100),
    data_emissao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    codigo_rastreio VARCHAR(255)
);

-- Tabela Multa
CREATE TABLE multa (
    id SERIAL PRIMARY KEY,
    id_aluguel INTEGER REFERENCES aluguel(id_transacao),
    dias_atraso INTEGER,
    valor NUMERIC(10, 2),
    status_pagamento BOOLEAN DEFAULT false
);

-- Tabela Avaliacao
CREATE TABLE avaliacao (
    id SERIAL PRIMARY KEY,
    id_transacao INTEGER REFERENCES transacao(id),
    nota INTEGER,
    comentario TEXT
);

-- Tabela Reserva
CREATE TABLE reserva (
    id SERIAL PRIMARY KEY,
    id_cliente INTEGER REFERENCES cliente(id_usuario),
    id_jogo INTEGER REFERENCES jogo(id),
    data_reserva DATE,
    status VARCHAR(100)
);

-- Relacionamentos que não foram modelados como herança ou FK direta
-- Aluguel "1" -- "0..1" Reserva (Um aluguel pode vir de uma reserva)
ALTER TABLE aluguel ADD COLUMN id_reserva INTEGER REFERENCES reserva(id);

