from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, FLOAT, DATETIME
from config import CONN_STR
import pandas as pd

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
        "continent": String(255),
        "country_name": String(255),
        "country_code_iso2": String(255),
        "region_name": String(255),
        "city_name": String(255),
        "city_code": String(255),
        "city_image_url": String(255),
        "airport_name": String(255),
        "airport_code_IATA": String(255),
        "airport_type": String(255),
        "airport_lat": FLOAT,
        "airport_lon": FLOAT,
    },
    index=False,
    method="multi",
    chunksize=100,
)

#%% Flights data

df_flights = pd.read_csv(r"data/data_flights.csv", index_col=0).drop('trace_id',axis=1)

df_flights.to_sql(
    con=engine_azure,
    name="FV_FLIGHTS",
    if_exists="append",  #'append'
    dtype={
        "flight": String(255),
        "departure_date": DATETIME,
        "price": FLOAT,
        "origin": String(255),
        "dest_city_code": String(255),
        "timestamp": DATETIME,
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
    df_read = pd.read_sql_query('select * from "FV_FLIGHTS"', con=engine_azure)

    #%% test delete DATA
    with engine_azure.connect() as con:
        # con.execute("Deletee FROM FV_AIRPORTS_SS")
        con.execute("""
        select * from FV_AIRPORTS_SS
        where city_code like 'RUHA'
        """)
