import json
import sys

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists
from config import colorful
from sys import platform
import os

with open("./config/config.json") as f:
    configure = json.load(f)

SQL_PAX_URL = '{DRIVER}://{UNAME}:{PASSWD}@{HOST}/{DB_NAME}'.format(
    DRIVER=configure['DB_DRIVER'],
    UNAME=configure['DB_USER'],
    PASSWD=configure['DB_PASSWD'],
    HOST=configure['DB_HOST'],
    PORT=configure['DB_PORT'],
    DB_NAME=configure['DB_NAME']
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


def backup():
    match sys.platform:
        case 'linux':
            try:
                os.system(f"mysqldump -h {configure['DB_HOST']} -u {configure['DB_USER']} -p{configure['DB_PASSWD']} > '.\\backups\\$(date +\"F_%H-%M-%S\").sql'")
            except:
                return False
        case 'win32':
            try:
                os.system(f"mysqldump -h {configure['DB_HOST']} -u {configure['DB_USER']} -p{configure['DB_PASSWD']} pax > .\\database\\backups\\pierdolę_windowsa.sql")
            except:
                return False
    return True


pax_engine = start(SQL_PAX_URL)
if check_engine(pax_engine):
    check_databases()

