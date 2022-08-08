
import dash
import dash_bootstrap_components as dbc
from dash import html

dash.register_page(__name__)

layout = html.Div(
    [
        dbc.Container(
            dbc.Row(
                dbc.Col(
                    [
                        html.H1("Error 404: Page not found!"),
                            dbc.Nav(
                                dbc.NavItem(dbc.NavLink("Back to home page", href="/", active=True)),
                                pills=True
                            ),
                    ],
                    align="center",
                ),
            )
        )
    ]
)
