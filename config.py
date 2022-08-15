# -*- coding: utf-8 -*-
"""
Created on Tue May  3 21:17:05 2022

@author: krasimirk
"""

import urllib
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

db_host = os.environ["DBHOST"]
db_pass = os.environ["DBPASS"]
db_u_name = os.environ["DBUSER"]
db_name = os.environ["DBNAME"]
local_dev = os.environ["LOCAL_DEVELOPMENT"]

# https://stackoverflow.com/questions/52450659/pyodbc-to-sqlalchemy-connection
# https://stackoverflow.com/questions/15750711/connecting-to-sql-server-2012-using-sqlalchemy-and-pyodbc
# https://chartio.com/resources/tutorials/how-to-execute-raw-sql-in-sqlalchemy/

# workaround for the ODBC versions but correct way should be described here:  https://stackoverflow.com/questions/53704187/connecting-to-an-azure-database-using-sqlalchemy-in-python
if local_dev == "true":
    odbc_vers = 13
else:
    odbc_vers = 17

params = urllib.parse.quote_plus(
    rf"Driver=ODBC Driver {odbc_vers} for SQL Server;Server=tcp:{db_host},1433;Database={db_name};Uid={db_u_name}@{db_host};Pwd={db_pass};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)  # urllib.parse.quote_plus for python 3
CONN_STR = "mssql+pyodbc:///?odbc_connect={}".format(params)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
}


SLEEP_TIME_SHORT = 5  # in seconds so we will randomly get up to 3 seconds sleep
SLEEP_TIME_LONG = 10  # in seconds so we will randomly get up to 3 seconds sleep

ORIGIN_AIRPORTS = {
    "Venice": "VCE",
    "Treviso": "TSF",
    "Trieste": "TRS",
    "Ljubljana": "LJU",
    "Zagreb": "ZAG",
    "Sofia": "SOF",
}
