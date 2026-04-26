"""Configuração global do pytest para o projeto RetroHub.

Os arquivos listados em `collect_ignore` foram escritos contra a arquitetura
antiga (SQLAlchemy ORM, `session.query`, classe `Jogo`) e quebram a coleta no
momento do refactor para Python puro. Eles são mantidos no repositório para
serem reescritos posteriormente contra a nova arquitetura
(`MockDataSource` + camadas Service/Repository), agora usando `Catalogo` no
lugar de `Jogo`.
"""

collect_ignore = [
    # Testes legacy (ORM/session.query/`Jogo`) — precisam ser reescritos
    # para a nova arquitetura mock/services/repositories.
    "tests/models/estoque/test_estoque_routes.py",
    "tests/models/transacao/test_hu05_retirada.py",
    "tests/models/transacao/test_hu06_hu07_devolucao.py",
    "tests/models/transacao/test_vendas_routes.py",
    "tests/models/transacao/test_alugueis_routes.py",
    "tests/models/usuario/test_clientes_routes.py",
    "tests/models/usuario/test_funcionarios_routes.py",
    "tests/models/catalogo/test_catalogo_routes.py",
    # Scripts standalone na raiz (não são pytest tests)
    "standalone_test.py",
    "test_refactoring.py",
    "test_circular_import_fix.py",
    "debug_test.py",
    # Teste de conexão com Postgres real (requer banco rodando)
    "tests/database/db_test.py",
]
