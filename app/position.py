from app.orm import ORM
from app.util import get_price


class Position(ORM):

    tablename = 'positions'
    fields = ['accounts_pk', 'ticker', 'shares']

    # tablename = "todoitems"

    def __init__(self, *args, **kwargs):
        self.pk = kwargs.get('pk')
        self.accounts_pk = kwargs.get('accounts_pk')
        self.ticker = kwargs.get('ticker')
        self.shares = kwargs.get('shares')

    def current_value(self):
        """ current value of this postion at the current market rate. returns
        a float """
        return 0.0

    