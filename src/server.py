from flask import Flask, jsonify, request, make_response
import src.login as login
import src.scrapper as scrapper
import src.proxis as proxis
import src.accounts as accounts
import src.campaigns as campaigns
import src.join as join

app = Flask(__name__)
ClientGlobalLogin = None

def returnResponse(data):
    try:
        return data, int(data.json['status'])    
    except:
        return data

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
    return returnResponse(login.checkLogins(jsonify, request))

# Status Check Logins Route
@app.route('/login/status-logins', methods=['GET'])
def login_StatusLogins():
    return returnResponse(login.StatusLogins(jsonify, request))

# Scrapper Route
@app.route('/scrapper', methods=['POST'])
def login_Scrapper():
    return returnResponse(scrapper.scrapper(jsonify, request))

# Scrapper Route
@app.route('/scrapper-details', methods=['POST'])
def login_ScrapperDetails():
    return returnResponse(scrapper.status(jsonify, request))

# Proxis List Route
@app.route('/proxis', methods=['GET'])
def login_Proxis():
    return returnResponse(proxis.all(jsonify, request))

# Proxis Add Route
@app.route('/proxis', methods=['POST'])
def login_ProxisAdd():
    return returnResponse(proxis.add(jsonify, request))

# Proxis Delete Route
@app.route('/proxis', methods=['DELETE'])
def login_ProxisDelete():
    return returnResponse(proxis.delete(jsonify, request))

# Proxis Check Route
@app.route('/proxis-check', methods=['GET'])
def login_ProxisCheck():
    return returnResponse(proxis.test(jsonify, request))

# Proxis Import Route
@app.route('/proxis', methods=['PUT'])
def login_ProxisImport():
    return returnResponse(proxis.importProxis(jsonify, request))

# Accounts List Route
@app.route('/accounts', methods=['GET'])
def login_Accounts():
    return returnResponse(accounts.all(jsonify, request))

# Accounts Delete Route
@app.route('/accounts', methods=['DELETE'])
def login_AccountsDelete():
    return returnResponse(accounts.delete(jsonify, request))

# Accounts Export Route
@app.route('/accounts-export', methods=['GET'])
def login_AccountsExport():
    return returnResponse(accounts.export(jsonify, request, make_response))

# Accounts Import Route
@app.route('/accounts-import', methods=['POST'])
def login_AccountsImport():
    return returnResponse(accounts.importAccounts(jsonify, request))

# Accounts Errors Route
@app.route('/accounts-errors', methods=['GET'])
def login_AccountsErrors():
    return returnResponse(accounts.errors(jsonify, request))

# Accounts Delete Errors Route
@app.route('/accounts-delete-errors', methods=['DELETE'])
def login_AccountsDeleteErrors():
    return returnResponse(accounts.deleteErrors(jsonify, request))

# Campaigns List Route
@app.route('/campaigns', methods=['GET'])
def login_Campaigns():
    return returnResponse(campaigns.all(jsonify, request))

# Campaigns Accounts Route
@app.route('/campaigns-accounts', methods=['POST'])
def login_CampaignsAccounts():
    return returnResponse(campaigns.accounts(jsonify, request))

# Campaigns Users Route
@app.route('/campaigns-users', methods=['POST'])
def login_CampaignsUsers():
    return returnResponse(campaigns.users(jsonify, request))

# Campaigns Delete Route
@app.route('/campaigns', methods=['DELETE'])
def login_CampaignsDelete():
    return returnResponse(campaigns.delete(jsonify, request))

# Campaigns Pause Route
@app.route('/campaigns', methods=['PUT'])
def login_CampaignsPause():
    return returnResponse(campaigns.pause(jsonify, request))

# Campaigns Export Route
@app.route('/campaigns-export/<int:campaign_id>', methods=['GET'])
def login_CampaignsExport(campaign_id):
    return returnResponse(campaigns.export(jsonify, request, make_response, int(campaign_id)))

# Campaigns Import Route
@app.route('/campaigns-import', methods=['POST'])
def login_CampaignsImport():
    return returnResponse(campaigns.importCampaigns(jsonify, request))

# Campaigns Join Route
@app.route('/campaigns-joined', methods=['POST'])
def login_CampaignsJoin():
    return returnResponse(campaigns.joined(jsonify, request))

# Join Users to campaign Route
@app.route('/join', methods=['POST'])
def login_Join():
    return returnResponse(join.join(jsonify, request))

# Test Code Response Route
@app.route('/test-code', methods=['GET'])
def login_Test():
    data = jsonify({'status': 500, 'message': 'OK', 'payload': {}})
    return returnResponse(data)

# Error 404 Route
@app.errorhandler(404)
def handle_404(e):
    return returnResponse(jsonify({'status': 404, 'message': 'Error 404', 'payload': {}}))

def start(PORT):
    print('Server running in port : ' + str(PORT))
    app.run(debug=True, port=PORT)
