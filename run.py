#! /usr/bin/env python3
import os
from app.orm import ORM
from app import controller

DIR = os.path.dirname(__file__)
DBFILENAME = 'ttrader.db'
DBPATH = os.path.join(DIR, 'data', DBFILENAME)

# child classes default to ORM'm dbpath if it is not set
ORM.dbpath = DBPATH
controller.run()
