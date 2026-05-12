# Demo script

This demo starts the API server in the repository virtualenv, waits for readiness, runs example requests against the `/api/alugueis` endpoints and saves JSON responses under `scripts/demo/output`.

Usage:

```bash
source .venv/bin/activate
bash scripts/demo/run_demo.sh
```

Outputs:
- `scripts/demo/output/meus_alugueis.json`
- `scripts/demo/output/retirada_1.json`
- `scripts/demo/output/devolucao_1.json`

Quick Swagger instructions for the presentation:

- Restart the server right before your demo so the mock JSON is reloaded.
- Open the Swagger UI at `http://127.0.0.1:5001/docs` (or `http://localhost:5001/docs`).
- Use the demo helper endpoint `/api/demo/available` to see which `clientes`, `funcionarios` and `alugueis` are present (look for an aluguel with status `SOLICITADO`, id 10).
- In each endpoint that requires headers, click "Try it out" and add the headers under "Parameters":
	- `X-Cliente-Id`: 3 (for client operations)
	- `X-Funcionario-Id`: 1 (for staff operations such as retirada)
- Sequence to demo (expected result):
	1. (Optional) If you previously modified data or performed the demo, call `POST /api/demo/reset` in Swagger or via curl to reload `resources/database/data-mock.json` into memory so aluguel id 10 returns to `SOLICITADO`.
	2. `GET /api/alugueis/meus-alugueis` with `X-Cliente-Id: 3` — should list aluguel id 10 with status `SOLICITADO`.
	3. `PATCH /api/alugueis/10/retirada` with `X-Funcionario-Id: 1` — should return 200 and mensagem "Retirada registrada com sucesso." and aluguel status `ATIVO` in the response body.
	3. (Optional) `PATCH /api/alugueis/10/devolucao` with `X-Funcionario-Id: 1` and body `{ "condicao_item": "BOM" }` — should accept and return updated aluguel.

Notes:
- Always restart the server after changing `resources/database/data-mock.json` so the `MockDataSource` reloads data.
- If Swagger UI doesn't show header fields for a route, they appear under the request parameters when you click "Try it out" for that operation.
- You can avoid restarting the server by calling `POST /api/demo/reset` (in `/docs` or via curl) — this reloads the JSON into the running MockDataSource.
