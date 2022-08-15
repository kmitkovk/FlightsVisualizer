# import sqlalchemy
# from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
# from sqlalchemy import inspect
from sqlalchemy import create_engine

# import pyodbc
import urllib

import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
#%%

db_host = os.environ["DBHOST"]
db_pass = os.environ["DBPASS"]
db_u_name = os.environ["DBUSER"]
db_name = os.environ["DBNAME"]

# https://stackoverflow.com/questions/52450659/pyodbc-to-sqlalchemy-connection
#%%
# https://stackoverflow.com/questions/15750711/connecting-to-sql-server-2012-using-sqlalchemy-and-pyodbc
# https://chartio.com/resources/tutorials/how-to-execute-raw-sql-in-sqlalchemy/
# engine = create_engine(f"mssql+pyodbc://{db_u_name}:{db_pass}@{db_host}/{db_name}/?driver={driver}")

# driver = "ODBC+DRIVER+17+for+SQL+Server"
params = urllib.parse.quote_plus(
    rf"Driver=ODBC Driver 13 for SQL Server;Server=tcp:{db_host},1433;Database={db_name};Uid={db_u_name}@{db_host};Pwd={db_pass};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)  # urllib.parse.quote_plus for python 3
conn_str = "mssql+pyodbc:///?odbc_connect={}".format(params)
engine_azure = create_engine(conn_str, echo=True)


#%%

with engine_azure.connect() as con:

    rs = con.execute("SELECT * FROM x_test_table")

    for row in rs:
        print(row)
# %%
# setting AZURE DB CONN:https://stackoverflow.com/questions/53704187/connecting-to-an-azure-database-using-sqlalchemy-in-python
