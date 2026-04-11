from flask import Flask
from app.database.factories.database_manager import DatabaseManager
from app.routes.clientes_routes import clientes_bp
from app.routes.funcionarios_routes import funcionarios_bp
from app.routes.catalogo_routes import catalogo_bp

def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        # Inicializa a conexão com o banco de dados principal
        DatabaseManager.init_db()
    else:
        # Se for teste, inicializa usando as configurações injetadas (ex: sqlite em memória)
        DatabaseManager.init_db(**test_config)

    # Registra os blueprints das rotas
    app.register_blueprint(clientes_bp)
    app.register_blueprint(funcionarios_bp)
    app.register_blueprint(catalogo_bp)

    @app.route('/')
    def index():
        return {"status": "RetroHub API is running"}

    return app
