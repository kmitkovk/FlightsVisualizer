from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, FLOAT
from config import CONN_STR

engine_azure = create_engine(CONN_STR, echo=True)

data_tables = ["FV_AIRPORTS_SS", "FV_FLIGHTS", "FV_AIRPORTS_ALL"]

#%% All airports

df_airports_all = pd.read_csv(r"data/data_airports_all.csv")
df_airports_all = df_airports_all.dropna(subset=["iata_code"])

df_airports_all.to_sql(
    con=engine_azure,
    name="FV_AIRPORTS_ALL",
    if_exists="append",  #'append'
    dtype={
        "ident": String(255),
        "type": String(255),
        "name": String(255),
        "elevation_ft": FLOAT,
        "continent": String(255),
        "iso_country": String(255),
        "iso_region": String(255),
        "municipality": String(255),
        "gps_code": String(255),
        "iata_code": String(255),
        "local_code": String(255),
        "coordinates": String(255),
    },
    index=False,
    method="multi",
    chunksize=100,
)

#%% SS airports

df_airports = pd.read_csv(r"data/data_airports.csv", index_col=0)

df_airports.to_sql(
    con=engine_azure,
    name="FV_AIRPORTS_SS",
    if_exists="append",  #'append'
    dtype={
        "ident": String(255),
        "type": String(255),
        "name": String(255),
        "elevation_ft": FLOAT,
        "continent": String(255),
        "iso_country": String(255),
        "iso_region": String(255),
        "municipality": String(255),
        "gps_code": String(255),
        "iata_code": String(255),
        "local_code": String(255),
        "coordinates": String(255),
    },
    index=False,
    method="multi",
    chunksize=100,
)

#%% Test

if False:
    #%% test read DATA
    df_read = pd.read_sql_query('select * from "x_test_table"', con=engine_azure)
    df_read = pd.read_sql_query('select * from "FV_AIRPORTS_ALL"', con=engine_azure)
    df_read = pd.read_sql_query('select * from "FV_AIRPORTS_SS"', con=engine_azure)

    #%% test delete DATA
    with engine_azure.connect() as con:
        con.execute("Delete FROM x_test_table")
