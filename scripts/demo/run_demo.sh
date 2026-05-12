#!/usr/bin/env bash
set -euo pipefail
# Demo script: starts the app, waits for readiness, runs example requests, saves outputs.

REPO_ROOT=$(cd "$(dirname "$0")/../.." && pwd)
PY=$REPO_ROOT/.venv/bin/python
OUT_DIR=$REPO_ROOT/scripts/demo/output
mkdir -p "$OUT_DIR"

PORT=5001
echo "Starting RetroHub API (background) on port $PORT..."
"$PY" -c "from app import create_app; app=create_app(); app.run(host='127.0.0.1', port=$PORT, debug=True)" &> "$REPO_ROOT/scripts/demo/server.log" &
SERVER_PID=$!
echo $SERVER_PID > "$REPO_ROOT/scripts/demo/server.pid"
echo "Server PID: $SERVER_PID"

echo "Waiting for server readiness..."
"$PY" "$REPO_ROOT/scripts/demo/wait_for_server.py" http://127.0.0.1:$PORT/ 15

echo "Running requests and saving outputs to $OUT_DIR"

# Auto-select IDs from mock data to make demo robust
DATA_FILE="$REPO_ROOT/resources/database/data-mock.json"
VALS=$("$PY" - <<PY
import json
f=open('$DATA_FILE')
data=json.load(f)
# find first ATIVO aluguel
aluguel_id=None
for a in data.get('alugueis',[]):
	if a.get('status')=='ATIVO':
		aluguel_id=a.get('id_transacao')
		break
if aluguel_id is None:
	aluguel_id=(data.get('alugueis',[{}])[0].get('id_transacao') if data.get('alugueis') else 1)
# find cliente id for that transacao
cliente_id=None
for t in data.get('transacoes',[]):
	if t.get('id')==aluguel_id:
		cliente_id=t.get('id_cliente')
		break
if cliente_id is None:
	cliente_id=(data.get('clientes',[{}])[0].get('id_usuario') if data.get('clientes') else 1)
# pick a funcionario id (first configured)
func_id=None
funcs=data.get('funcionarios',[])
if funcs:
	func_id=funcs[0].get('id_usuario')
else:
	for u in data.get('usuarios',[]):
		if u.get('tipo')=='funcionario':
			func_id=u.get('id')
			break
print(aluguel_id, cliente_id, func_id)
PY
)
read ALUGUEL_ID ID_CLIENTE FUNC_ID <<< "$VALS"
echo "Using aluguel_id=$ALUGUEL_ID, cliente_id=$ID_CLIENTE, funcionario_id=$FUNC_ID"

curl -s -H "X-Cliente-Id: $ID_CLIENTE" http://127.0.0.1:$PORT/api/alugueis/meus-alugueis -o "$OUT_DIR/meus_alugueis.json"

curl -s -X PATCH -H "X-Funcionario-Id: $FUNC_ID" http://127.0.0.1:$PORT/api/alugueis/$ALUGUEL_ID/retirada -o "$OUT_DIR/retirada_${ALUGUEL_ID}.json"

curl -s -X PATCH -H "Content-Type: application/json" -H "X-Funcionario-Id: $FUNC_ID" -d '{"condicao_item":"bom"}' http://127.0.0.1:$PORT/api/alugueis/$ALUGUEL_ID/devolucao -o "$OUT_DIR/devolucao_${ALUGUEL_ID}.json"

echo "Requests complete. Server log tail (last 40 lines):"
tail -n 40 "$REPO_ROOT/scripts/demo/server.log" || true

echo "Stopping server (PID $SERVER_PID)..."
kill $SERVER_PID || true
rm -f "$REPO_ROOT/scripts/demo/server.pid"

echo "Demo outputs saved in: $OUT_DIR"
ls -l "$OUT_DIR"
