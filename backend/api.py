from flask import Flask, jsonify, request, abort, make_response
import json

app = Flask(__name__)

@app.route("/")
def home():
    with open('./data/forecast.json') as f:
        data = json.load(f)
    return jsonify(data)

    
if __name__ == "__main__":
    app.run(debug=True)