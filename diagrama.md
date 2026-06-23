erDiagram
  aluguel {
    INTEGER id_transacao PK,FK
    INTEGER id_reserva FK "nullable"
    DATE data_devolucao "nullable"
    DATE data_inicio "nullable"
    DATE data_prevista_devolucao "nullable"
    INTEGER periodo "nullable"
    VARCHAR status "nullable"
  }

  avaliacao {
    INTEGER id PK
    INTEGER id_transacao FK "nullable"
    TEXT comentario "nullable"
    DATE data_avaliacao "nullable"
    INTEGER nota "nullable"
  }

  cliente {
    INTEGER id_usuario PK,FK
    VARCHAR(255) dados_pagamento "nullable"
    DATE data_cadastro "nullable"
    VARCHAR(50) tipo_cliente "nullable"
  }

  comprovante {
    INTEGER id PK
    INTEGER id_transacao FK "nullable"
    VARCHAR(255) codigo_rastreio "nullable"
    DATETIME data_envio "nullable"
    VARCHAR tipo "nullable"
  }

  exemplar {
    INTEGER id PK
    INTEGER id_jogo FK
    VARCHAR(50) tipo_midia
  }

  funcionario {
    INTEGER id_usuario PK,FK
    VARCHAR(100) cargo "nullable"
    DATE data_admissao "nullable"
    VARCHAR(50) matricula UK
    VARCHAR(100) setor "nullable"
  }

  item_transacao {
    INTEGER id PK
    INTEGER id_exemplar FK "nullable"
    INTEGER id_transacao FK "nullable"
    NUMERIC(10-2) valor_unitario "nullable"
  }

  jogo {
    INTEGER id PK
    BOOLEAN ativo "nullable"
    VARCHAR(50) classificacao "nullable"
    TEXT descricao "nullable"
    VARCHAR(100) genero "nullable"
    VARCHAR(100) plataforma "nullable"
    VARCHAR(255) titulo
    NUMERIC(10-2) valor_diaria_aluguel "nullable"
    NUMERIC(10-2) valor_venda "nullable"
  }

  midia_digital {
    INTEGER id_exemplar PK,FK
    VARCHAR(255) chave_ativacao UK
    DATE data_expiracao "nullable"
  }

  midia_fisica {
    INTEGER id_exemplar PK,FK
    VARCHAR(255) codigo_barras UK
    VARCHAR(100) estado_conservacao "nullable"
  }

  multa {
    INTEGER id PK
    INTEGER id_aluguel FK "nullable"
    DATE data_calculo "nullable"
    INTEGER dias_atraso "nullable"
    VARCHAR status "nullable"
    NUMERIC(10-2) valor "nullable"
  }

  reserva {
    INTEGER id PK
    INTEGER id_cliente FK "nullable"
    INTEGER id_jogo FK "nullable"
    DATE data_expiracao "nullable"
    DATE data_reserva "nullable"
    VARCHAR status "nullable"
  }

  transacao {
    INTEGER id PK
    INTEGER id_cliente FK "nullable"
    INTEGER id_funcionario FK "nullable"
    DATETIME data_transacao "nullable"
    VARCHAR status "nullable"
    NUMERIC(10-2) valor_total "nullable"
  }

  usuario {
    INTEGER id PK
    VARCHAR(14) cpf UK
    DATE data_cadastro "nullable"
    DATE data_nascimento "nullable"
    VARCHAR(255) email UK
    VARCHAR(255) nome
    VARCHAR(255) senha
  }

  venda {
    INTEGER id_transacao PK,FK
    DATE data_confirmacao "nullable"
    VARCHAR status "nullable"
  }

  transacao ||--o| aluguel : id_transacao
  reserva ||--o{ aluguel : id_reserva
  transacao ||--o{ avaliacao : id_transacao
  usuario ||--o| cliente : id_usuario
  transacao ||--o{ comprovante : id_transacao
  jogo ||--o{ exemplar : id_jogo
  usuario ||--o| funcionario : id_usuario
  transacao ||--o{ item_transacao : id_transacao
  exemplar ||--o{ item_transacao : id_exemplar
  exemplar ||--o| midia_digital : id_exemplar
  exemplar ||--o| midia_fisica : id_exemplar
  aluguel ||--o{ multa : id_aluguel
  cliente ||--o{ reserva : id_cliente
  jogo ||--o{ reserva : id_jogo
  cliente ||--o{ transacao : id_cliente
  funcionario ||--o{ transacao : id_funcionario
  transacao ||--o| venda : id_transacao
