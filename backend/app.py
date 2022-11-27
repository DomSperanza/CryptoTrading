from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    response_body = {
        'name' : 'Testname',
        'about'  : 'hello world',
    }
    return response_body