from flask import Flask
from flask_restx import Api

from app.container.container import Container
from app.routes.clientes_routes import clientes_ns
from app.routes.funcionarios_routes import funcionarios_ns
from app.routes.catalogo_routes import catalogo_ns
from app.routes.estoque_routes import estoque_ns
from app.routes.alugueis_routes import alugueis_ns
from app.routes.vendas_routes import vendas_ns
from app.routes.demo_routes import demo_ns

def create_app(test_config=None):
    app = Flask(__name__)

    # Configuração do Swagger
    api = Api(
        app,
        version='1.0',
        title='RetroHub API',
        description='API para loja online de jogos físicos e digitais',
        doc='/docs'  # URL para acessar a documentação Swagger
    )

    # Initialize data factory (mock mode by default)
    # injeta dependencias nas rotas
    app.container = Container()

    # If a test configuration for DB was provided, initialize the DB factory
    if test_config:
        try:
            from app.database.factories.database_manager import DatabaseManager
            # test_config is expected to contain keys accepted by DatabaseManager.init_db
            DatabaseManager.init_db(**test_config)
        except Exception:
            # If DB initialization fails here, tests will handle/report it
            pass

    # Registra os namespaces do Flask-RESTX
    api.add_namespace(clientes_ns)
    api.add_namespace(funcionarios_ns)
    api.add_namespace(catalogo_ns)
    api.add_namespace(estoque_ns)
    api.add_namespace(alugueis_ns)
    api.add_namespace(vendas_ns)
    api.add_namespace(demo_ns)

    @app.route('/')
    def index():
        return {"status": "RetroHub API is running (mock mode)"}

    return app
