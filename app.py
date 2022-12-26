from flask import Flask
from flask_cors import CORS
from flask import render_template
from flask import jsonify
from flask import send_from_directory
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return render_template('index.html.j2')

@app.route("/trade")
def send_trade_page():
    return render_template('trade.html.j2')

@app.route("/backtest")
def send_graph():
    return render_template('backtest.html.j2')

