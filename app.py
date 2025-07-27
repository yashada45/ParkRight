from flask import Flask, request, make_response
from app import create_app

app = Flask(__name__, template_folder='templates')

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', use_reloader=True, port=5000)