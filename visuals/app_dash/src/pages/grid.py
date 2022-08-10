import pandas as pd
import datetime as dt

import dash
import dash_bootstrap_components as dbc

import plotly.express as px
from dash import Input, Output, dcc, html


dash.register_page(__name__)


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
                                        "Date-grid",
                                        className="card-title",
                                        style={"textAlign": "center"},
                                    ),
                                    html.P(
                                        "Days of vacation:",
                                        className="card-text",
                                    ),
                                    dcc.Slider(
                                        id="days_grid_dropdown",
                                        min=2,
                                        max=16,
                                        step=1,
                                        value=5,
                                        marks={i: str(i) for i in range(2, 17, 1)},
                                        tooltip={
                                            "placement": "bottom",
                                            "always_visible": True,
                                        },
                                    ),
                                    dcc.Dropdown(
                                        clearable=False,
                                        id="selection_flight_dropdown",
                                        placeholder="Zagreb-Eindhoven-Zagreb",
                                        style={"minWidth": "-webkit-fill-available"},
                                    ),
                                    dcc.Graph(id="grid_chart"),
                                ]
                            )
                        ],
                    ),
                ],
                align="center",
            ),
        ),
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
        r"../../../data/data_flights.csv",
    ).drop(["Unnamed: 0", "trace_id", "origin", "dest_city_code"], axis=1)

    df_airports = pd.read_csv(r"../../../data/data_airports.csv")
    dict_airports = (
        df_airports.loc[:, ["airport_code_IATA", "city_name", "country_name"]]
        .set_index("airport_code_IATA")
        .to_dict()
    )

    missing_iata = [
        "AYT",
        "TSR",
        "FRA",
        "NUE",
        "CPH",
        "AUH",
        "GVA",
        "VIE",
        "LPL",
        "BHX",
        "AHO",
        "AMS",
        "MUC",
        "AQJ",
    ]
    for c, i in enumerate(missing_iata):
        dict_airports["city_name"][i] = f"{c}_temporary_city"
        dict_airports["country_name"][i] = f"{c}_temporary_country"
    print("fix above in DB and LOGIC in utils to check")

    df_all["from_pl"] = df_all.flight.apply(lambda x: x[:3])
    origins = ["ZAG", "SOF", "TSF", "LJU", "TRS"]

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
    [Output("grid_chart", "figure"), Output("loading-output-grid", "children")],
    [
        Input("data_grid", "data"),
        Input("data_airports", "data"),
        Input("days_grid_dropdown", "value"),
        Input("selection_flight_dropdown", "value"),
    ],
)
def grid_chart(data, data_airports, dropdown_value, dropdown_value2):
    dff = pd.read_json(data, orient="split")
    dff.departure_date = pd.to_datetime(dff.departure_date)

    # print("\n\n\n\n\n\n\n\n", dropdown_value2, "\n\n\n\n\n\n\n\n")
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
    days_diff_max = dropdown_value
    days_diff_min = 1
    days_delta_max = dt.timedelta(days=days_diff_max)
    days_delta_min = dt.timedelta(days=days_diff_min)

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
    fig.update_layout(yaxis_title="Flight options", plot_bgcolor="rgba(0,0,0,0)")

    return fig, None
