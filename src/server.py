from flask import Flask, jsonify, request

app = Flask(__name__)

# Home Route
@app.route('/', methods=['GET'])
def index():
    return jsonify({'response': 'Hello world!'})

# Testing Route
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'response': 'pong!'})

def start():
    app.run(debug=True, port=4000)
    print('Server running')
