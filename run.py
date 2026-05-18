import logging
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Configura um logger temporário para imprimir a mensagem antes do app rodar
    # já que as mensagens padrões do Flask não são facilmente sobrescritas.
    logger = logging.getLogger('werkzeug')
    logger.info("---------------------------------------------------------")
    logger.info("  Swagger UI disponível em: http://localhost:5000/docs   ")
    logger.info("---------------------------------------------------------")

    # Run the Flask development server
    # host='0.0.0.0' allows access from outside the container (if using Docker)
    # debug=True enables auto-reload on code changes
    app.run(host='0.0.0.0', port=5000, debug=True)