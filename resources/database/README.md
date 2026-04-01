# Configuração do Banco de Dados - RetroHub

Este diretório contém todos os scripts e configurações necessários para o banco de dados PostgreSQL do projeto RetroHub.

## Estrutura de Arquivos

A inicialização do banco de dados é controlada por dois arquivos principais, que são executados em ordem alfabética pelo contêiner do PostgreSQL na primeira vez que ele é iniciado com um volume de dados vazio.

-   `schema.sql`: Este é o arquivo principal que define a **estrutura** do banco de dados. Ele contém todos os comandos `CREATE TABLE`, `CREATE TYPE` (para ENUMs), e define as chaves primárias, chaves estrangeiras e restrições. A execução deste script garante que todas as tabelas e seus relacionamentos sejam criados corretamente.

-   `02_data.sql`: Após a criação da estrutura pelo `schema.sql`, este arquivo é executado para **popular** o banco de dados com dados iniciais de demonstração. Ele contém uma série de comandos `INSERT` que adicionam exemplos de usuários, clientes, funcionários, jogos e transações. Isso é extremamente útil para ter um ambiente de desenvolvimento funcional sem a necessidade de cadastrar tudo manualmente.

-   `servers.json`: Este arquivo é usado para pré-configurar a conexão com o banco de dados no **PGAdmin**. Ele informa ao PGAdmin como se conectar ao contêiner do PostgreSQL da RetroHub, para que o servidor já apareça listado na interface, simplificando o acesso durante o desenvolvimento.

## Diagrama Entidade-Relacionamento (ER)

O diagrama abaixo ilustra as principais entidades do banco de dados e como elas se relacionam.

```mermaid
erDiagram

    USUARIO {
        int id PK
        string nome
        string cpf
        string email
        string senha
        date data_cadastro
        date data_nascimento
    }

    CLIENTE {
        int id_usuario PK, FK
        string dados_pagamento
    }

    FUNCIONARIO {
        int id_usuario PK, FK
        string matricula
        string cargo
    }

    JOGO {
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

    MIDIA_FISICA {
        int id_jogo PK, FK
        string codigo_barras
        string estado_conservacao
        int quantidade
    }

    MIDIA_DIGITAL {
        int id_jogo PK, FK
        string chave_ativacao
        date data_expiracao
    }

    TRANSACAO {
        int id PK
        datetime data
        decimal valor_total
        string status
        int id_cliente FK
        int id_funcionario FK
    }

    VENDA {
        int id_transacao PK, FK
        string status
    }

    ALUGUEL {
        int id_transacao PK, FK
        int periodo
        date data_devolucao
        string status
        int id_reserva FK
    }

    ITEM_TRANSACAO {
        int id PK
        int id_transacao FK
        int id_jogo FK
        int quantidade
        decimal valor_unitario
    }

    COMPROVANTE {
        int id PK
        int id_transacao FK
        string tipo
        datetime data_emissao
        string codigo_rastreio
    }

    MULTA {
        int id PK
        int id_aluguel FK
        int dias_atraso
        decimal valor
        string status
    }

    AVALIACAO {
        int id PK
        int id_transacao FK
        int nota
        string comentario
    }

    RESERVA {
        int id PK
        int id_cliente FK
        int id_jogo FK
        date data_reserva
        string status
    }

    %% RELACIONAMENTOS

    USUARIO ||--|| CLIENTE : "is"
    USUARIO ||--|| FUNCIONARIO : "is"

    CLIENTE ||--o{ TRANSACAO : "realiza"
    FUNCIONARIO ||--o{ TRANSACAO : "processa"

    TRANSACAO ||--|| VENDA : "pode ser"
    TRANSACAO ||--|| ALUGUEL : "pode ser"

    TRANSACAO ||--o{ ITEM_TRANSACAO : "possui"
    JOGO ||--o{ ITEM_TRANSACAO : "referenciado em"

    TRANSACAO ||--o{ COMPROVANTE : "gera"
    TRANSACAO ||--o{ AVALIACAO : "recebe"

    ALUGUEL ||--o| MULTA : "pode gerar"

    CLIENTE ||--o{ RESERVA : "faz"
    JOGO ||--o{ RESERVA : "reservado"

    RESERVA ||--o| ALUGUEL : "origina"

    JOGO ||--|| MIDIA_FISICA : "pode ser"
    JOGO ||--|| MIDIA_DIGITAL : "pode ser"
```

## Como Funciona a Inicialização

Ao executar `docker-compose up` pela primeira vez:
1.  O Docker cria um volume para o PostgreSQL no diretório `resources/database/postgre`.
2.  Como o volume está vazio, o contêiner do PostgreSQL executa os scripts do diretório `/docker-entrypoint-initdb.d`.
3.  Nosso `docker-compose.yml` mapeia o `schema.sql` e o `02_data.sql` para este diretório.
4.  O PostgreSQL executa `schema.sql` primeiro (criando as tabelas) e depois `02_data.sql` (populando-as).
5.  Em todas as inicializações futuras, como o volume de dados não estará mais vazio, esses scripts de inicialização são ignorados, preservando os dados existentes.
