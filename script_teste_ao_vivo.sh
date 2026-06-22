#!/usr/bin/env bash
# Simula o cenário da professora: cadastra jogo + estoque ao vivo e testa tudo.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"
source ./venv/bin/activate

BASE="${DEMO_BASE_URL:-http://127.0.0.1:5000}"
PASS=0
FAIL=0
SUFFIX=$(date +%s)

check() {
  local name="$1" code="$2" expect="$3"
  if [ "$code" = "$expect" ]; then
    echo "  ✓ $name"
    PASS=$((PASS + 1))
  else
    echo "  ✗ $name (esperado $expect, recebeu $code)"
    FAIL=$((FAIL + 1))
  fi
}

request() {
  curl -s -w "\n%{http_code}" "$@"
}

echo "=== RetroHub — teste ao vivo (item novo) ==="
python3 seed_db.py >/dev/null

if ! curl -s -o /dev/null -w "%{http_code}" "$BASE/docs" | grep -q 200; then
  echo "ERRO: servidor não está em $BASE — rode: ./venv/bin/python run.py"
  exit 1
fi

TITULO="Jogo Ao Vivo $SUFFIX"

echo ""
echo "1. Cadastrar jogo no catálogo"
R=$(request -X POST "$BASE/api/catalogo/itens/" \
  -H "Content-Type: application/json" -H "X-Funcionario-Id: 1" \
  -d "{\"titulo\":\"$TITULO\",\"genero\":\"Aventura\",\"situacao\":\"DISPONIVEL\"}")
check "POST catalogo" "$(echo "$R" | tail -1)" "201"
CAT_ID=$(echo "$R" | sed '$d' | python3 -c "import sys,json; print(json.load(sys.stdin)['item']['id'])")
echo "     id_catalogo=$CAT_ID"

echo ""
echo "2. Cadastrar exemplares (venda + aluguel)"
R=$(request -X POST "$BASE/api/estoque/digital" \
  -H "Content-Type: application/json" -H "X-Funcionario-Id: 1" \
  -d "{\"id_catalogo\":$CAT_ID,\"chave_ativacao\":\"VENDA-$SUFFIX\"}")
check "POST estoque digital (venda)" "$(echo "$R" | tail -1)" "201"

R=$(request -X POST "$BASE/api/estoque/digital" \
  -H "Content-Type: application/json" -H "X-Funcionario-Id: 1" \
  -d "{\"id_catalogo\":$CAT_ID,\"chave_ativacao\":\"ALUGUEL-$SUFFIX\"}")
check "POST estoque digital (aluguel)" "$(echo "$R" | tail -1)" "201"

R=$(request "$BASE/api/estoque/catalogo/$CAT_ID")
check "GET estoque do jogo" "$(echo "$R" | tail -1)" "200"

echo ""
echo "3. Venda do jogo novo"
R=$(request -X POST "$BASE/api/vendas/solicitar" \
  -H "Content-Type: application/json" -H "X-Cliente-Id: 1" \
  -d "{\"id_catalogo\":$CAT_ID,\"tipo_midia\":\"DIGITAL\"}")
check "POST venda" "$(echo "$R" | tail -1)" "201"
VENDA_ID=$(echo "$R" | sed '$d' | python3 -c "import sys,json; print(json.load(sys.stdin).get('id_transacao',''))")

echo ""
echo "4. Aluguel completo do jogo novo"
R=$(request -X POST "$BASE/api/alugueis/solicitar" \
  -H "Content-Type: application/json" -H "X-Cliente-Id: 1" \
  -d "{\"id_catalogo\":$CAT_ID,\"dias_alugados\":2,\"data_inicio\":\"2026-06-25\",\"tipo_midia\":\"DIGITAL\"}")
check "POST aluguel" "$(echo "$R" | tail -1)" "201"
ALUGUEL_ID=$(echo "$R" | sed '$d' | python3 -c "import sys,json; print(json.load(sys.stdin)['aluguel']['id_transacao'])")

R=$(request -X PATCH "$BASE/api/alugueis/$ALUGUEL_ID/pagamento" \
  -H "Content-Type: application/json" -H "X-Cliente-Id: 1" -d '{"sucesso":true}')
check "PATCH pagamento" "$(echo "$R" | tail -1)" "200"

R=$(request -X PATCH "$BASE/api/alugueis/$ALUGUEL_ID/retirada" -H "X-Funcionario-Id: 1")
check "PATCH retirada" "$(echo "$R" | tail -1)" "200"

R=$(request -X PATCH "$BASE/api/alugueis/$ALUGUEL_ID/renovar" \
  -H "Content-Type: application/json" -H "X-Cliente-Id: 1" -d '{"dias_adicionais":1}')
check "PATCH renovar" "$(echo "$R" | tail -1)" "200"

R=$(request -X PATCH "$BASE/api/alugueis/$ALUGUEL_ID/devolucao" \
  -H "Content-Type: application/json" -H "X-Funcionario-Id: 1" -d '{"condicao_item":"bom"}')
check "PATCH devolucao" "$(echo "$R" | tail -1)" "200"

echo ""
echo "5. Avaliações"
R=$(request -X POST "$BASE/api/avaliacoes/$VENDA_ID" \
  -H "Content-Type: application/json" -H "X-Cliente-Id: 1" \
  -d '{"nota":5,"comentario":"Otimo jogo!"}')
check "POST avaliacao venda" "$(echo "$R" | tail -1)" "201"

R=$(request -X POST "$BASE/api/avaliacoes/$ALUGUEL_ID" \
  -H "Content-Type: application/json" -H "X-Cliente-Id: 1" \
  -d '{"nota":4,"comentario":"Boa experiencia de aluguel"}')
check "POST avaliacao aluguel" "$(echo "$R" | tail -1)" "201"

R=$(request "$BASE/api/avaliacoes/minhas" -H "X-Cliente-Id: 1")
check "GET minhas avaliacoes" "$(echo "$R" | tail -1)" "200"

echo ""
echo "6. Relatório"
R=$(request "$BASE/api/relatorios/compras-locacoes" -H "X-Funcionario-Id: 1")
check "GET relatorio" "$(echo "$R" | tail -1)" "200"

echo ""
echo "=========================================="
echo " Resultado: $PASS OK, $FAIL falha(s)"
echo "=========================================="
[ "$FAIL" -eq 0 ]
