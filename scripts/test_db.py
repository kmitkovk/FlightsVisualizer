# import sqlalchemy
# from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
# from sqlalchemy import inspect
from sqlalchemy import create_engine
from config import CONN_STR

engine_azure = create_engine(CONN_STR, echo=True)


#%% Test out
with engine_azure.connect() as con:

    rs = con.execute("SELECT * FROM x_test_table")

    for row in rs:
        print(row)

#%% test insert data
