# Configuração do Banco de Dados - RetroHub

Este diretório contém todos os scripts e configurações necessários para o banco de dados PostgreSQL do projeto RetroHub.

## Estrutura de Arquivos

A inicialização do banco de dados é controlada por dois arquivos principais, que são executados em ordem alfabética pelo contêiner do PostgreSQL na primeira vez que ele é iniciado com um volume de dados vazio.

-   `schema.sql`: Este é o arquivo principal que define a **estrutura** do banco de dados. Ele contém todos os comandos `CREATE TABLE`, `CREATE TYPE` (para ENUMs), e define as chaves primárias, chaves estrangeiras e restrições. A execução deste script garante que todas as tabelas e seus relacionamentos sejam criados corretamente. (Atualizado para a arquitetura Catálogo/Exemplar).

-   `02_data.sql`: Após a criação da estrutura pelo `schema.sql`, este arquivo é executado para **popular** o banco de dados com dados iniciais de demonstração. Ele contém uma série de comandos `INSERT` que adicionam exemplos de usuários, clientes, funcionários, catálogo de jogos, exemplares e transações.

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

## Como Funciona a Inicialização

Ao executar `docker-compose up` pela primeira vez:
1.  O Docker cria um volume para o PostgreSQL no diretório `resources/database/postgre`.
2.  Como o volume está vazio, o contêiner do PostgreSQL executa os scripts do diretório `/docker-entrypoint-initdb.d`.
3.  Nosso `docker-compose.yml` mapeia o `schema.sql` e o `02_data.sql` para este diretório.
4.  O PostgreSQL executa `schema.sql` primeiro (criando as tabelas e os ENUMs) e depois `02_data.sql` (populando-as com os Easter Eggs e catálogos).
5.  Em todas as inicializações futuras, como o volume de dados não estará mais vazio, esses scripts de inicialização são ignorados, preservando os dados existentes.

