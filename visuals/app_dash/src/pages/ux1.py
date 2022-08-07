import pandas as pd

import dash
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dcc, html

import utils

dash.register_page(__name__)


layout = dbc.Container(
    dbc.Row(
        dbc.Col(
            [
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H4(
                                    "test1",
                                    className="card-title",
                                ),
                                html.P(
                                    "test:",
                                    className="card-text",
                                ),
                                dcc.Dropdown(
                                    options=[1,2,3],
                                    value=["GG"],
                                    clearable=False,
                                    multi=True,
                                    id="dd",
                                ),
                                dcc.Graph(id="map-chart"),
                            ]
                        )
                    ],
                ),
            ],
            align="center",
        ),
    )
)



@dash.callback(Output("map-chart", "figure"), Input("dd", "value"))
def asfsad(countries):

    fig = go.Figure()
        
    fig.add_trace( #LINES
    go.Scattermapbox(
    # lon = [orig_lon, dest_lon + offset],
    lon = [52.35138889, 51.88499832],
    lat = [13.49388889, 0.234999999],
                        name = 'from ...',
    showlegend=False,
    mode = 'lines',
    line = dict(width = 1,color = 'red'),
    opacity = 0.9,
                )
            )
    
    
    fig.update_layout( #https://plotly.com/python/mapbox-layers/
    title_text = "Number of destinations at price €capp",
    legend_title_text='<br><b>From airport:</b><br>'+'<sub>[double-click to filter]</sub><br>',
    title_x=0.5,
    # autosize=True,
    # hovermode='closest',
    mapbox_style="carto-positron", #"open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain", "stamen-toner" or "stamen-watercolor" 
    mapbox=dict(
        # accesstoken=mapbox_access_token,
        center=dict(lat = 46.063562, lon = 14.48854),
        zoom=3.5),
                )
    return fig

