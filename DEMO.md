# Demo - Fluxo Venda e Aluguel

Instruções passo-a-passo para demonstrar as funcionalidades de **Comprar (Vendas)** e **Realizar Aluguel** para a professora.

## Preparação (antes da apresentação)

```bash
cd /home/lipon/projetos/retrohub/retrohub-project

# Ativar venv
source ./venv/bin/activate

# Re-seed DB (importante: limpa dados antigos e cria cliente, funcionário, catálogo e exemplares)
python3 seed_db.py

# Iniciar servidor
./venv/bin/python run.py
```

O servidor inicia em http://127.0.0.1:5000. Swagger UI disponível em http://127.0.0.1:5000/docs

---

## Opção 1: Demonstração via Swagger UI (recomendado para apresentação)

Abrir Swagger em http://localhost:5000/docs

### 1. Demonstrar Fluxo de Venda

1. Clique em **POST /api/vendas/solicitar**
2. Clique em "Try it out"
3. Em **X-Cliente-Id** (header), digite `1`
4. Em **Request body**, cole:
   ```json
   {
     "id_catalogo": 1,
     "tipo_midia": "DIGITAL"
   }
   ```
5. Clique **Execute** → deve retornar **201 Created** com `id_transacao`

6. Depois, clique em **GET /api/vendas/minhas-vendas**
7. Clique em "Try it out"
8. Digite header **X-Cliente-Id**: `1`
9. Clique **Execute** → mostra lista de vendas do cliente

### 2. Demonstrar Fluxo de Aluguel (ordem importante)

#### 2.1 Criar Aluguel
1. Clique em **POST /api/alugueis/solicitar**
2. Clique em "Try it out"
3. Header **X-Cliente-Id**: `1`
4. Request body:
   ```json
   {
     "id_catalogo": 1,
     "dias_alugados": 3,
     "data_inicio": "2026-06-23",
     "tipo_midia": "DIGITAL"
   }
   ```
5. Clique **Execute** → retorna **201 Created** com `aluguel.id_transacao` (ex: `3`)
6. **Copie o `id_transacao`** — você usará nos passos seguintes

#### 2.2 Demonstrar Guarda de Estado (erro esperado)
1. Clique em **PATCH /api/alugueis/{id}/retirada**
2. Clique em "Try it out"
3. Digite `{ID}` (o id_transacao do aluguel criado, ex: `3`)
4. Header **X-Funcionario-Id**: `2`
5. Clique **Execute** → deve retornar **400 BAD REQUEST** com mensagem "Transição de estado inválida"
   - **Explique**: Não é possível fazer retirada sem processar pagamento primeiro (máquina de estados).

#### 2.3 Processar Pagamento
1. Clique em **PATCH /api/alugueis/{id}/pagamento**
2. Clique em "Try it out"
3. Digite `{ID}` (mesmo id do aluguel)
4. Header **X-Cliente-Id**: `1`
5. Request body:
   ```json
   {
     "sucesso": true
   }
   ```
6. Clique **Execute** → deve retornar **200 OK**, status do aluguel muda para "APROVADO"

#### 2.4 Registrar Retirada
1. Clique em **PATCH /api/alugueis/{id}/retirada**
2. Clique em "Try it out"
3. Digite `{ID}` (mesmo id)
4. Header **X-Funcionario-Id**: `2`
5. Clique **Execute** → deve retornar **200 OK**, status muda para "ATIVO"

#### 2.5 Renovar Aluguel
1. Clique em **PATCH /api/alugueis/{id}/renovar**
2. Clique em "Try it out"
3. Digite `{ID}` (mesmo id)
4. Header **X-Cliente-Id**: `1`
5. Request body:
   ```json
   {
     "dias_adicionais": 2
   }
   ```
6. Clique **Execute** → retorna **200 OK**, `data_prevista_devolucao` e `valor_total` são atualizados

#### 2.6 Registrar Devolução
1. Clique em **PATCH /api/alugueis/{id}/devolucao**
2. Clique em "Try it out"
3. Digite `{ID}` (mesmo id)
4. Header **X-Funcionario-Id**: `2`
5. Request body:
   ```json
   {
     "condicao_item": "bom"
   }
   ```
6. Clique **Execute** → retorna **200 OK**, status muda para "FINALIZADO", comprovante de devolução é gerado

---

## Opção 2: Demonstração via Script Automatizado

Se preferir uma demo automatizada que execute todo o fluxo de uma vez:

```bash
cd /home/lipon/projetos/retrohub/retrohub-project
chmod +x script_demo.sh          # só precisa rodar uma vez
./script_demo.sh
```

### Onde aparece o resultado?

| O quê | Onde ver |
|-------|----------|
| Respostas JSON de cada passo (criar, pagar, retirar, renovar, devolver) | **No próprio terminal** onde você rodou o script |
| Logs do servidor Flask | Arquivo **`server.log`** na pasta do projeto |
| Interface visual (Swagger) | http://127.0.0.1:5000/docs (se o servidor estiver rodando) |

O script imprime cada etapa numerada (`[4/7] Criando aluguel...`, etc.) e o JSON formatado logo abaixo.

**Importante:** feche qualquer servidor antigo na porta 5000 antes de rodar, ou deixe o script reutilizar o que já estiver ativo. Se der erro, veja `server.log` ou o terminal onde o `run.py` está rodando.

Para encerrar o servidor automaticamente ao final (sem pergunta interativa):

```bash
DEMO_AUTO_KILL=y ./script_demo.sh
```

### Teste “professora pede item novo na hora”

Com o servidor rodando, este script cadastra um jogo **do zero**, cria estoque, vende, aluga (fluxo completo), avalia e gera relatório:

```bash
chmod +x script_teste_ao_vivo.sh
./script_teste_ao_vivo.sh
```

Se imprimir `14 OK, 0 falha(s)`, está pronto para esse cenário.

O script:
1. Reseedar DB
2. Inicia servidor (ou reutiliza um já ativo)
3. Cria um aluguel
4. Processa pagamento → retirada → renovação → devolução
5. Mostra respostas formatadas no terminal
6. Pergunta se quer parar o servidor

---

## Opção 3: Demonstração via REST Client (.http)

Se você usar a extensão **REST Client** do VS Code:

1. Abra o arquivo `demo_aluguel.http`
2. Substitua `{{ID}}` pelo id_transacao retornado na primeira requisição
3. Clique em "Send Request" em cada um dos blocos para executar sequencialmente

---

## Pontos-chave para a apresentação

✅ **Fluxo de Venda**
- Criar venda → retorna 201 e id_transacao
- Listar minhas vendas → filtra por cliente

✅ **Fluxo de Aluguel**
- Criar aluguel → reserva exemplar e cria transação
- Tentar retirada antes do pagamento → **erro 400** (guarda de estado)
- Pagar → muda status para APROVADO
- Retirada → muda status para ATIVO, gera comprovante
- Renovar → estende data_prevista_devolucao e valor_total
- Devolução → finaliza, gera comprovante de devolução

✅ **Máquina de Estados**
- Estados: SOLICITADO → APROVADO → ATIVO → FINALIZADO
- Transições inválidas são bloqueadas (ex: retirada antes de pagamento)

---

## Troubleshooting

**Erro: "Não há exemplares ... disponíveis"**
- Rode `python3 seed_db.py` novamente para liberar exemplares

**Erro: "Funcionário não encontrado"**
- Após `seed_db.py`, o funcionário costuma ser ID `2` (cliente é `1`)
- Use `X-Funcionario-Id: 2` nas rotas de retirada, devolução e relatório

**Erro: "Aluguel não encontrado ou não pertence a este cliente"**
- Certifique-se de usar o mesmo `id_transacao` retornado na criação
- Verifique que está usando `X-Cliente-Id: 1` (cliente que criou o aluguel)

**Servidor não inicia**
- Certifique-se de ativar venv: `source ./venv/bin/activate`
- Verifique se porta 5000 está livre: `lsof -i :5000`

---

## Dicas finais

- **Antes de entrar na sala:** rode `seed_db.py` e inicie o servidor
- **Durante a demo:** use cliente `1` e funcionário `2` (IDs exibidos ao rodar `seed_db.py`)
- **Se algo quebrar:** re-execute `seed_db.py` e reinicie o servidor
- **Logs do servidor:** verifique terminal ou arquivo `server.log` (se usar script_demo.sh)
