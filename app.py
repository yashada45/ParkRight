from flask import Flask, request, make_response
from app import create_app

app = Flask(__name__, template_folder='templates')

app = create_app()

# @app.route('/')
# def index(): 
#     myresponse = make_response('<h1>heyy again!</h1>')
#     myresponse.status_code =  200
#     myresponse.headers['Content-Type'] = 'text/html'
#     return myresponse

# @app.route('/hie', methods=['GET', 'POST'])
# def hie():
#     if request.method == 'POST':
#         return "<h1>hello, hie! (POST)</h1>"
#     else:
#         return "<h1>hie, hello!</h1>", 200

# @app.route('/greet/<name>')
# def greet(name):
#     return f"<h1>hello, {name}!</h1>"

# @app.route('/add/<int:a>/<int:b>')
# def add(a, b):
#     return f"<h1>{a} + {b} = {a + b}</h1>"

# @app.route('/handle_url_param')
# def handle_url_param():
#     if 'name' in request.args.keys() and 'quality' in request.args.keys():
#         name = request.args.get('name') 
#         quality = request.args.get('quality')
#         return f"<h1>Hello, {name}! You are so {quality}!</h1>"
#     else:
#         return "<h1>Hello, stranger!</h1>"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', use_reloader=True, port=5000)