from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify
from time import time
import requests, os

app = Flask(__name__)

client_id = os.environ.get('ID')
client_secret = os.environ.get('SECRET')
base_url = 'https://io.catchpoint.com/ui/api/v1/'
token_url = 'https://io.catchpoint.com/ui/api/token'
refresh_url = token_url
redirect_uri = 'http://127.0.0.1:5000/menu'


@app.route("/")
def homepage():
    return redirect(url_for('callback'))

@app.route("/menu")
def menu():
    return """
    <h1> Catchpoint v1 api menu</h1>
    <ul>
        <li><a href="/token">Get Token manually</a></li>
        <li><a href="/nodes">Get Nodes</a></li>
        <li><a href="/alltests">Get All Tests</a></li>
        <li><a href="/filteredtests">Get All Tests - Filtered</a></li>
        <li><a href="/filterederrors">Get All Errors - Filtered</a></li>
        <li><a href="/products">Get Products</a></li>
        <li><a href="/assertions">Retrieve identity provider</a></li>
    </ul>
    """

@app.route("/token", methods=["GET"])
def callback():
    # https://requests-oauthlib.readthedocs.io/en/latest/oauth2_workflow.html#backend-application-flow
    client = BackendApplicationClient(client_id=client_id)
    catchpoint = OAuth2Session(client=client)
    token = catchpoint.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret)

    session['oauth_token'] = token['access_token']
    return redirect(url_for('menu'))

@app.route("/assertions", methods=["GET"])
def assertions():
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + session['oauth_token']}
    r = requests.get(base_url + 'assertions', headers=headers)
    ass = r.json()
    return jsonify(ass)

@app.route("/nodes", methods=["GET"])
def nodes():
    if 'oauth_token' not in session:
        return redirect(url_for('homepage'))
    try:
        headers = {'Accept': 'application/json',
                   'Authorization': 'Bearer ' + session['oauth_token']}
        r = requests.get(base_url + 'nodes', headers=headers)
        node_id = []
        nodes = r.json()['items']
        for node in nodes:
            try:
                # Enterprise, Backbone, Lastmile...
                if node['network_type']['name'] == 'Enterprise':
                    node_id.append(node)
            except KeyError:
                # node_id.append(node['isp']['name']) #AWS, Azure, Alibaba, Google, Softlayer
                continue
        return jsonify(node_id)
    except KeyError:
        return redirect(url_for('homepage'))

@app.route("/products", methods=["GET"])
def products():
    if 'oauth_token' not in session:
        return redirect(url_for('homepage'))
    try:
        headers = {'Accept': 'application/json',
                   'Authorization': 'Bearer ' + session['oauth_token']}
        r = requests.get(base_url + 'products', headers=headers)
        products = r.json()['items']
        session['products'] = products
        return jsonify(products)
    except KeyError:
        return redirect(url_for('homepage'))

@app.route("/alltests", methods=['GET'])
def tests():
    if 'oauth_token' not in session:
        return redirect(url_for('homepage'))
    try:
        headers = {'Accept': 'application/json',
                   'Authorization': 'Bearer ' + session['oauth_token']}
        r = requests.get(base_url + 'tests', headers=headers)
        tests = r.json()
        session['tests'] = tests
        return jsonify(tests)
    except KeyError:
        return redirect(url_for('homepage'))

@app.route("/filteredtests", methods=['GET'])
def filtered_tests():
    if 'oauth_token' not in session:
        return redirect(url_for('homepage'))
    try:
        headers = {'Accept': 'application/json',
                   'Authorization': 'Bearer ' + session['oauth_token']}
        r = requests.get(base_url + 'tests', headers=headers)
        tests = r.json()['items']
        results = [[test[0]] for test in tests]
        session['filteredtests'] = results
        return jsonify(tests)
    except KeyError:
        return redirect(url_for('homepage'))

@app.route("/filterederrors", methods=["GET"])
def filterederrors():
    if 'oauth_token' not in session:
        return redirect(url_for('homepage'))
    try:
        headers = {'Accept': 'application/json',
                   'Authorization': 'Bearer ' + session['oauth_token']}
        r = requests.get(base_url + 'errors/raw', headers=headers)
        errors = r.json()['detail']['items']
        filterederrors = [[error['data_fields'][0], error['data_fields'][7], error['data_fields'][11], error['data_fields'][15]] for error in errors]
        return jsonify(filterederrors)
    except KeyError:
        return redirect(url_for('homepage'))

if __name__ == "__main__":
    # This allows us to use a plain HTTP callback   
    os.environ.get('OAUTHLIB_INSECURE_TRANSPORT')
    app.secret_key = os.urandom(24)
    app.run(debug=True)