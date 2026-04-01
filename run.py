from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
        # Run the Flask development server
        # host='0.0.0.0' allows access from outside the container (if using Docker)
        # debug=True enables auto-reload on code changes
        app.run(host='0.0.0.0', port=5000, debug=True)
