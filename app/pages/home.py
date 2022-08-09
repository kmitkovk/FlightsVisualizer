"""Home page of the app."""
import random

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Input, Output, dcc, html

import utils

dash.register_page(__name__, path="/")

layout = [
    dbc.Row(
        dbc.Col(
            dbc.Container(
                [
                    dcc.Dropdown(
                        id="as-filter",
                        options=[
                            {"label": "ff", "value": "ff"},
                            {"label": "ffs", "value": "ffs"},
                        ],
                        value="SI",
                        clearable=False,
                        searchable=False,
                        className="dropdown",
                    ),
                    dcc.Graph(
                        id="-chart",
                        config={"displayModeBar": False},
                    ),
                ],
            ),
            width=8,
            className="tight",
        ),
        justify="center",
        className="tight",
    )
]
