from flask import Flask, jsonify, request, make_response
import src.login as login
import src.scrapper as scrapper
import src.proxis as proxis
import src.accounts as accounts
import src.campaigns as campaigns

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

# Accounts List Route
@app.route('/accounts', methods=['GET'])
def login_Accounts():
    return accounts.all(jsonify, request)

# Accounts Delete Route
@app.route('/accounts', methods=['DELETE'])
def login_AccountsDelete():
    return accounts.delete(jsonify, request)

# Campaigns List Route
@app.route('/campaigns', methods=['GET'])
def login_Campaigns():
    return campaigns.all(jsonify, request)

# Campaigns Accounts Route
@app.route('/campaigns-accounts', methods=['POST'])
def login_CampaignsAccounts():
    return campaigns.accounts(jsonify, request)

# Campaigns Users Route
@app.route('/campaigns-users', methods=['POST'])
def login_CampaignsUsers():
    return campaigns.users(jsonify, request)

# Campaigns Delete Route
@app.route('/campaigns', methods=['DELETE'])
def login_CampaignsDelete():
    return campaigns.delete(jsonify, request)

# Campaigns Pause Route
@app.route('/campaigns', methods=['PUT'])
def login_CampaignsPause():
    return campaigns.pause(jsonify, request)

# Campaigns Export Route
@app.route('/campaigns-export/<int:campaign_id>', methods=['GET'])
def login_CampaignsExport(campaign_id):
    return campaigns.export(jsonify, request, make_response, int(campaign_id))

# Campaigns Import Route
@app.route('/campaigns-import', methods=['POST'])
def login_CampaignsImport():
    return campaigns.importCampaigns(jsonify, request)

def start(PORT):
    print('Server running in port : ' + str(PORT))
    app.run(debug=True, port=PORT)
