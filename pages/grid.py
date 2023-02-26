import pandas as pd
import datetime as dt
import subprocess
import sys
import os

import dash
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dcc, html, dash_table, ctx

from sqlalchemy import create_engine
from config import CONN_STR

# below could cause connection to be lost if page is not interacted with, fixed on refresh
engine_azure = create_engine(CONN_STR, echo=True)

dash.register_page(__name__)

origins = ["ZAG", "TSF", "LJU", "TRS", "SOF", "VCE"]

layout = dbc.Container(
    [
        dcc.Store(id="data_grid"),
        dcc.Store(id="data_airports"),
        dcc.Store(id="data_grid_dummy"),
        html.Div(id="hidden-content"),
        dcc.Loading(
            type="default",
            children=html.Div(
                id="loading-output-grid-data",
            ),
            style={
                "z-index": "1",
                "position": "fixed",
                "top": "50%",
            },
        ),
        dcc.Loading(
            type="circle",
            children=html.Div(
                id="loading-output-grid-chart",
            ),
            style={"z-index": "1", "position": "fixed", "top": "50%"},
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
                                                md=5,
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
                                                md=5,
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.CardHeader(
                                                        "Show # of months:",
                                                    ),
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
                                                md=2,
                                            ),
                                        ],
                                        className="g-3",  # horizontal spacing (also vertical if smalls creen)
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
    ],
    # fluid=True, #if you want your Container to fill available horizontal space and resize fluidly.
)


@dash.callback(
    [
        Output("selection_flight_dropdown", "options"),
        Output("data_airports", "data"),
    ],
    Input("data_grid_dummy", "data"),
)
def data_options(dummy):
    query_distinct_routes = """
                            DECLARE @Date DATE = GETDATE()
                            Select DISTINCT flight FROM FV_FLIGHTS
                            where origin is NOT NULL
                            and departure_date > @Date
                            and LEFT(flight,3) in ('{origins_string}')
    """
    options = pd.read_sql_query(
        query_distinct_routes.format(origins_string="','".join(origins)),
        con=engine_azure,
    ).flight.to_list()

    df_airports = pd.read_sql_query("SELECT * FROM FV_AIRPORTS_SS", con=engine_azure)
    dict_airports = (
        df_airports.loc[:, ["airport_code_IATA", "city_name", "country_name"]]
        .set_index("airport_code_IATA")
        .to_dict()
    )

    dict_airports_cities = (
        df_airports.loc[:, ["airport_code_IATA", "city_code"]]
        .set_index("airport_code_IATA")
        .to_dict()
    )

    options_dict = [
        {
            "label": f"{dict_airports['city_name'][flight[:3]]}-{dict_airports['city_name'][flight[-3:]]}({dict_airports['country_name'][flight[-3:]]})-{dict_airports['city_name'][flight[:3]]}",
            "value": flight,
        }
        for flight in options
    ]

    return options_dict, dict_airports_cities


@dash.callback(
    [Output("data_grid", "data"), Output("loading-output-grid-data", "children")],
    [
        Input("selection_flight_dropdown", "value"),
        Input("months_show_dropdown", "value"),
    ],
)
def data_grid(route_selection, num_months_show):
    print(pd.Timestamp("now"))
    if route_selection == None:
        route_selection = "ZAG_EIN"
    frm = route_selection[:3]
    to = route_selection[-3:]

    # below origin needed for repeating scrapes ZAG-SOF-ZAG vs SOF-ZAG-SOF
    # grouping on and using the latest timestamp tick below on the data as
    # scrape is always done on the origin towards all destinations meaning
    # if in scrape one VCE-ATH showed up for a particular departure date
    # but it did not show up on scrape 2 this means that one of the flights
    # became more expensive than the eur100 limit
    query_flights = """
        SET NOCOUNT ON
        DECLARE @NumMonths int = {months_offset}
        DECLARE @Date DATE = GETDATE()
        DECLARE @DateEnd DATE = DATEADD(DAY,-1,DATEFROMPARTS(YEAR (DATEADD (MONTH, @NumMonths, @Date )),MONTH (DATEADD (MONTH, @NumMonths, @Date)),1))
        SELECT origin, year(departure_date) as year_gr , MONTH (departure_date) month_gr, max([timestamp]) as maxtick
        into #TEMPTABLE
        FROM FV_FLIGHTS
        GROUP by origin, YEAR(departure_date), MONTH (departure_date)
        SELECT flights.flight, flights.departure_date, flights.price, flights.origin, flights.[timestamp] from FV_FLIGHTS as flights
        join #TEMPTABLE as tvmx on tvmx.origin = flights.origin
            and tvmx.year_gr = year(flights.departure_date)
            and tvmx.month_gr = month(flights.departure_date)
            and tvmx.maxtick = flights.[timestamp]
        where flights.origin like '{frm}'
        and (flight like '{frm}_{to}' OR flight like '{to}_{frm}')
        and departure_date BETWEEN @Date and @DateEnd
        order by departure_date
        DROP table #TEMPTABLE
    """

    df_flights = pd.read_sql_query(
        query_flights.format(frm=frm, to=to, months_offset=num_months_show),
        con=engine_azure,
    )
    return df_flights.to_json(orient="split"), None

dash.clientside_callback(
    """
    function(click_data, airports_data) {
        if (typeof(click_data) !== 'undefined') { // we need this because airports_data triggers first and at this point click_data is undefined
            let dep = JSON.stringify(click_data.points[0].base);
            let dep_str = dep.substring(3,5)+dep.substring(6,8)+dep.substring(9,11);
            let arr = JSON.stringify(click_data.points[0].value);
            let arr_str = arr.substring(3,5)+arr.substring(6,8)+arr.substring(9,11);

            let route = JSON.stringify(click_data.points[0].customdata[0]).split("_")
            let orig = route[1].substring(0,3)
            let dest = route[0].substring(1,4)

            orig_str = airports_data.city_code[orig].toLowerCase()
            dest_str = airports_data.city_code[dest].toLowerCase()
            //window.alert(orig_str);
            window.open("https://www.skyscanner.net/transport/flights/" + orig_str + "/" + dest_str + "/" + dep_str + "/" + arr_str + "/?currency=EUR&stops=!oneStop,!twoPlusStops");
        }

        return ""
    }
    """,
    Output('hidden-content', 'children'),
    Input("grid_chart", "clickData"),
    Input("data_airports", "data"),
    prevent_initial_call=True,
)


@dash.callback(
    [
        Output("grid_chart", "figure"),
        Output("last_timestamp", "children"),
        Output("loading-output-grid-chart", "children"),
    ],
    [
        Input("data_grid", "data"),
        Input("days_grid_dropdown", "value"),
        Input("selection_flight_dropdown", "value"),
    ],
)
def grid_chart(data_flights, days_vacay_selection, route_selection):
    dff = pd.read_json(
        data_flights, orient="split", convert_dates=["departure_date", "timestamp"]
    )
    days_diff_min = days_vacay_selection[0]
    days_diff_max = days_vacay_selection[1]

    if route_selection == None:
        route_selection = "ZAG_EIN"
    frm = route_selection[:3]
    to = route_selection[-3:]

    # below does not need to add origin for repeating routes such as ZAG-SOF
    # where ZAG is the origin and SOF-ZAG where sofia is the origin
    # this is because in either case max tick will be taken
    dff = dff[
        dff.timestamp
        == dff.groupby(["flight", "departure_date"]).timestamp.transform(max)
    ]

    # %% Extract:

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
    deps = dff[dff.flight.str.startswith(f"{frm}")].drop(["timestamp"], axis=1)
    arrs = dff[dff.flight.str.startswith(f"{to}")].drop(["timestamp"], axis=1)

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
        matching_return_flights.loc[:, "€ Total"] = (
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
    df["custom_name"] = df.apply(lambda row: "€" + str(row["€ Total"]), axis=1)
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
        color="€ Total",
        color_continuous_scale=px.colors.diverging.Temps,
        custom_data=["flight"]
        # range_x=("2022-10-01", "2022-11-30"),
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
        yaxis_title="Flight options",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(b=3, l=2, r=2),
    )
    # fig.update_coloraxes(colorbar_orientation="h", colorbar_title_side="top")

    df_timestamps = (
        dff.groupby(dff.departure_date.dt.strftime("%Y-%m-01"))  # %b'%y
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
