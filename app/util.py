import hashlib, uuid, random
import requests
import jwt 
import datetime


salt = "MYSALT"  # generates a random uuid
encoded_salt = salt.encode() 

""" fake prices to lookup for unit testing purposes """
FAKE_PRICES = {
        'stok': 3.50
    }

def hash_password(password):
    """ WEEK 4 TODO: encrypt with sha512 & a salt """
    encoded_pw = password.encode()
    hashed_pw = hashlib.sha512(encoded_pw + encoded_salt).hexdigest()
    return hashed_pw

def api_key():
    api_key = ''.join(["%s" % random.randint(0, 9) for num in range(0, 15)])
    return api_key

def get_price(ticker):
    # if ticker in FAKE_PRICES.keys():
    #     return FAKE_PRICES[ticker]
    
    try: 
        response = requests.get('https://api.iextrading.com/1.0/stock/{}/previous'.format(ticker))
        data = response.json()
        return [data['symbol'], data['open']]
    except ValueError:
        return False


def encodeAuthToken(pk):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        'user': pk
    }
    token = jwt.encode(payload, 'secret-key', algorithm='HS256')
    return token

def decodeAuthToken(token):
    try:
        payload = jwt.decode(token, 'secret-key', algorithm='HS256')
        return payload
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Login please'
    except jwt.InvalidTokenError:
        return 'Nice try, invalid token. Login please'
