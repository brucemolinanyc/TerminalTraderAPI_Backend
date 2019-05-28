import sqlite3
import os

DIR = os.path.dirname(__file__)
DBFILENAME = "ttrader.db"
DBPATH = os.path.join(DIR, DBFILENAME)


def schema(dbpath=DBPATH):
    with sqlite3.connect(dbpath) as conn:
        cur = conn.cursor()
        DROPSQL = "DROP TABLE IF EXISTS {tablename};"

        cur.execute(DROPSQL.format(tablename="accounts"))

        SQL = """CREATE TABLE accounts(
                pk INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(16) NOT NULL,
                password_hash VARCHAR(128),
                api_key VARCHAR(128),
                balance INTEGER
            );"""

        cur.execute(SQL)

        cur.execute(DROPSQL.format(tablename="positions"))

        SQL = """CREATE TABLE positions(
            pk INTEGER PRIMARY KEY AUTOINCREMENT,
            accounts_pk INT,
            ticker VARCHAR(4) NOT NULL,
            shares INT,
            FOREIGN KEY(accounts_pk) REFERENCES accounts(pk),
            UNIQUE(accounts_pk, ticker)
            );"""

        cur.execute(SQL)

        cur.execute(DROPSQL.format(tablename="trades"))

        SQL = """CREATE TABLE trades(
            pk INTEGER PRIMARY KEY AUTOINCREMENT,
            accounts_pk INT,
            ticker VARCHAR(4) NOT NULL,
            volume INT,
            price FLOAT,
            time FLOAT,
            FOREIGN KEY(accounts_pk) REFERENCES accounts(pk)
            );"""

        cur.execute(SQL)


