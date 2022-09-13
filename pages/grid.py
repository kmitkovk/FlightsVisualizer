from sqlite3 import Timestamp
import pandas as pd
import datetime as dt

import dash
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dcc, html, dash_table


dash.register_page(__name__)

origins = ["ZAG", "TSF", "LJU", "TRS", "SOF", "VCE"]

layout = dbc.Container(
    [
        dcc.Store(id="data_grid"),
        dcc.Store(id="data_airports"),
        dcc.Store(id="data_grid_dummy"),
        dcc.Loading(
            id="loading-grid",
            type="default",
            children=html.Div(id="loading-output-grid"),
        ),
        dbc.Row(
            dbc.Col(
                [
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H4(
                                        "Trip planner",
                                        className="card-title",
                                        style={"textAlign": "center"},
                                    ),
                                    html.Br(),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.CardHeader(
                                                        "Days of vacation:",
                                                    ),
                                                    html.Br(),
                                                    dcc.RangeSlider(
                                                        id="days_grid_dropdown",
                                                        min=1,
                                                        max=17,
                                                        step=1,
                                                        value=[2, 5],
                                                        marks={
                                                            i: str(i)
                                                            for i in range(1, 18, 1)
                                                        },
                                                        tooltip={
                                                            "placement": "bottom",
                                                            "always_visible": True,
                                                        },
                                                    ),
                                                ],
                                                width=5,
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.CardHeader(
                                                        "Origin-destination:",
                                                    ),
                                                    dcc.Dropdown(
                                                        clearable=False,
                                                        id="selection_flight_dropdown",
                                                        placeholder="Zagreb-Eindhoven-Zagreb",
                                                        style={
                                                            "minWidth": "-webkit-fill-available"
                                                        },
                                                    ),
                                                ],
                                                width=5,
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.CardHeader(
                                                        "Show # of months:",
                                                    ),
                                                    html.Br(),
                                                    dcc.Slider(
                                                        id="months_show_dropdown",
                                                        min=1,
                                                        max=5,
                                                        step=1,
                                                        value=1,
                                                        marks={
                                                            i: str(i)
                                                            for i in range(1, 6, 1)
                                                        },
                                                        tooltip={
                                                            "placement": "bottom",
                                                            "always_visible": True,
                                                        },
                                                    ),
                                                ],
                                                width=2,
                                            ),
                                        ]
                                    ),
                                    dcc.Graph(id="grid_chart"),
                                    html.P(id="test_progress"),
                                ]
                            )
                        ],
                    ),
                ],
                align="center",
            ),
        ),
        dbc.Row([dbc.Col(id="last_timestamp", width=3)]),
        html.Br(),
        html.Br(),
    ]
)


@dash.callback(
    [
        Output("data_grid", "data"),
        Output("data_airports", "data"),
        Output("selection_flight_dropdown", "options"),
    ],
    Input("data_grid_dummy", "data"),
)
def data(dummy):
    df_all = pd.read_csv(
        r"data/data_flights.csv",
    ).drop(["Unnamed: 0", "trace_id", "origin", "dest_city_code"], axis=1)

    df_airports = pd.read_csv(r"data/data_airports.csv")
    dict_airports = (
        df_airports.loc[:, ["airport_code_IATA", "city_name", "country_name"]]
        .set_index("airport_code_IATA")
        .to_dict()
    )

    df_all["from_pl"] = df_all.flight.apply(lambda x: x[:3])

    # options = df_all.flight.apply(lambda x: x if x[:3] in origins else '').unique()
    options = df_all.flight[df_all.from_pl.isin(origins)].unique()
    options_dict = [
        {
            "label": f"{dict_airports['city_name'][flight[:3]]}-{dict_airports['city_name'][flight[-3:]]}({dict_airports['country_name'][flight[-3:]]})-{dict_airports['city_name'][flight[:3]]}",
            "value": flight,
        }
        for flight in options
    ]

    return (
        df_all.to_json(orient="split"),
        df_airports.to_json(orient="split"),
        options_dict,
    )  # , 'ZAG-EIN'


@dash.callback(
    [
        Output("grid_chart", "figure"),
        Output("last_timestamp", "children"),
        Output("loading-output-grid", "children"),
    ],
    [
        Input("data_grid", "data"),
        Input("data_airports", "data"),
        Input("days_grid_dropdown", "value"),
        Input("selection_flight_dropdown", "value"),
        Input("months_show_dropdown", "value"),
    ],
)
def grid_chart(data, data_airports, dropdown_value, dropdown_value2, num_months_show):
    dff = pd.read_json(data, orient="split")
    dff.departure_date = pd.to_datetime(dff.departure_date)
    dff = dff[
        (
            dff.departure_date
            <= pd.Timestamp("now") + pd.offsets.DateOffset(months=num_months_show)
        )
        & (dff.departure_date > pd.Timestamp("now"))  # removes past data
    ]

    print(pd.Timestamp("now"))
    if dropdown_value2 == None:
        dropdown_value2 = "ZAG_EIN"

    frm = dropdown_value2[:3]
    to = dropdown_value2[-3:]

    dff = dff[dff.flight.isin([f"{to}_{frm}", f"{frm}_{to}"])]
    dff = dff[
        dff.timestamp
        == dff.groupby(["flight", "departure_date"]).timestamp.transform(max)
    ]

    deps = dff[dff.flight.str.startswith(f"{frm}")].drop(["timestamp"], axis=1)
    arrs = dff[dff.flight.str.startswith(f"{to}")].drop(["timestamp"], axis=1)

    #%% Extract:
    days_diff_min = dropdown_value[0]
    days_diff_max = dropdown_value[1]
    days_delta_max = dt.timedelta(days=days_diff_max)
    days_delta_min = dt.timedelta(days=days_diff_min)

    if dff.empty:
        timestamps = pd.DataFrame([], columns=["Month(s):", "Last updated:"])
        table_timestamps = dash_table.DataTable(
            timestamps.to_dict("records"),
            [{"name": i, "id": i} for i in timestamps.columns],
        )
        fig = go.Figure()
        fig.update_layout(
            title_x=0.5,
            title="*NO TRIPS AVAILABLE FOR THIS COMBINATION OF TRIP, PRICE, DAYS OF VACATION OR # MONTHS SHOWN!",
        )
        return fig, table_timestamps, None

    df_matching = pd.DataFrame()
    for c, dep in enumerate(deps.iterrows()):
        origin = dep[1].flight[:3]
        origin_dep_date = dep[1].departure_date
        origin_dep_price = dep[1].price
        arr_dep_delta = arrs.departure_date - origin_dep_date
        matching_return_flights = arrs[
            (arr_dep_delta <= days_delta_max) & (arr_dep_delta >= days_delta_min)
        ].copy()  # removes settingwithcopywarnin see second answer: https://stackoverflow.com/questions/42379818/correct-way-to-set-new-column-in-pandas-dataframe-to-avoid-settingwithcopywarnin
        matching_return_flights.loc[:, "d_delta"] = (
            matching_return_flights.departure_date - origin_dep_date
        )
        matching_return_flights.loc[:, "total_fare"] = (
            matching_return_flights.price + origin_dep_price
        )

        matching_return_flights["outbound_date"] = origin_dep_date
        # matching_return_flights["id_trip"] = str(c) + "_" + origin + "_"

        df_matching = pd.concat([df_matching, matching_return_flights])
    df_matching = df_matching.sort_values("outbound_date").reset_index()
    df_matching["flight_num"] = (df_matching.index + 1).astype("str")
    df_matching.departure_date = df_matching.departure_date.dt.strftime("%Y-%m-%d")
    df_matching.outbound_date = df_matching.outbound_date.dt.strftime("%Y-%m-%d")
    df_matching.d_delta = df_matching.d_delta.dt.days

    df = df_matching.copy()

    if df.empty:
        timestamps = pd.DataFrame([], columns=["Month(s):", "Last updated:"])
        table_timestamps = dash_table.DataTable(
            timestamps.to_dict("records"),
            [{"name": i, "id": i} for i in timestamps.columns],
        )
        fig = go.Figure()
        fig.update_layout(
            title_x=0.5,
            title="*NO TRIPS AVAILABLE FOR THIS COMBINATION OF TRIP, PRICE, DAYS OF VACATION OR # MONTHS SHOWN!",
        )
        return fig, table_timestamps, None

    df["custom_name"] = df.apply(lambda row: "€" + str(row.total_fare), axis=1)
    dates = pd.date_range(df.outbound_date.min(), df.departure_date.max())

    # Source: https://plotly.com/python/gantt/
    # Source: https://plotly.com/python-api-reference/generated/plotly.express.timeline.html
    # Colors: https://plotly.com/python/builtin-colorscales/
    # Colors: https://plotly.com/python/colorscales/
    fig = px.timeline(
        df,
        x_start="outbound_date",
        x_end="departure_date",
        y="flight_num",
        text="custom_name",
        color="total_fare",
        color_continuous_scale=px.colors.diverging.Temps,
        # width=1600, height=800)
    )

    fig.update_yaxes(autorange="reversed")
    for date in dates[dates.day_of_week.isin([5, 6])]:
        fig.add_vline(x=date, line_width=2, line_color="gray", opacity=0.3)
    for date in dates[dates.day_of_week.isin([0, 1, 2, 3, 4])]:
        fig.add_vline(
            x=date, line_width=1, line_color="gray", line_dash="dash", opacity=0.2
        )
    fig.update_layout(
        yaxis_title="Flight options", plot_bgcolor="rgba(0,0,0,0)", margin=dict(b=3)
    )

    df_timestamps = (
        dff.groupby(dff.departure_date.dt.strftime("%Y-%m-01"))  #%b'%y
        .timestamp.max()
        .sort_index()
    )
    timestamps = df_timestamps.dt.strftime("%d-%b-%Y").to_frame().reset_index()
    timestamps.departure_date = pd.to_datetime(
        timestamps.departure_date, dayfirst=True
    ).dt.strftime("%b'%y")
    timestamps = timestamps.rename(
        columns={"departure_date": "Month(s):", "timestamp": "Last updated:"}
    )
    table_timestamps = dash_table.DataTable(
        timestamps.to_dict("records"),
        [{"name": i, "id": i} for i in timestamps.columns],
    )

    return fig, table_timestamps, None
