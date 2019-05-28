from app.account import Account
from app.view import View 
from app.util import get_price 
import time 

view = View()

def run():
    welcome_homepage()


def welcome_homepage():
    while True:  
        selection = view.welcome_screen()
        if selection not in ["1","2","3"]:
            view.improper_selection()
            continue 

        if selection == "1":
            username, balance, password, confirm_password = view.get_username(), view.add_balance(), view.get_password(), view.confirm_password() 

            if password != confirm_password:
                view.improper_password()
                continue  
            if not balance.isdigit() or int(balance) < 0:
                view.improper_balance()
                continue
            
            account = Account(username = username, balance = balance)
            hashed_pw = Account.set_password(account, password)
            account.set_api_key()
            account.save()
            logged_in_homepage(account)
            return 
        elif selection == "2":
            username, password = view.get_username(), view.get_password()
            logged_in_account = Account.login(username=username, password=password)
            
            if logged_in_account:
                logged_in_homepage(logged_in_account)
                return
            else:
                print("Invalid credentials supplied")
                continue
        elif selection == "3":
            view.goodbye()
            return


def logged_in_homepage(account):
    
    while True:
        selection = view.logged_in_screen(account.username, account.api_key, account.balance)
        
        if selection not in ["1", "2", "3", "4", "5", "6", "7", "8"]:
            view.improper_selection()
            time.sleep(3)
        
        if selection == "1":
            view.account_positions(account.username)
            Account.get_positions(account)
            time.sleep(3)
        elif selection == "2":
            deposit = view.deposit_funds()
            if not deposit.isdigit() or int(deposit) < 1:
                view.improper_balance()
                time.sleep(3)
            else:
                account.balance = int(account.balance) +  int(deposit)
                account.save()
                continue
        elif selection == "3":
            ticker_request = view.request_ticker_symbol()
            ticker_response = get_price(ticker_request)
            if type(ticker_response) == list:
                view.return_ticker_symbol_price(ticker_response)
                time.sleep(3)
            else:
                view.improper_ticker()
                time.sleep(3)
        elif selection == "4":
            ticker = view.request_ticker_symbol()
            ticker_price = get_price(ticker)
            if ticker_price == False:
                view.improper_ticker()
                time.sleep(3)
                continue
                 
            purchase_amount = view.get_shares(ticker_price)
            if not purchase_amount.isdigit():
                view.improper_money()
                time.sleep(3)
                continue

            total_cost = int(purchase_amount) * int(ticker_price[1])
            
            if total_cost < int(account.balance):
                Account.buy(account, ticker, purchase_amount, ticker_price[1], total_cost)
            elif int(total_cost) > int(account.balance):
                view.not_enough_money()
                time.sleep(3)

        elif selection == "5":
            Account.get_positions(account)
            time.sleep(3)
            ticker_to_sell = view.sell_shares()
            has_stock = get_price(ticker_to_sell)
            position = account.get_position_for(ticker_to_sell)
            amount = view.sell_shares_amount()

            if has_stock and position.shares >= int(amount):
                Account.sell(account, ticker_to_sell, amount)
            elif not has_stock:
                view.improper_ticker()
                time.sleep(3)
            else:
                view.not_enough_shares()
        elif selection == "6":
            selection = view.select_trade_option(account.username)
            
            if len(selection) != 1 or selection.lower() not in ["a", "b", "c"]:
                view.improper_selection()
                time.sleep(3)
            elif selection.lower() == "a":
                account_trades = Account.get_trades(account)
                if not account_trades:
                    view.no_trades(account.username)
                    time.sleep(3)
                for trade in account_trades:
                    view.show_trades(account.username, trade)
                    time.sleep(3)
            elif selection.lower() == "b":
                ticker_symbol = view.request_ticker_symbol()
                account_trades_by_ticker = Account.trades_for(account, ticker_symbol)
               
                if get_price(ticker_symbol) == False:
                    view.improper_ticker()
                    time.sleep(3)
                elif not account_trades_by_ticker:
                    view.no_trades(account.username)
                    time.sleep(3)              
                else:
                    for trade in account_trades_by_ticker:
                        view.show_trades(account.username, trade)
                        time.sleep(3)
            elif selection.lower() == "c":
                continue
        elif selection == "7":
            view.goodbye()
            welcome_homepage()
            return
        elif selection == "8":
            view.goodbye()
            return
        


"""TODO 
   develop the view for the login screen and the controller options for it
   see the below for inspiration
""" 



"""
Sample execution

Welcome to Terminal Trader!
    
    1. create account
    2. login
    3. quit

Your choice: 2.


Main Menu:

    1. see balance & positions
    2. deposit money
    3. look up stock price
    4. buy stock
    5. sell stock
    6. trade history

etc.


you should have useful output if a user inputs a stock that does not exist

you should not allow a user to spend money they don't have or sell
shares they don't have

your display of positions or trades should be well-formatted, don't
just print a python list
"""
