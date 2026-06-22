<div align="center">
<p align="center">
  <img src="http://img.shields.io/static/v1?label=STATUS&message=Em%20Desenvolvimento&color=brightgreen&style=for-the-badge"/>
</p>

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)
![SQLite](https://img.shields.io/badge/SQLite-Local-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/license/mit/)
</div>

---

# RetroHub API

Esta é uma plataforma digital para entusiastas de jogos retrô, desenvolvida para modernizar e otimizar os processos de venda, aluguel e gestão de estoque de mídias físicas e digitais. A plataforma é construída sobre uma arquitetura limpa e robusta, focada em boas práticas de Engenharia de Software.

### 🚀 Principais Funcionalidades e Arquitetura

- **Arquitetura Limpa e em Camadas**: O projeto adota uma estrita separação de responsabilidades (SOLID):
  - **Rotas (Controllers)**: Camada fina que apenas recebe requisições HTTP e retorna respostas (JSON), utilizando `Flask-RestX` e Swagger.
  - **Serviços**: Concentram toda a lógica de negócio, orquestrando as operações sem se preocupar com como os dados são salvos.
  - **Repositórios**: Abstraem o acesso ao banco de dados através de interfaces.
  - **Modelos**: Entidades ORM puras mapeadas com `SQLAlchemy 2.0`.
- **Injeção de Dependência (DI)**: Utilização de um `Container` centralizado para injetar dependências (Repositórios nos Serviços), garantindo baixo acoplamento.
- **Factory de Banco de Dados**: O `DatabaseFactory` permite alternar entre `Mock` (memória), `SQLite` (arquivos locais) e `PostgreSQL` (produção/Docker) mudando apenas uma variável de ambiente.
- **Design Patterns Aplicados**:
  - Padrão **State** para gerenciar o ciclo de vida complexo de um Aluguel (Solicitado -> Aprovado -> Ativo -> Finalizado/Atrasado).
  - Padrão **Catálogo vs. Inventário**: Separação clara entre a vitrine (Catalogo) e os itens físicos/digitais reais no estoque (Exemplares).
- **Dockerizado**: Configuração automatizada com Docker Compose.

---

### 🔌 API Endpoints (Swagger UI)

A documentação completa e interativa da API está disponível via **Swagger UI**. Após iniciar o projeto, acesse:

👉 **[http://localhost:5000/docs](http://localhost:5000/docs)**

Lá você poderá testar todas as rotas diretamente do navegador, incluindo operações de CRUD para:
- `Clientes` e `Funcionários`
- `Catálogo` de Jogos
- `Estoque` (Mídias Físicas e Digitais)
- `Transações` (Vendas e Aluguéis)
- `Avaliações`
- `Relatórios` gerenciais

*(Dica: Algumas rotas exigem a passagem do header `X-Funcionario-Id` ou `X-Cliente-Id`, conforme detalhado no Swagger).*

---

### 🛠️ Como Configurar e Executar

A arquitetura do RetroHub permite que você o execute com diferentes bancos de dados. Recomendamos o uso do **SQLite** para desenvolvimento local simplificado ou **Docker** para um ambiente completo.

#### 1. Configurando o Ambiente (`.env`)

Crie um arquivo `.env` na raiz do projeto com as seguintes configurações:

```bash
# Define o banco de dados a ser usado: sqlite, postgre ou mock
APP_MODE=sqlite

# Configuração para SQLite (os dados serão salvos em /resources/database/sqlite/app.db)
SQLITE_DATABASE_URL=sqlite:///resources/database/sqlite/app.db

# Configuração para PostgreSQL (se estiver usando Docker)
DB_USER=admin
DB_PASSWORD=admin
DB_NAME=retrohub
PG_DATABASE_URL=postgresql+psycopg2://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
```

#### 2. Inicializando o Banco de Dados (Para SQLite Local)

Se você escolheu `APP_MODE=sqlite`, execute o script de inicialização para criar o arquivo de banco de dados e as tabelas:

```bash
python init_db.py
```
*(Certifique-se de que a pasta `resources/database/sqlite/` existe na raiz do projeto).*

#### 3. Executando (Opção A: Rápido com Docker)

A maneira mais robusta é usar o Docker Compose, que subirá a API, o banco PostgreSQL (se configurado) e o PGAdmin:

```bash
docker-compose up --build
```
- Acesse a API e o Swagger em: `http://localhost:5000/docs`

*(Nota: O Docker Compose está configurado para mapear a pasta local `./resources` para dentro do contêiner, garantindo a persistência do seu SQLite local, se esta for a sua escolha em `APP_MODE`).*

#### 4. Executando (Opção B: Manual / Desenvolvimento Local)

1. Crie um ambiente virtual (Conda recomendado):
   ```bash
   conda create -n retrohub python=3.11
   conda activate retrohub
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Inicie o servidor Flask:
   ```bash
   python run.py
   ```

---

### 🧪 Como Rodar os Testes

O projeto conta com uma robusta bateria de testes automatizados unitários e de integração, garantindo o funcionamento desde a camada de domínio (modelos) até a orquestração dos serviços no banco de dados.

Os testes utilizam o framework **Pytest** e são configurados para rodar de forma isolada, criando e destruindo um banco de dados SQLite em memória (`sqlite:///:memory:`) para cada teste, garantindo máxima confiabilidade.

Para executar todos os testes, rode no terminal:

```bash
pytest -v
```

---
### Diagramas

- [Diagrama de Classe](classDiagram.md) 

## Logo

<table table align="center" cellspacing="20">
    <tr align="center"><h3>Retro</h3></tr>
    <tr>
        <td align="center">
            <a> <img width="48" height="48" alt="Image" src="https://github.com/user-attachments/assets/3d87777e-f09c-4bdc-9d7b-fec05688124a" /><br> <sub><b>48x48</b></sub> </a>
        </td>
        <td align="center">
            <a> <img width="100" height="100" alt="Image" src="https://github.com/user-attachments/assets/61463e20-5ba3-4ce4-a632-8905ed1357b0" /><br> <sub><b>100x100</b></sub> </a>
        </td>
    </tr>
</table>
<table table align="center" cellspacing="20">
    <tr align="center"><h3>Neon</h3></tr>
    <tr>
        <td align="center">
            <a> <img width="48" height="48" alt="Image" src="https://github.com/user-attachments/assets/6009e417-0221-4307-89c2-aedba5be7d12" /><br> <sub><b>48x48</b></sub> </a>
        </td>
        <td align="center">
            <a> <img width="100" height="100" alt="Image" src="https://github.com/user-attachments/assets/fc997634-c093-4689-a609-a37ad21de6ed" /><br> <sub><b>100x100</b></sub> </a>
        </td>
    </tr>
</table>

---

## Licença

MIT — ou seja: use, quebre, refaça, mas me cite se for ficar famoso com isso 😎

---

🧙‍♂️ Autores

<table>
    <tr>
    <td align="center">
        <a href="https://github.com/alinmeyer"> <img src="https://avatars.githubusercontent.com/u/143973449?v=4" width="115"/><br> <sub><b>Aline Meyer</b></sub> </a>
    </td>
        <td align="center"> <a href="https://github.com/JunhaumHayden"> <img src="https://avatars.githubusercontent.com/u/79289647?v=4" width="115"/><br> <sub><b>Carlos Hayden</b></sub> </a>
    </td>
        <td align="center"> <a href="https://github.com/flplz"> <img src="https://avatars.githubusercontent.com/u/127215448?v=4" width="115"/><br> <sub><b>Felipe Pacheco</b></sub> </a> </td>
    </tr>
</table>
<p align="center"> <em>🧠💻 Built with data, code & caffeine.<br> May the <strong>rent</strong> be ever in your favor.</em> ☕✨ </p>