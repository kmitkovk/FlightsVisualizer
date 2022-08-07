import pandas as pd
import datetime

import dash
import dash_bootstrap_components as dbc

import plotly.express as px
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
    # Source: https://plotly.com/python-api-reference/generated/plotly.express.timeline.html
    # Colors: https://plotly.com/python/builtin-colorscales/
    # Colors: https://plotly.com/python/colorscales/

    data2 = {'flight': {1506: 'EIN_ZAG1', 1507: 'EIN_ZAG2', 1508: 'EIN_ZAG3', 1509: 'EIN_ZAG4', 1502: 'EIN_ZAG5', 1503: 'EIN_ZAG6', 1504: 'EIN_ZAG7', 1505: 'EIN_ZAG8', 1510: 'EIN_ZAG9'}, 'departure_date': {1506: '2022-09-02', 1507: '2022-09-05', 1508: '2022-09-09', 1509: '2022-09-12', 1502: '2022-09-16', 1503: '2022-09-19', 1504: '2022-09-23', 1505: '2022-09-26', 1510: '2022-09-30'}, 'price': {1506: 57.0, 1507: 20.0, 1508: 24.0, 1509: 24.0, 1502: 43.0, 1503: 23.0, 1504: 27.0, 1505: 18.0, 1510: 22.0}, 'd_delta': {1506: 4, 1507: 3, 1508: 4, 1509: 3, 1502: 4, 1503: 3, 1504: 4, 1505: 3, 1510: 4}, 'total_fare': {1506: 150.0, 1507: 92.0, 1508: 104.0, 1509: 76.0, 1502: 96.0, 1503: 82.0, 1504: 105.0, 1505: 75.0, 1510: 56.0}, 'outbound_date': {1506: '2022-08-29', 1507: '2022-09-02', 1508: '2022-09-05', 1509: '2022-09-09', 1502: '2022-09-12', 1503: '2022-09-16', 1504: '2022-09-19', 1505: '2022-09-23', 1510: '2022-09-26'}}
    df = pd.DataFrame(data2)
    df["custom_name"] = df.apply(lambda row: "€" + str(row.total_fare), axis=1)

    dates = pd.date_range(df.outbound_date.min(), df.departure_date.max())

    fig = px.timeline(
        df,
        x_start="outbound_date",
        x_end="departure_date",
        y="flight",
        text="custom_name",
        color="total_fare",
        color_continuous_scale=px.colors.diverging.Temps,
        title = 'Flight-combos:',
        # width=1600, height=800)
    )

    fig.update_yaxes(autorange="reversed")
    for date in dates[dates.day_of_week.isin([5, 6])]:
        fig.add_vline(x=date, line_width=2, line_color="gray", opacity=0.3)
    for date in dates[dates.day_of_week.isin([0, 1, 2, 3, 4])]:
        fig.add_vline(
            x=date, line_width=1, line_color="gray", line_dash="dash", opacity=0.2
        )
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")

    return fig
