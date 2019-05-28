from flask import jsonify, abort, request, make_response, current_app
from flask_app import app
from app import Account
from app import Position
from app.util import get_price, hash_password, encodeAuthToken, decodeAuthToken
import jwt
import datetime

UNAUTHORIZED = {"error": "unauthorized", "status_code": 401}
NOT_FOUND = {"error": "not found", "status_code": 404}
APP_ERROR = {"error": "application error", "status_code": 500}
BAD_REQUEST = {"error": "bad request", "status_code": 400}

@app.errorhandler(404)
def error404():
    return jsonify({"error": "404 not found"}), 404 

@app.errorhandler(500) 
def error500():
    return jsonify({"error": "application error"}), 500
    
@app.route('/user/<id>')
def user(id):
        user = Account.one_from_pk(id)
        if user.balance is None:
            user.balance = 0 
        return jsonify({"user": user.username, "balance":user.balance})

@app.route('/login', methods=['POST', 'GET'])
def login():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return jsonify(BAD_REQUEST), 401
    account = Account.login(request.json['username'], request.json['password'])
    if not account:
        return jsonify(UNAUTHORIZED), 401
    token = encodeAuthToken(account.pk)
    return jsonify({'status': 'success', 'auth_token': str(token), 'api_key':account.api_key}) 

@app.route('/create', methods=['GET', 'POST'])
def create():
    if not request.json or 'username' not in request.json or 'password_hash' not in request.json:
        return jsonify(BAD_REQUEST), 401
    account = Account(username = request.json['username'], password_hash =request.json['password_hash'])
    hashed_pw = Account.set_password(account, request.json['password_hash'])
    account.set_api_key()
    account.save()
    token = encodeAuthToken(account.pk)
    return jsonify({'status': 'success', 'auth_token': str(token), 'api_key':account.api_key}) 

#works
@app.route('/api/price/<ticker>', methods=['GET'])
def lookup(ticker):
    response = get_price(ticker)
    if response:
        return jsonify({"symbol": response[0], "price": response[1]})
    else:
        return jsonify({"error": "404 not found"}), 404 

#works
@app.route('/api/<api_key>/positions', methods=['GET'])
def positions(api_key):
    account = Account.authenticate_api(api_key)
    if not account:
        return jsonify({"error": "authentication error"}), 401
    positions = account.get_positions_json()
    return jsonify({"positions": positions})


@app.route('/api/<api_key>/position/<ticker>', methods=['GET'])
def position(api_key, ticker):
    account = Account.authenticate_api(api_key)
    if not account:
        return jsonify({"error": "authentication error"}), 401
    positions = account.get_positions()
    for posish in positions:
        if posish.ticker == ticker:
            return jsonify({"position": posish.ticker, "shares": posish.shares})
    return jsonify({"error": "404 not found"}), 404 
  

@app.route('/api/<api_key>/trades/<ticker>', methods=['GET'])
def trades(api_key, ticker):
    account = Account.authenticate_api(api_key)
    if not account:
            return jsonify({"error": "authentication error"}), 401
    ticker_trades = account.get_trades_by_ticker_json(ticker)
    return jsonify({"trades": ticker_trades})
    
@app.route('/api/<api_key>/alltrades', methods=['GET'])
def alltrades(api_key):
    account = Account.authenticate_api(api_key)
    if not account:
        return jsonify({"error": "authentication error"}), 401
    else:
        all_trades = account.get_all_trades_json()
        return jsonify({"trades": all_trades})


@app.route('/api/<api_key>/balance', methods=['GET'])
def balance(api_key):
    account = Account.authenticate_api(api_key)
    if not account:
        return jsonify({"error": "authentication error"}), 401
    return jsonify({"username": account.username, "balance": account.balance})

@app.route('/api/<api_key>/deposit', methods=['PUT'])
def deposit(api_key):
    account = Account.authenticate_api(api_key)
  
    if not account:
        return jsonify({"error": "authentication error"}), 401
    if not request.json:
        return jsonify({"error": "bad request"}), 400
    try:
        amount = request.json['amount']
        if int(amount) < 0.0:
            raise ValueError
        if account.balance is None:
            account.balance = 0 
        account.balance += int(amount)
    except (ValueError, KeyError):
        return jsonify({"error": "bad request"}), 400
    account.save()
    return jsonify({"username": account.username, "balance": account.balance})

@app.route('/api/<api_key>/sell/<ticker>/<amount>', methods=['POST'])
def sell(api_key, ticker, amount):
    account = Account.authenticate_api(api_key) 
    position = account.get_position_for(ticker)

    if request.json['amount'] and request.json['ticker'] and (position.shares >= int(amount)):
        account.sell(ticker, amount)
        return jsonify({"username": account.username, "balance": account.balance})
    else:
        return jsonify({"error": "bad request"}), 400
    # if not account:
    #     return jsonify({"error": "authentication error"}), 401
    # if not ticker:
    #     return jsonify({ "error": "bad ticker data"})
    # if not request.json:
    #     return jsonify({"error": "bad request"}), 400

    
    

@app.route('/api/<api_key>/buy/<ticker>/<amount>', methods=['POST'])
def buy(api_key, ticker, amount):
    account = Account.authenticate_api(api_key)
    price = get_price(ticker)[1]
    if not price:
        return jsonify({ "error": "bad ticker data"})

    purchase = int(amount) * price
    if request.json['amount'] and request.json['ticker'] and account.balance > int(purchase):
        account.buy(ticker, amount, price, purchase)
        return jsonify({"username": account.username, "balance": account.balance})
    else:
        return jsonify({ "error": "bad ticker data"})
    if account.balance < purchase:
        return jsonify({"error": "bad request"}), 400
    if not account:
        return jsonify({"error": "authentication error"}), 401
    if not request.json:
        return jsonify({"error": "bad request"}), 400
    
    # if request.json['amount'] and request.json['ticker'] and account.balance > purchase:
    #     account.buy(ticker, int(amount), int(price), purchase)
    #     return jsonify({"username": account.username, "balance": account.balance})
    # elif account.balance < purchase:
    #     return jsonify({"error": "bad request"}), 400
           
@app.route('/api/accounts', methods=['GET'])
def accounts():
    accounts_dic = {}
    accounts = Account.all()
    for account in accounts:
        accounts_dic[account.username] = {
            "username": account.username,
            "balance": account.balance,
            "api-key": account.api_key
        }
    return jsonify({"accounts": accounts_dic})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def react_path(path):
    return app.send_static_file('index.html')