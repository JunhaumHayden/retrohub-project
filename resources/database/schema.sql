-- ================================
-- RESET
-- ================================
DROP TABLE IF EXISTS transacao, item_transacao, comprovante, multa, aluguel, venda, reserva, avaliacao, midia_fisica, midia_digital, exemplar, jogo, cliente, funcionario, usuario CASCADE;

DROP TYPE IF EXISTS status_transacao_enum, status_venda_enum, status_aluguel_enum, status_reserva_enum, status_pagamento_enum, tipo_comprovante_enum, tipo_cliente_enum CASCADE;

-- ================================
-- ENUMS
-- ================================

CREATE TYPE status_transacao_enum AS ENUM ('PENDENTE', 'CONCLUIDA', 'CANCELADA');
CREATE TYPE status_venda_enum AS ENUM ('FINALIZADA', 'ESTORNADA');
CREATE TYPE status_aluguel_enum AS ENUM ('ATIVO', 'FINALIZADO', 'ATRASADO');
CREATE TYPE status_reserva_enum AS ENUM ('ATIVA', 'CANCELADA', 'EXPIRADA', 'CONVERTIDA');
CREATE TYPE status_pagamento_enum AS ENUM ('PENDENTE', 'PAGO');
CREATE TYPE tipo_comprovante_enum AS ENUM ('VENDA', 'ALUGUEL');
CREATE TYPE tipo_cliente_enum AS ENUM ('regular', 'premium');

-- ================================
-- USUARIO
-- ================================

CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    data_cadastro DATE DEFAULT CURRENT_DATE,
    data_nascimento DATE
);

-- ================================
-- CLIENTE / FUNCIONARIO
-- ================================

CREATE TABLE cliente (
    id_usuario INTEGER PRIMARY KEY REFERENCES usuario(id) ON DELETE CASCADE,
    dados_pagamento VARCHAR(255),
    data_cadastro DATE DEFAULT CURRENT_DATE,
    tipo_cliente tipo_cliente_enum DEFAULT 'regular'
);

CREATE TABLE funcionario (
    id_usuario INTEGER PRIMARY KEY REFERENCES usuario(id) ON DELETE CASCADE,
    matricula VARCHAR(50) NOT NULL UNIQUE,
    cargo VARCHAR(100),
    setor VARCHAR(100),
    data_admissao DATE
);

-- ================================
-- JOGO (CATÁLOGO / VITRINE)
-- ================================

CREATE TABLE jogo (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT,
    plataforma VARCHAR(100),
    ativo BOOLEAN DEFAULT TRUE,
    genero VARCHAR(100),
    classificacao VARCHAR(50),
    valor_venda NUMERIC(10,2) CHECK (valor_venda >= 0),
    valor_diaria_aluguel NUMERIC(10,2) CHECK (valor_diaria_aluguel >= 0),
    UNIQUE (titulo, plataforma)
);

-- ================================
-- EXEMPLARES (1 Jogo -> N Exemplares)
-- ================================

CREATE TABLE exemplar (
    id SERIAL PRIMARY KEY,
    id_jogo INTEGER REFERENCES jogo(id) ON DELETE CASCADE,
    tipo_midia VARCHAR(50) NOT NULL
);

CREATE TABLE midia_fisica (
    id_exemplar INTEGER PRIMARY KEY REFERENCES exemplar(id) ON DELETE CASCADE,
    codigo_barras VARCHAR(255) UNIQUE NOT NULL,
    estado_conservacao VARCHAR(100)
);

CREATE TABLE midia_digital (
    id_exemplar INTEGER PRIMARY KEY REFERENCES exemplar(id) ON DELETE CASCADE,
    chave_ativacao VARCHAR(255) UNIQUE NOT NULL,
    data_expiracao DATE
);

-- ================================
-- TRANSACAO
-- ================================

CREATE TABLE transacao (
    id SERIAL PRIMARY KEY,
    data_transacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valor_total NUMERIC(10,2) CHECK (valor_total >= 0),
    status status_transacao_enum DEFAULT 'PENDENTE',
    id_cliente INTEGER REFERENCES cliente(id_usuario),
    id_funcionario INTEGER REFERENCES funcionario(id_usuario)
);

-- ================================
-- VENDA / ALUGUEL
-- ================================

CREATE TABLE venda (
    id_transacao INTEGER PRIMARY KEY REFERENCES transacao(id) ON DELETE CASCADE,
    status status_venda_enum DEFAULT 'FINALIZADA',
    data_confirmacao DATE
);

-- ================================
-- RESERVA
-- ================================

CREATE TABLE reserva (
    id SERIAL PRIMARY KEY,
    id_cliente INTEGER REFERENCES cliente(id_usuario),
    id_jogo INTEGER REFERENCES jogo(id),  -- Reserva é feita no catálogo, o exemplar é definido na locação
    data_reserva DATE DEFAULT CURRENT_DATE,
    status status_reserva_enum DEFAULT 'ATIVA',
    data_expiracao DATE
);

CREATE TABLE aluguel (
    id_transacao INTEGER PRIMARY KEY REFERENCES transacao(id) ON DELETE CASCADE,
    periodo INTEGER CHECK (periodo > 0),
    data_devolucao DATE,
    status status_aluguel_enum DEFAULT 'ATIVO',
    id_reserva INTEGER REFERENCES reserva(id),
    data_inicio DATE,
    data_prevista_devolucao DATE
);


-- ================================
-- ITEM TRANSACAO
-- ================================

CREATE TABLE item_transacao (
    id SERIAL PRIMARY KEY,
    id_transacao INTEGER REFERENCES transacao(id) ON DELETE CASCADE,
    id_exemplar INTEGER REFERENCES exemplar(id), -- Agora aponta para o exemplar específico!
    valor_unitario NUMERIC(10,2) CHECK (valor_unitario >= 0)
);

-- ================================
-- COMPROVANTE
-- ================================

CREATE TABLE comprovante (
    id SERIAL PRIMARY KEY,
    id_transacao INTEGER REFERENCES transacao(id) ON DELETE CASCADE,
    tipo tipo_comprovante_enum,
    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    codigo_rastreio VARCHAR(255)
);

-- ================================
-- MULTA
-- ================================

CREATE TABLE multa (
    id SERIAL PRIMARY KEY,
    id_aluguel INTEGER REFERENCES aluguel(id_transacao),
    dias_atraso INTEGER CHECK (dias_atraso > 0),
    valor NUMERIC(10,2) CHECK (valor >= 0),
    status status_pagamento_enum DEFAULT 'PENDENTE',
    data_calculo DATE
);

-- ================================
-- AVALIACAO
-- ================================

CREATE TABLE avaliacao (
    id SERIAL PRIMARY KEY,
    id_transacao INTEGER REFERENCES transacao(id) ON DELETE CASCADE,
    nota INTEGER CHECK (nota BETWEEN 1 AND 5),
    comentario TEXT,
    data_avaliacao DATE
);
