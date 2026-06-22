import logging
from flask import Flask
from flask_restx import Api

from app.container.container import Container
from app.routes.clientes_routes import clientes_ns
from app.routes.funcionarios_routes import funcionarios_ns
from app.routes.catalogo_routes import catalogo_ns
from app.routes.estoque_routes import estoque_ns
from app.routes.alugueis_routes import alugueis_ns
from app.routes.vendas_routes import vendas_ns
from app.routes.avaliacoes_routes import avaliacoes_ns
from app.routes.relatorios_routes import relatorios_ns

def create_app(test_config=None):
    app = Flask(__name__)

    # Configuração do Swagger
    api = Api(
        app,
        version='1.0',
        title='RetroHub API',
        description='API para loja online de jogos físicos e digitais',
        doc='/docs'
    )

    app.container = Container()

    # Registra os namespaces
    api.add_namespace(clientes_ns)
    api.add_namespace(funcionarios_ns)
    api.add_namespace(catalogo_ns)
    api.add_namespace(estoque_ns)
    api.add_namespace(alugueis_ns)
    api.add_namespace(vendas_ns)
    api.add_namespace(avaliacoes_ns)
    api.add_namespace(relatorios_ns)

    @app.route('/')
    def index():
        return {"status": "RetroHub API is running"}

    with app.app_context():
        logger = logging.getLogger('werkzeug')
        if not logger.hasHandlers():
            # Evita duplicar handlers se a app for recarregada
            handler = logging.StreamHandler()
            logger.addHandler(handler)
        logger.info("*" * 60)
        logger.info("  => Swagger UI disponível em: http://localhost:5000/docs")
        logger.info("*" * 60)

    return app
