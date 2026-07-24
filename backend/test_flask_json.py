from flask import Flask, jsonify
import numpy as np
import json
import math

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"data": [np.float64(1.0)]})

with app.app_context():
    try:
        print(index().get_data(as_text=True))
    except Exception as e:
        print(f"ERROR: {e}")
