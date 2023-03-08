import json
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists
from config import colorful
with open('config/db.json') as f:
    dbconfig = json.load(f)# database config
from sys import platform
import os

SQL_PAX_URL = '{DRIVER}://{UNAME}:{PASSWD}@{HOST}/{DB_NAME}'.format(
    DRIVER=dbconfig['DB_DRIVER'],
    UNAME=dbconfig['DB_USER'],
    PASSWD=dbconfig['DB_PASSWD'],
    HOST=dbconfig['DB_HOST'],
    PORT=dbconfig['DB_PORT'],
    DB_NAME=dbconfig['DB_NAME']
)


def start(url):
    print("Creating SQLAlchemy connection engine.")
    #try:
    return create_engine(url, pool_size=50, max_overflow=10)
    #except:
    #    print("An error occurred.")
    #    return None


def check_engine(eng):
    if eng is None:
        print("Engine not present.")
        return False
    else:
        print("Engine present.")
        return True


def check_databases():
    if not database_exists(SQL_PAX_URL):
        print("Main database not found! Creating an empty database. Please load back-up ASAP!")
        # create_database(SQL_PAX_URL)
    else:
        print("Main database present.")


def backup(action):
    pass


pax_engine = start(SQL_PAX_URL)
if check_engine(pax_engine):
    check_databases()

