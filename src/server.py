from flask import Flask, jsonify, request
import src.login as login
import src.scrapper as scrapper
import src.proxis as proxis

app = Flask(__name__)
ClientGlobalLogin = None

# Home Route
@app.route('/', methods=['GET'])
def index():
    return jsonify({'response': 'Hello world!'})

# Testing Route
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'response': 'pong!'})

# Check Logins Route
@app.route('/login/check-logins', methods=['GET'])
def login_CheckLogins():
    return login.checkLogins(jsonify, request)

# Status Check Logins Route
@app.route('/login/status-logins', methods=['GET'])
def login_StatusLogins():
    return login.StatusLogins(jsonify, request)

# Scrapper Route
@app.route('/scrapper', methods=['POST'])
def login_Scrapper():
    return scrapper.scrapper(jsonify, request)

# Scrapper Route
@app.route('/scrapper-details', methods=['POST'])
def login_ScrapperDetails():
    return scrapper.status(jsonify, request)

# Proxis List Route
@app.route('/proxis', methods=['GET'])
def login_Proxis():
    return proxis.all(jsonify, request)

# Proxis Add Route
@app.route('/proxis', methods=['POST'])
def login_ProxisAdd():
    return proxis.add(jsonify, request)

# Proxis Delete Route
@app.route('/proxis', methods=['DELETE'])
def login_ProxisDelete():
    return proxis.delete(jsonify, request)

# Proxis Check Route
@app.route('/proxis-check', methods=['GET'])
def login_ProxisCheck():
    return proxis.test(jsonify, request)

# Proxis Import Route
@app.route('/proxis', methods=['PUT'])
def login_ProxisImport():
    return proxis.importProxis(jsonify, request)    

def start(PORT):
    print('Server running in port : ' + str(PORT))
    app.run(debug=True, port=PORT)
