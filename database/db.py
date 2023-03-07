import json
import sqlalchemy
from sqlalchemy import create_engine
from config import colorful
with open("config/db.json") as f:
    dbc = json.load(f) # database config

# Creating the SQLAlchemy for later.
print("Creating SQLAlchemy connection engine")
try:
    engine = create_engine(f"mysql+pymysql://{dbc['Muser']}:{dbc['Mpassword']}@{dbc['Mip']}/{dbc['Mdb']}\
    ?charset=utf8mb4", pool_size=50, max_overflow=20)
except:
    print("An error occurred.")
    pass

