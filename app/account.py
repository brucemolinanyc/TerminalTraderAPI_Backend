import sqlite3
from app.orm import ORM
from app.util import hash_password
from app.util import get_price
from app.util import api_key
from app.position import Position
from app.trade import Trade
from app.util import hash_password
from app.view import View 
from datetime import datetime
import json

class Account(ORM):
    tablename = "accounts"
    fields = ["username", "password_hash", "balance", "api_key"]

    def __init__(self, *args, **kwargs):
        self.pk = kwargs.get('pk')
        self.username = kwargs.get('username')
        self.password_hash = kwargs.get('password_hash')
        self.api_key = kwargs.get('api_key')
        self.balance = kwargs.get('balance')
        self.api_key = kwargs.get('api_key')

    @classmethod
    def login(cls, username, password):
        return cls.select_one_where("WHERE username = ? AND password_hash = ?",
                                    (username, hash_password(password)))

    @classmethod
    def authenticate_api(cls,key):
        return cls.select_one_where("WHERE api_key = ?", (key,))

    def set_password(self, password):
        hashed_pw = hash_password(password)
        self.password_hash = hashed_pw 
        return hashed_pw

    def set_api_key(self):
        key = api_key()
        self.api_key = key
        return api_key

    def get_positions(self):
        view = View()
        positions = Position.select_many_where("WHERE accounts_pk = ?", (self.pk, ))

        for position in positions:
            view.positions(self, position)
        return positions

    def get_positions_json(self):
        positions = []
        all_positions = Position.select_many_where("WHERE accounts_pk = ?", (self.pk, ))
        for position in all_positions:
            posish = {}
            posish[position.ticker] = {"ticker": position.ticker, "shares": position.shares}
            positions.append(posish)
        return positions

    def get_position_for(self, ticker):
        """ return a specific Position object for the user. if the position does not
        exist, return a new Position with zero shares. Returns a Position object """
        position = Position.select_one_where(
            "WHERE ticker = ? AND accounts_pk = ?", (ticker, self.pk))
        if position is None:
            return Position(ticker=ticker, accounts_pk=self.pk, shares=0)
        return position

    def get_trades(self):
        """ return all of the user's trades ordered by time. returns a list of
        Trade objects """
        return Trade.select_many_where("WHERE accounts_pk = ?", (self.pk, ))

    def get_all_trades_json(self):
        all_trades = []
        trades = Trade.select_many_where("WHERE accounts_pk = ?", (self.pk, ))      
        
        for trade in trades:
            one_trade = {}
            ts = int(trade.time)
            timestamp = datetime.utcfromtimestamp(ts).strftime('%m-%d-%Y, %H:%M:%S')

            one_trade[trade.pk] = {"ticker": trade.ticker, "volume": trade.volume, "price":trade.price, "time": timestamp}
            all_trades.append(one_trade)
        return all_trades

    def trades_for(self, ticker):
        """ return all of a user's trades for a given ticker """
        return Trade.select_many_where("WHERE accounts_pk = ? AND ticker = ?", (self.pk, ticker))

    def get_trades_by_ticker_json(self, ticker):
        trades = {}
        ticker_trades = Trade.select_many_where("WHERE accounts_pk = ? AND ticker = ?", (self.pk, ticker))
        if ticker_trades:
            for trade in ticker_trades:
                trades[trade.pk] = {"ticker": trade.ticker, "volume": trade.volume, "price":trade.price, "time": trade.time}
        return trades
        

    def buy(self, ticker, amount, current_price, total_cost):
        """ make a purchase. raise KeyError for a non-existent stock and
        ValueError for insufficient funds. will create a new Trade and modify
        a Position and alters the user's balance. returns nothing """
        position = self.get_position_for(ticker)
    
        trade = Trade(accounts_pk = self.pk, ticker=ticker, price=current_price, volume = amount)
        self.balance -= int(total_cost)
        position.shares += int(amount)
        position.save()
        trade.save()
        self.save()
        

    def sell(self, ticker, amount):
        """ make a sale. raise KeyErrror for a non-existent stock and
        ValueError for insufficient shares. will create a new Trade object,
        modify a Position, and alter the self.balance. returns nothing."""
        position = self.get_position_for(ticker)
        
        price = get_price(ticker)[1]
        trade = Trade(accounts_pk = self.pk, ticker=ticker, price=price, volume= -int(amount))
        position.shares -= int(amount)
        self.balance += int(amount) * price
        position.save()
        trade.save()
        self.save()