import pandas as pd

import dash
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dcc, html

import utils

dash.register_page(__name__)


layout = dbc.Container(
    [
        dcc.Store(
            id="dummy_input_map",
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


# @dash.callback(
#     [
#         Output("data_grid", "data"),
#         Output("data_airports", "data"),
#         Output("selection_flight_dropdown", "options"),
#     ],
#     Input("data_grid_dummy", "data"),
# )
# def data(dummy):
#     df_all = pd.read_csv(
#         r"../../../data/data_flights.csv",
#     ).drop(["Unnamed: 0", "trace_id", "origin", "dest_city_code"], axis=1)

#     df_airports = pd.read_csv(r"../../../data/data_airports.csv")
#     dict_airports = (
#         airports.loc[:, ["aiport_lat", "airport_lon", "airport_code_IATA", "city_name"]]
#         .set_index("airport_code_IATA")
#         .to_dict()
#     )

#     missing_iata = [
#         "AYT",
#         "TSR",
#         "FRA",
#         "NUE",
#         "CPH",
#         "AUH",
#         "GVA",
#         "VIE",
#         "LPL",
#         "BHX",
#     ]
#     print('FIX ABOV CODES in to DB')
#     df_all = df_all[df_all.flight.str.contains()]

#     df_all["from_pl"] = df_all.flight.apply(lambda x: x[:3])
#     origins = ["ZAG", "SOF", "TSF", "LJU", "TRS"]

#     # options = df_all.flight.apply(lambda x: x if x[:3] in origins else '').unique()
#     options = df_all.flight[df_all.from_pl.isin(origins)].unique()
#     options_dict = [
#         {
#             "label": f"{dict_airports['city_name'][flight[:3]]}-{dict_airports['city_name'][flight[-3:]]}({dict_airports['country_name'][flight[-3:]]})-{dict_airports['city_name'][flight[:3]]}",
#             "value": flight,
#         }
#         for flight in options
#     ]

#     return df_all.to_json(orient="split"),


@dash.callback(Output("map-chart", "figure"), Input("dummy_input_map", "data"))
def map_render(countries):

    print(
        "do NOT PASS data back and forth from pd to dict and back to pd. just use dict"
    )

    # airports = pd.read_json(data, orient="split")

    airports = pd.read_csv(r"../../../data/data_airports.csv")

    ap_dict = (
        airports.loc[:, ["aiport_lat", "airport_lon", "airport_code_IATA", "city_name"]]
        .set_index("airport_code_IATA")
        .to_dict()
    )
    origins = ["TSF", "TRS", "ZAG", "LJU"]

    fig = go.Figure()
    for origin in origins:
        orig_lon = ap_dict["airport_lon"][origin]
        orig_lat = ap_dict["aiport_lat"][origin]

        fig.add_trace(  # LINES
            go.Scattermapbox(
                # lon = [orig_lon, dest_lon + offset],
                lon=[orig_lon, 77.34999999],
                lat=[orig_lat, 16.234999999],
                name="from ...",
                showlegend=False,
                mode="lines",
                line=dict(width=1, color="red"),
                opacity=0.9,
            )
        )

        fig.add_trace(
            go.Scattermapbox(  # MARKERS for the points of origins (moved this sections below because of hovers
                lon=[orig_lon],
                lat=[orig_lat],
                text=[origin],
                name=origin,
                # legendgroup=origin,
                hoverinfo="text",
                showlegend=True,
                mode="markers",
                marker=dict(size=9, color="green"),
            )
        )
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
    return fig
