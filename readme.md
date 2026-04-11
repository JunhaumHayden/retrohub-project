# <img src="https://github.com/user-attachments/assets/61463e20-5ba3-4ce4-a632-8905ed1357b0" width="48" height="48" alt="RetroHub Logo" align="center" /> RetroHub Web
<img width="100" height="100" alt="Image" src="https://github.com/user-attachments/assets/fc997634-c093-4689-a609-a37ad21de6ed" />


![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)

[English Version](#english-version) | [Versão em Português](#versão-em-português)

---

## English Version

This is a digital platform for retro gaming enthusiasts, not only modernizing and optimizing sales, rental, and inventory processes, but also enriching the customer experience through advanced personalization, community engagement, and intelligent tools. We will implement predictive intelligence for inventory management, recommendation systems, and an ecosystem that values the passion for classic games, maintaining nostalgic authenticity through elements such as personalized rental receipts and improving operational efficiency for the team.

### 🚀 Key Features

- **Clean Architecture**: Separation of concerns using Models, Routes, and Templates.
- **Robust Data Modeling**: SQLAlchemy 2.0 ORM with comprehensive constraints and relationships.
- **Database Factory**: Modular support for PostgreSQL (Production/Docker) and SQLite (Local testing).
- **Modern UI**: Responsive Dashboard built with Bootstrap 5.
- **Dockerized**: Fully automated setup with Docker Compose.

### 🔌 API Endpoints (Current Progress)
- **Clients (CRUD)**
  - `POST /api/clientes/cadastro`: Registers a new client (Validates 18+ age, unique CPF/Email, password hashing).
  - `GET /api/clientes/`: Lists all clients.
  - `GET /api/clientes/<id>`: Retrieves a specific client.
  - `PUT /api/clientes/<id>`: Updates client data.
  - `DELETE /api/clientes/<id>`: Removes a client.

- **Employees (CRUD)**
  - `POST /api/funcionarios/`: Registers a new employee (Requires Admin via `X-Admin-Id` header, validates 18+ age, unique CPF/Email/Registration).
  - `GET /api/funcionarios/`: Lists all employees.
  - `GET /api/funcionarios/<id>`: Retrieves a specific employee.
  - `PUT /api/funcionarios/<id>`: Updates employee data (Requires Admin, prevents last admin downgrade).
  - `DELETE /api/funcionarios/<id>`: Inactivates/removes an employee (Requires Admin, prevents self-deletion).

### 🧪 Running Tests

The project includes an automated test suite utilizing an in-memory SQLite database to avoid interfering with the main PostgreSQL data.

To run all test cases (Database Connections, ORM Models, and API Routes), execute:
```bash
python -m unittest discover tests -v
```

### 📂 Project Structure

```plaintext
/project-retrohub
├── app
│   ├── __init__.py          # Application Factory
│   ├── database             # DB Adapters & Factory
│   ├── models               # SQLAlchemy Models
│   ├── routes               # Web Controllers
│   └── templates            # HTML Views (Jinja2)
├── tests                    # Test Suite
├── resources
│   └── database             # SQL Scripts (Schema)
├── docker-compose.yml       # Container Orchestration
├── Dockerfile               # App Container Definition
├── run.py                   # Entry Point
└── requirements.txt
```

---

### Class Diagram

```mermaid
classDiagram
class Usuario {
    +int id
    +char nome
    +char cpf
    +char email
    +char senha
    +date data_cadastro
    +date data_nascimento
}
class Cliente {
    +char dados_pagamento
}
class Funcionario {
    +char matricula
    +char cargo
}
class Jogo {
    +char id
    +char titulo
    +char descricao
    +char plataforma
    +boolean status
    +char genero
    +char classificacao
    +double valor_venda
    +double valor_diaria_aluguel
}
class MidiaFisica {
    +char codido_barras
    +char estado_conservacao
    +int quantidade
}
class MidiaDigital {
    +char chave_ativacao
    +date data_expiracao
}
class Venda {
    +char status
}
class Comprovante {
    +char id
    +char tipo
    +date data_emissao
    +char codigo_rastreio
}
class Multa {
    +char id
    +int dias_atraso
    +double valor
    +boolean status_pagamnento
}
class Aluguel {
    +int periodo
    +date data_devolucao
    +char status
}
class ItemTransacao {
    +int quantidade
    +int valor_unitario
}
class Avaliacao {
    +char id
    +char nota
    +char comentario
}
class Reserva {
    +char id
    +int data_reserva
    +int status
}
class Transacao {
    +char id
    +date data
    +double valor_total
}
Transacao "0..*" -- "1" Cliente
Transacao "0..*" -- "0..1" Funcionario
Transacao "1" -- "1..*" ItemTransacao
ItemTransacao "0..*" -- "1" Jogo
Comprovante "1" -- "1" Transacao
Multa "0..1" -- "1" Aluguel
Aluguel "1" -- "0..1" Reserva
Avaliacao "0..1" -- "1" Transacao
Cliente --|> Usuario
Funcionario --|> Usuario
MidiaFisica --|> Jogo
MidiaDigital --|> Jogo
Venda --|> Transacao
 Aluguel--|> Transacao
%%Generated by Astah mermaid plugin
```

---

### 🛠️ How to Run (Quick Start with Docker)

The easiest way to run the project is using Docker Compose. This will set up the Database, Web App, and PGAdmin automatically.

#### 1. Prerequisites

- Docker & Docker Compose installed.

#### 2. Run the Application

Execute the following command in the project root:

```bash
    docker-compose up --build
```

*This will build the Python image, start PostgreSQL, initialize the database schema, and launch the web server.*

#### 3. Access the Services

- **Web App:** [http://localhost:5000](http://localhost:5000)
- **PGAdmin (Database UI):** [http://localhost:5050](http://localhost:5050)
  - **Email:** `admin@retrohub.com`
  - **Password:** `admin`

---

### 🔧 How to Run (Manual / Local Development)

If you prefer to run the Python application locally (outside Docker) for debugging:

#### 1. Prerequisites

- Python 3.11+ (Conda recommended)
- PostgreSQL Database running (you can use `docker-compose up -d postgres`)

#### 2. Configure Environment

Create a `.env` file in the root directory:

```bash
    # Connection String: dialect+driver://username:password@host:port/database
    export PG_DATABASE_URL="postgresql+psycopg2://admin:admin@localhost:5432/retrohub"
```

#### 3. Install Dependencies

```bash
    conda create -n tc_generator_web python=3.11
    conda activate tc_generator_web
    pip install -r requirements.txt
```

#### 4. Run the Application

```bash
  python run.py
```

---

## Versão em Português

Esta é uma plataforma digital para entusiastas de jogos retrô, não apenas modernizando e otimizando processos de venda, aluguel e estoque, mas também enriquecendo a experiência do cliente através de personalização avançada, engajamento comunitário e ferramentas inteligentes. Implementaremos inteligência preditiva para gestão de inventário, sistemas de recomendação e um ecossistema que valoriza a paixão por jogos clássicos, mantendo a autenticidade nostálgica através de elementos como comprovantes de aluguel personalizados e aprimorando a eficiência operacional para a equipe.

### 🚀 Principais Funcionalidades

- **Arquitetura Limpa**: Separação de responsabilidades usando Models, Routes e Templates.
- **Modelagem Robusta**: ORM SQLAlchemy 2.0 com restrições e relacionamentos completos.
- **Interface Moderna**: Aplicativo responsivo.
- **Dockerizado**: Configuração automatizada com Docker Compose.

### 🔌 Endpoints da API (Progresso Atual)
- **Clientes (CRUD)**
  - `POST /api/clientes/cadastro`: Registra um novo cliente (Valida 18+, CPF/Email único e hash de senha).
  - `GET /api/clientes/`: Lista todos os clientes.
  - `GET /api/clientes/<id>`: Retorna os dados de um cliente específico.
  - `PUT /api/clientes/<id>`: Atualiza os dados cadastrais.
  - `DELETE /api/clientes/<id>`: Remove um cliente do sistema.

- **Funcionários (CRUD)**
  - `POST /api/funcionarios/`: Registra um novo funcionário (Requer Admin via header `X-Admin-Id`, valida 18+, CPF/Email/Matrícula).
  - `GET /api/funcionarios/`: Lista todos os funcionários.
  - `GET /api/funcionarios/<id>`: Retorna os dados de um funcionário específico.
  - `PUT /api/funcionarios/<id>`: Atualiza os dados cadastrais (Requer Admin, impede rebaixamento do último admin).
  - `DELETE /api/funcionarios/<id>`: Remove/inativa um funcionário (Requer Admin, impede auto-exclusão).

### 🧪 Como Rodar os Testes

O projeto conta com uma robusta bateria de testes automatizados. Eles rodam isolados utilizando um banco SQLite em memória `sqlite:///:memory:`, o que garante velocidade extrema e zero poluição no seu banco de dados principal de desenvolvimento.

Para executar todos os testes (Conexão com Banco, Mapeamento de Modelos ORM e Rotas de API), abra o terminal na raiz do projeto e rode:
```bash
python -m unittest discover tests -v
```

### 🛠️ Como Executar (Rápido com Docker)

A maneira mais fácil de rodar o projeto é usando Docker Compose. Isso configurará o Banco de Dados, a Aplicação Web e o PGAdmin automaticamente.

#### 1. Pré-requisitos

- Docker & Docker Compose instalados.

#### 2. Executar a Aplicação

Execute o seguinte comando na raiz do projeto:

```bash
docker-compose up --build
```

*Isso construirá a imagem Python, iniciará o PostgreSQL, inicializará o esquema do banco de dados e lançará o servidor web.*

#### 3. Acessar os Serviços

- **App Web:** [http://localhost:5000](http://localhost:5000)
- **PGAdmin (Interface do Banco):** [http://localhost:5050](http://localhost:5050)
  - **Email:** `admin@retrohub.com`
  - **Senha:** `admin`

---

### 🔧 Como Executar (Manual / Desenvolvimento Local)

Se preferir rodar a aplicação Python localmente (fora do Docker) para depuração:

#### 1. Pré-requisitos

- Python 3.11+ (Recomendado usar Conda)
- Banco de dados PostgreSQL rodando (você pode usar `docker-compose up -d postgres`)

#### 2. Configurar Ambiente

Crie um arquivo `.env` na raiz ou exporte as variáveis:

```bash
    # String de Conexão: dialect+driver://username:password@host:port/database
    export PG_DATABASE_URL="postgresql+psycopg2://admin:admin@localhost:5432/retrohub"
```

#### 3. Instalar Dependências

```bash
    conda create -n tc_generator_web python=3.11
    conda activate tc_generator_web
    pip install -r requirements.txt
```

#### 4. Executar a Aplicação

```bash
    python run.py
```

---

### logo

#### retro

48x48
<img width="48" height="48" alt="Image" src="https://github.com/user-attachments/assets/3d87777e-f09c-4bdc-9d7b-fec05688124a" />

100x100
<img width="100" height="100" alt="Image" src="https://github.com/user-attachments/assets/61463e20-5ba3-4ce4-a632-8905ed1357b0" />

#### Neon

48x48:

<img width="48" height="48" alt="Image" src="https://github.com/user-attachments/assets/6009e417-0221-4307-89c2-aedba5be7d12" />

100x100:

<img width="100" height="100" alt="Image" src="https://github.com/user-attachments/assets/fc997634-c093-4689-a609-a37ad21de6ed" />