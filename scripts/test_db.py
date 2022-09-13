#%% Imports and setups
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

if False:
    #%% test read DATA
    df_read = pd.read_sql_query('select * from "x_test_table"', con=engine_azure)

    #%% test delete DATA
    with engine_azure.connect() as con:
        con.execute("Delete FROM x_test_table")


#%% test insert data
# from sqlalchemy import String, INT
if False:
    df = pd.DataFrame(
        [[i, i, i, i, i] for i in range(2000)],
        columns=["PersonID", "LastName", "FirstName", "Address", "City"],
    )

    df.to_sql(
        con=engine_azure,
        name="x_test_table",
        if_exists="append",
        dtype={
            "PersonID": INT,
            "LastName": String(255),
            "FirstName": String(255),
            "Address": String(255),
            "City": String(255),
        },
        index=False,
        method="multi",
        chunksize=200,
    )
# %%
