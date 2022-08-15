import pandas as pd

import dash
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dcc, html

from sqlalchemy import create_engine
import urllib
import os
from dotenv import load_dotenv

dash.register_page(__name__)

load_dotenv()  # take environment variables from .env.

origins = ["TSF", "TRS", "ZAG", "LJU"]  # "SOF"

db_host = os.environ["DBHOST"]
db_pass = os.environ["DBPASS"]
db_u_name = os.environ["DBUSER"]
db_name = os.environ["DBNAME"]

params = urllib.parse.quote_plus(
    rf"Driver=ODBC Driver 17 for SQL Server;Server=tcp:{db_host},1433;Database={db_name};Uid={db_u_name}@{db_host};Pwd={db_pass};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)  # urllib.parse.quote_plus for python 3
conn_str = "mssql+pyodbc:///?odbc_connect={}".format(params)
engine_azure = create_engine(conn_str, echo=True)


layout = dbc.Container(
    [
        dcc.Store(
            id="data_map_airports",
        ),
        dcc.Store(
            id="data_map_flights",
        ),
        dcc.Store(
            id="dummy_input_map",
        ),
        dcc.Loading(
            id="loading-map",
            type="default",
            children=html.Div(id="loading-output-map"),
        ),
        dbc.Row(
            dbc.Col(
                [
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H4(
                                        "Map destinations",
                                        className="card-title",
                                    ),
                                    dcc.Graph(id="map-chart"),
                                ]
                            )
                        ],
                    ),
                ],
                align="center",
            ),
        ),
    ],
)


@dash.callback(
    [
        Output("data_map_flights", "data"),
        Output("data_map_airports", "data"),
    ],
    Input("dummy_input_map", "data"),
)
def data_map(dummy):
    df_flights = pd.read_csv(
        r"data/data_flights.csv",
    ).drop(["Unnamed: 0", "trace_id", "origin", "dest_city_code"], axis=1)

    df_flights = df_flights[df_flights.flight.apply(lambda x: x[:3]).isin(origins)]

    # here we need an additional transofrmation next to timestamp since at the same
    # minute for the same flight we scrape multiple dates (departure) at the same time
    # which means that grouping by flight and timestamp only will still give us the same
    # flight only the difference will be the departure dates
    df_flights = df_flights[
        df_flights.timestamp == df_flights.groupby("flight").timestamp.transform(max)
    ]
    df_flights = df_flights[
        df_flights.departure_date
        == df_flights.groupby("flight").departure_date.transform(max)
    ]

    print("above maybe you wanna be able to select specific month")
    print("otherwise you gotta provide a range of months with average departure price")
    print(
        "or maybe even calculate round trip... all this should be provided in options"
    )

    df_airports = pd.read_csv(r"data/data_airports.csv")
    df_airports = df_airports.loc[
        :,
        [
            "airport_lat",
            "airport_lon",
            "airport_code_IATA",
            "city_name",
            "country_name",
        ],
    ].set_index("airport_code_IATA")

    df_airports_dict = df_airports.to_dict()

    df_flights["dest"] = df_flights.flight.apply(lambda x: x[-3:])
    df_flights["dest_lon"] = df_flights.dest.apply(
        lambda x: df_airports_dict["airport_lon"][x]
    )
    df_flights["dest_lat"] = df_flights.dest.apply(
        lambda x: df_airports_dict["airport_lat"][x]
    )

    df_flights["orig"] = df_flights.flight.apply(lambda x: x[:3])
    # df_flights['orig_lon'] = df_flights.orig.apply(lambda x: df_airports_dict['airport_lon'][x])
    # df_flights['orig_lat'] = df_flights.orig.apply(lambda x: df_airports_dict['airport_lat'][x])

    return (df_flights.to_json(orient="split"), df_airports.to_json(orient="split"))


@dash.callback(
    [
        Output("map-chart", "figure"),
        Output("loading-output-map", "children"),
    ],
    [Input("data_map_flights", "data"), Input("data_map_airports", "data")],
)
def map_render(flights, airports):

    df_flights = pd.read_json(flights, orient="split")
    df_airports = pd.read_json(airports, orient="split")

    highest_price = df_flights.price.max()
    # colors = px.colors.sequential.Viridis
    # colors = ['red','green','darkorange','blue']
    colors = [
        "rgb(102,102,102)",
        "rgb(27,158,119)",
        "rgb(217,95,2)",
        "#750D86",
        # "violet",
    ]  # px.colors.qualitative.Dark2 #https://plotly.com/python/discrete-color/
    skip = int(len(colors) / len(origins))
    assert len(colors) >= len(origins), "Not enough colors for all cities"

    # offset destination if there are more than two routes to it
    # cities = [city[0] for city in city_countries]
    # dest_repetition = {city:{'rep':cities.count(city),'offset':0}
    #                     for city in cities if cities.count(city) > 1}
    # duplicates handle
    # df_routes[df_routes.dest_city.duplicated()]

    num_dest = 0
    dest_offset = 0
    count = 0

    fig = go.Figure()
    for origin in origins:
        # link = f"https://www.skyscanner.net/transport/flights/{origin}/{i.dest_city_code}/?adultsv2=1&cabinclass=economy&childrenv2=&inboundaltsenabled=false&iym={iym}&outboundaltsenabled=false&oym={oym}&selectedoday=12&selectediday=12"

        orig_lon = df_airports.loc[origin, "airport_lon"]
        orig_lat = df_airports.loc[origin, "airport_lat"]

        show_legend = True
        for row in df_flights[df_flights.orig == origin].iterrows():
            dest_iata_code = row[1].dest
            dest_lon = row[1].dest_lon
            dest_lat = row[1].dest_lat
            dest_price = row[1].price
            dest_city_name = df_airports.loc[dest_iata_code, "city_name"]
            dest_country_name = df_airports.loc[dest_iata_code, "country_name"]

            fig.add_trace(  # LINES
                go.Scattermapbox(
                    # lon = [orig_lon, dest_lon + offset],
                    lon=[orig_lon, dest_lon],
                    lat=[orig_lat, dest_lat],
                    name=f"from {dest_city_name}",
                    legendgroup=origin,
                    showlegend=False,
                    mode="lines",
                    # text=[i.dest_city + f" from {origin} from €{int(i.dest_price_dir)}"],
                    # hoverinfo="text",
                    line=dict(width=1, color=colors[count]),
                    opacity=(1 - (dest_price / highest_price)) * 0.5,
                )
            )

            show_legend = False
            fig.add_trace(
                go.Scattermapbox(  # MARKERS
                    # lon = [dest_lon + offset],
                    lon=[dest_lon],
                    lat=[dest_lat],
                    text=[
                        dest_city_name
                        + f", {dest_country_name} from €{int(dest_price)}"
                    ],
                    hoverinfo="text",
                    mode="markers",
                    legendgroup=origin,
                    showlegend=False,
                    # customdata=[link],
                    line=dict(width=1, color=colors[count]),
                    opacity=1 - (dest_price / highest_price),
                )
            )

        fig.add_trace(
            go.Scattermapbox(  # MARKERS for the points of origins (moved this sections below because of hovers
                lon=[orig_lon],
                lat=[orig_lat],
                text=[origin],
                name=df_airports.loc[origin, "city_name"],
                legendgroup=origin,
                hoverinfo="text",
                showlegend=True,
                mode="markers",
                marker=dict(size=9, color=colors[count]),
            )
        )

        count += skip

    print(
        "FIX LINES SO THEY ARE CURVED AND gradient: https://plotly.com/python/lines-on-maps/"
    )
    fig.update_layout(  # https://plotly.com/python/mapbox-layers/
        # title_text="Number of destinations at price €capp",
        legend_title_text="<br><b>From airport:</b><br>"
        + "<sub>[double-click to filter]</sub><br>",
        title_x=0.5,
        # autosize=True,
        # hovermode='closest',
        geo=dict(
            projection=dict(
                type="orthographic", rotation=dict(lon=-500, lat=290, roll=23)
            ),
        ),
        mapbox_style="carto-positron",  # "open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain", "stamen-toner" or "stamen-watercolor"
        mapbox=dict(
            # accesstoken=mapbox_access_token,
            center=dict(lat=46.063562, lon=14.48854),
            zoom=3.1,
        ),
        margin=dict(l=5, r=5, t=5, b=5),
    )

    with engine_azure.connect() as con:
        rs = con.execute("SELECT * FROM x_test_table")
        for row in rs:
            print(row)

    return fig, None
