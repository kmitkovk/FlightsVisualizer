import pandas as pd
import datetime

import dash
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.figure_factory as ff
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
                                    "tes2",
                                    className="card-title",
                                ),
                                html.P(
                                    "test:",
                                    className="card-text",
                                ),
                                dcc.Dropdown(
                                    options=[1, 2, 3],
                                    value=["GG"],
                                    clearable=False,
                                    multi=True,
                                    id="s-dd",
                                ),
                                dcc.Graph(id="s-chart"),
                            ]
                        )
                    ],
                ),
            ],
            align="center",
        ),
    )
)


@dash.callback(Output("s-chart", "figure"), Input("s-dd", "value"))
def update_output(countries):

    # Source: https://plotly.com/python/gantt/
    df = pd.DataFrame(
        [
            dict(
                Task="Job A", Start="2021-01-08", Finish="2021-01-29", Completion_pct=50
            ),
            dict(
                Task="Job B", Start="2021-01-15", Finish="2021-02-12", Completion_pct=60
            ),
            dict(
                Task="Job C", Start="2021-01-29", Finish="2021-02-19", Completion_pct=70
            ),
            dict(
                Task="Job D", Start="2021-02-05", Finish="2021-02-26", Completion_pct=80
            ),
        ]
    )

    fig = px.timeline(
        df, x_start="Start", x_end="Finish", y="Task", color="Completion_pct"
    )

    # my_figure = ff.create_gantt(df, showgrid_x=True, showgrid_y=True)
    weeks_ticktext = ["KW: 01 ('21)", "", "", "", "KW: 05 ('21)", "", "", "", ""]
    weeks_tickvals = [
        datetime.datetime(2021, 1, 4, 0, 0),
        datetime.datetime(2021, 1, 11, 0, 0),
        datetime.datetime(2021, 1, 18, 0, 0),
        datetime.datetime(2021, 1, 25, 0, 0),
        datetime.datetime(2021, 2, 1, 0, 0),
        datetime.datetime(2021, 2, 8, 0, 0),
        datetime.datetime(2021, 2, 15, 0, 0),
        datetime.datetime(2021, 2, 22, 0, 0),
        datetime.datetime(2021, 3, 1, 0, 0),
    ]
    fig.layout.xaxis["tickmode"] = "array"
    fig.layout.xaxis["tickvals"] = weeks_tickvals
    fig.layout.xaxis["ticktext"] = weeks_ticktext

    return fig
