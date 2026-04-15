# Configuração do Banco de Dados - RetroHub

Este diretório contém todos os scripts e configurações necessários para o banco de dados PostgreSQL do projeto RetroHub.

## Estrutura de Arquivos

A inicialização do banco de dados é controlada por dois arquivos principais, que são executados em ordem alfabética pelo contêiner do PostgreSQL na primeira vez que ele é iniciado com um volume de dados vazio.

-   `schema.sql`: Este é o arquivo principal que define a **estrutura** do banco de dados. Ele contém todos os comandos `CREATE TABLE`, `CREATE TYPE` (para ENUMs), e define as chaves primárias, chaves estrangeiras e restrições. A execução deste script garante que todas as tabelas e seus relacionamentos sejam criados corretamente. (Atualizado para a arquitetura Catálogo/Exemplar).

-   `data.sql`: Após a criação da estrutura pelo `schema.sql`, este arquivo é executado para **popular** o banco de dados com dados iniciais de demonstração. Ele contém uma série de comandos `INSERT` que adicionam exemplos de usuários, clientes, funcionários, catálogo de jogos, exemplares e transações.

-   `servers.json`: Este arquivo é usado para pré-configurar a conexão com o banco de dados no **PGAdmin**. Ele informa ao PGAdmin como se conectar ao contêiner do PostgreSQL da RetroHub, para que o servidor já apareça listado na interface, simplificando o acesso durante o desenvolvimento.

## Diagrama Entidade-Relacionamento (ER)

O diagrama abaixo ilustra as principais entidades do banco de dados e como elas se relacionam (agora incluindo o modelo Catálogo vs Inventário com a entidade `Exemplar`).

```mermaid
erDiagram
    usuario ||--o| cliente : "herda"
    usuario ||--o| funcionario : "herda"

    cliente }o--o{ transacao : "realiza"
    cliente }o--o{ reserva : "faz"

    funcionario }o--o{ transacao : "registra"

    jogo ||--o{ exemplar : "possui"
    exemplar ||--o| midia_fisica : "herda"
    exemplar ||--o| midia_digital : "herda"

    exemplar ||--o{ item_transacao : "é item de"
    jogo ||--o{ reserva : "é reservado em"

    transacao ||--o| venda : "herda"
    transacao ||--o| aluguel : "herda"
    transacao ||--|{ item_transacao : "contém"
    transacao ||--o| comprovante : "gera"
    transacao ||--o| avaliacao : "pode ter"

    aluguel ||--o| multa : "pode gerar"

    reserva ||--o| aluguel : "é convertida em"

    usuario {
        int id PK
        string nome
        string cpf
        string email
        string senha
        date data_cadastro
        date data_nascimento
    }
    cliente {
        int id_usuario PK, FK
        string dados_pagamento
        string tipo_cliente
    }
    funcionario {
        int id_usuario PK, FK
        string matricula
        string cargo
        string setor
        date data_admissao
    }
    jogo {
        int id PK
        string titulo
        string descricao
        string plataforma
        boolean ativo
        string genero
        string classificacao
        decimal valor_venda
        decimal valor_diaria_aluguel
    }
    exemplar {
        int id PK
        int id_jogo FK
        string tipo_midia
    }
    midia_fisica {
        int id_exemplar PK, FK
        string codigo_barras
        string estado_conservacao
    }
    midia_digital {
        int id_exemplar PK, FK
        string chave_ativacao
        date data_expiracao
    }
    transacao {
        int id PK
        datetime data_transacao
        decimal valor_total
        string status
        int id_cliente FK
        int id_funcionario FK
    }
    venda {
        int id_transacao PK, FK
        string status
        date data_confirmacao
    }
    aluguel {
        int id_transacao PK, FK
        int periodo
        date data_devolucao
        date data_inicio
        date data_prevista_devolucao
        string status
        int id_reserva FK
    }
    item_transacao {
        int id PK
        int id_transacao FK
        int id_exemplar FK
        decimal valor_unitario
    }
    comprovante {
        int id PK
        int id_transacao FK
        string tipo
        datetime data_envio
        string codigo_rastreio
    }
    multa {
        int id PK
        int id_aluguel FK
        int dias_atraso
        decimal valor
        string status
        date data_calculo
    }
    avaliacao {
        int id PK
        int id_transacao FK
        int nota
        string comentario
        date data_avaliacao
    }
    reserva {
        int id PK
        int id_cliente FK
        int id_jogo FK
        date data_reserva
        date data_expiracao
        string status
    }
```


### Atualizaçao do modelo
```mermaid
erDiagram
    USUARIO {
        SERIAL id PK
        VARCHAR nome
        VARCHAR cpf UK
        VARCHAR email UK
        VARCHAR senha
        DATE data_cadastro
        DATE data_nascimento
        VARCHAR tipo "cliente|funcionario"
    }

    FUNCIONARIO {
        INTEGER id_usuario PK,FK
        VARCHAR matricula UK
        VARCHAR cargo
        VARCHAR setor
        DATE data_admissao
    }

    CLIENTE {
        INTEGER id_usuario PK,FK
        VARCHAR dados_pagamento
        VARCHAR tipo_cliente "REGULAR|PREMIUM"
    }

    CATALOGO {
        SERIAL id PK
        VARCHAR titulo
        TEXT descricao
        VARCHAR plataforma
        BOOLEAN ativo
        VARCHAR genero
        VARCHAR classificacao
        NUMERIC valor_venda
        NUMERIC valor_diaria_aluguel
    }

    EXEMPLAR {
        SERIAL id PK
        INTEGER id_catalogo FK
        VARCHAR tipo_midia "FISICA|DIGITAL"
    }

    MIDIA_FISICA {
        INTEGER id_exemplar PK,FK
        VARCHAR codigo_barras UK
        VARCHAR estado_conservacao
    }

    MIDIA_DIGITAL {
        INTEGER id_exemplar PK,FK
        VARCHAR chave_ativacao UK
        DATE data_expiracao
    }

    RESERVA {
        SERIAL id PK
        INTEGER id_cliente FK
        INTEGER id_catalogo FK
        DATE data_reserva
        VARCHAR status
        DATE data_expiracao
    }

    TRANSACAO {
        SERIAL id PK
        TIMESTAMP data_transacao
        NUMERIC valor_total
        VARCHAR pagamento
        VARCHAR status
        INTEGER id_cliente FK
        INTEGER id_funcionario FK
        VARCHAR tipo "VENDA|ALUGUEL"
    }

    VENDA {
        INTEGER id_transacao PK,FK
        VARCHAR status
        DATE data_confirmacao
    }

    ALUGUEL {
        INTEGER id_transacao PK,FK
        INTEGER periodo
        DATE data_devolucao
        VARCHAR status
        INTEGER id_reserva FK
        DATE data_inicio
        DATE data_prevista_devolucao
    }

    ITEM_TRANSACAO {
        SERIAL id PK
        INTEGER id_transacao FK
        INTEGER id_exemplar FK
        NUMERIC valor_unitario
    }

    COMPROVANTE {
        SERIAL id PK
        INTEGER id_transacao FK
        VARCHAR tipo
        TIMESTAMP data_envio
        VARCHAR tipo_comprovante
        VARCHAR codigo_rastreio
    }

    MULTA {
        SERIAL id PK
        INTEGER id_aluguel FK
        INTEGER dias_atraso
        NUMERIC valor
        VARCHAR status
        DATE data_calculo
    }

    AVALIACAO {
        SERIAL id PK
        INTEGER id_transacao FK
        INTEGER nota "1 a 5"
        TEXT comentario
        DATE data_avaliacao
    }

    %% Relacionamentos
    USUARIO ||--o| FUNCIONARIO : "id_usuario"
    USUARIO ||--o| CLIENTE : "id_usuario"

    CATALOGO ||--o{ EXEMPLAR : "id_catalogo"
    EXEMPLAR ||--o| MIDIA_FISICA : "id_exemplar"
    EXEMPLAR ||--o| MIDIA_DIGITAL : "id_exemplar"

    CLIENTE ||--o{ RESERVA : "id_cliente"
    CATALOGO ||--o{ RESERVA : "id_catalogo"

    CLIENTE ||--o{ TRANSACAO : "id_cliente"
    FUNCIONARIO ||--o{ TRANSACAO : "id_funcionario"

    TRANSACAO ||--o| VENDA : "id_transacao"
    TRANSACAO ||--o| ALUGUEL : "id_transacao"

    TRANSACAO ||--o{ ITEM_TRANSACAO : "id_transacao"
    EXEMPLAR ||--o{ ITEM_TRANSACAO : "id_exemplar"

    TRANSACAO ||--o{ COMPROVANTE : "id_transacao"
    TRANSACAO ||--o{ AVALIACAO : "id_transacao"

    ALUGUEL ||--o{ MULTA : "id_aluguel"
    RESERVA ||--o| ALUGUEL : "id_reserva"
```

## Principais Características do Modelo

Herança com Polimorfismo

USUARIO se especializa em CLIENTE ou FUNCIONARIO via campo tipo
EXEMPLAR se especializa em MIDIA_FISICA ou MIDIA_DIGITAL via tipo_midia
Catálogo vs Estoque

CATALOGO representa a vitrine (produto)
EXEMPLAR representa cópias físicas/digitais (estoque)
Transações Polimórficas

TRANSACAO se especializa em VENDA ou ALUGUEL via campo tipo
Rastreabilidade Completa

ITEM_TRANSACAO vincula cada transação a um exemplar específico
COMPROVANTE documenta cada operação
AVALIACAO permite feedback pós-transação
Regras de Negócio

MULTA vinculada a aluguéis atrasados
RESERVA pode se converter em ALUGUEL
CLIENTE tem tipo (REGULAR/PREMIUM) para regras diferenciadas

## Como Funciona a Inicialização

Ao executar `docker-compose up` pela primeira vez:
1.  O Docker cria um volume para o PostgreSQL no diretório `resources/database/postgre`.
2.  Como o volume está vazio, o contêiner do PostgreSQL executa os scripts do diretório `/docker-entrypoint-initdb.d`.
3.  Nosso `docker-compose.yml` mapeia o `schema.sql` e o `data.sql` para este diretório.
4.  O PostgreSQL executa `schema.sql` primeiro (criando as tabelas e os ENUMs) e depois `data.sql` (populando-as com os Easter Eggs e catálogos).
5.  Em todas as inicializações futuras, como o volume de dados não estará mais vazio, esses scripts de inicialização são ignorados, preservando os dados existentes.

