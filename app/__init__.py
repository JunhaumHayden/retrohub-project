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

    # Injeta o container na aplicação Flask
    app.container = Container()

    # Registra os namespaces do Flask-RESTX
    api.add_namespace(clientes_ns)
    api.add_namespace(funcionarios_ns)
    api.add_namespace(catalogo_ns)
    api.add_namespace(estoque_ns)
    api.add_namespace(alugueis_ns)
    api.add_namespace(vendas_ns)

    @app.route('/')
    def index():
        return {"status": "RetroHub API is running"}

    # Adiciona a mensagem customizada na inicialização do servidor
    # (visível apenas quando o servidor de desenvolvimento do Flask é usado)
    with app.app_context():
        logger = logging.getLogger('werkzeug')
        if logger.hasHandlers():
            logger.info("*" * 60)
            logger.info("  => Swagger UI disponível em: http://localhost:5000/docs")
            logger.info("*" * 60)

    return app
