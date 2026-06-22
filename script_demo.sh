#!/usr/bin/env bash
# Demo automatizada do fluxo de aluguel.
#
# ONDE VER O RESULTADO:
#   - Respostas JSON de cada passo: impressas neste terminal (stdout)
#   - Logs do servidor Flask: arquivo server.log na pasta do projeto
#
# USO:
#   chmod +x script_demo.sh    # só precisa uma vez
#   ./script_demo.sh             # modo interativo (pergunta se quer parar o servidor)
#   DEMO_AUTO_KILL=y ./script_demo.sh   # para o servidor automaticamente ao final
#
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

BASE_URL="${DEMO_BASE_URL:-http://127.0.0.1:5000}"
SERVER_PID=""
STARTED_SERVER=0

pretty_json() {
  python3 -c 'import sys,json; data=sys.stdin.read();
try:
    print(json.dumps(json.loads(data), indent=2, ensure_ascii=False))
except Exception:
    print(data)'
}

extract_aluguel_id() {
  python3 -c 'import sys,json
try:
    d=json.loads(sys.stdin.read())
    print(d.get("aluguel", {}).get("id_transacao", "") or "")
except Exception:
    print("")'
}

port_in_use() {
  python3 -c "import socket; s=socket.socket(); exit(0 if s.connect_ex(('127.0.0.1', 5000)) == 0 else 1)"
}

wait_for_server() {
  for _ in $(seq 1 20); do
    if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/docs" | grep -q "200"; then
      return 0
    fi
    sleep 1
  done
  return 1
}

cleanup() {
  if [ "$STARTED_SERVER" -eq 1 ] && [ -n "${SERVER_PID:-}" ]; then
    kill "$SERVER_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT

echo "=========================================="
echo " RetroHub — Demo automatizada de aluguel"
echo "=========================================="
echo ""

echo "[1/7] Ativando venv..."
source ./venv/bin/activate

echo "[2/7] Recriando banco (seed_db.py)..."
python3 seed_db.py

echo "[3/7] Verificando servidor na porta 5000..."
if port_in_use; then
  echo "      Servidor já está rodando em $BASE_URL — reutilizando."
else
  echo "      Iniciando servidor (logs em server.log)..."
  ./venv/bin/python run.py > server.log 2>&1 &
  SERVER_PID=$!
  STARTED_SERVER=1
  if ! wait_for_server; then
    echo "ERRO: servidor não respondeu. Veja server.log:"
    tail -n 50 server.log || true
    exit 1
  fi
  echo "      Servidor OK (PID $SERVER_PID)"
fi

echo ""
echo "[4/7] Criando aluguel..."
RESP=$(curl -s -X POST "$BASE_URL/api/alugueis/solicitar" \
  -H "Content-Type: application/json" \
  -H "X-Cliente-Id: 1" \
  -d '{"id_catalogo":1,"dias_alugados":3,"data_inicio":"2026-06-23","tipo_midia":"DIGITAL"}')

echo "$RESP" | pretty_json

ALUGUEL_ID=$(echo "$RESP" | extract_aluguel_id)

if [ -z "$ALUGUEL_ID" ]; then
  echo ""
  echo "ERRO: não foi possível criar o aluguel."
  if [ "$STARTED_SERVER" -eq 1 ]; then
    echo "Últimas linhas de server.log:"
    tail -n 50 server.log || true
  else
    echo "O servidor já estava rodando — confira o terminal onde você iniciou o run.py."
  fi
  exit 1
fi

echo ""
echo "      id_transacao capturado: $ALUGUEL_ID"
echo ""

echo "[5/7] Processando pagamento..."
curl -s -X PATCH "$BASE_URL/api/alugueis/$ALUGUEL_ID/pagamento" \
  -H "Content-Type: application/json" \
  -H "X-Cliente-Id: 1" \
  -d '{"sucesso": true}' | pretty_json
echo ""

sleep 1

echo "[6/7] Registrando retirada..."
curl -s -X PATCH "$BASE_URL/api/alugueis/$ALUGUEL_ID/retirada" \
  -H "X-Funcionario-Id: 1" | pretty_json
echo ""

sleep 1

echo "[7/7] Renovando aluguel..."
curl -s -X PATCH "$BASE_URL/api/alugueis/$ALUGUEL_ID/renovar" \
  -H "Content-Type: application/json" \
  -H "X-Cliente-Id: 1" \
  -d '{"dias_adicionais":2}' | pretty_json
echo ""

sleep 1

echo "Devolução (final do ciclo)..."
curl -s -X PATCH "$BASE_URL/api/alugueis/$ALUGUEL_ID/devolucao" \
  -H "Content-Type: application/json" \
  -H "X-Funcionario-Id: 1" \
  -d '{"condicao_item":"bom"}' | pretty_json
echo ""

echo "=========================================="
echo " Demo concluída com sucesso!"
echo " - Respostas JSON: acima neste terminal"
if [ "$STARTED_SERVER" -eq 1 ]; then
  echo " - Logs do servidor: $PROJECT_DIR/server.log"
fi
echo " - Swagger UI: $BASE_URL/docs"
echo "=========================================="

if [ "$STARTED_SERVER" -eq 1 ]; then
  if [ "${DEMO_AUTO_KILL:-}" = "y" ] || [ "${DEMO_AUTO_KILL:-}" = "Y" ]; then
    echo "Parando servidor (DEMO_AUTO_KILL=y)..."
    kill "$SERVER_PID" 2>/dev/null || true
    STARTED_SERVER=0
  else
    read -r -p "Parar o servidor que este script iniciou? [y/N] " KILL
    if [ "$KILL" = "y" ] || [ "$KILL" = "Y" ]; then
      kill "$SERVER_PID" 2>/dev/null || true
      STARTED_SERVER=0
      echo "Servidor parado."
    else
      echo "Servidor continua rodando em $BASE_URL (PID $SERVER_PID)."
      trap - EXIT
    fi
  fi
fi
