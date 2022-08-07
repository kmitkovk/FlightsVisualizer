import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html

import utils

dash.register_page(__name__)

layout = dbc.Container(
    [
        html.Div(
            className="app-content",
            children=[
                html.H1(children="Subpage 3"),
            ],
        ),
        dbc.Card(
            [
                dbc.CardHeader("Cardh"),
                dbc.CardBody(
                    [
                        html.H4("Card title", className="card-title"),
                        dcc.Dropdown(
                            options=["1", "2", "3", "4"],
                            value="1",
                            clearable=False,
                            multi=False,
                            id="sd-dd",
                        ),
                        dcc.Markdown(id="text-fsld"),
                    ]
                ),
                dbc.CardFooter(" footer"),
            ],
        ),
    ]
)
