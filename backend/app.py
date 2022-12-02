from flask import Flask
from flask_cors import CORS
from flask import render_template
from flask import jsonify

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    response_body = {
        'name' : 'Testname',
        'about'  : 'hello world',
    }
    return response_body

@app.route("/graph/", methods=['GET'])
def send_graph():
    # return render_template('positives.html',)
    return jsonify(render_template('positives.html',))
    # return send_from_directory('positives.html','/api')
