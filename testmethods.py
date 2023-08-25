# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 16:32:00 2023

@author: krasimir.kerliev
"""







if False: # old

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
    dff = df_flights.copy()
    days_vacay_selection = [2,5]

    
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


    days_delta_max = dt.timedelta(days=days_diff_max)
    days_delta_min = dt.timedelta(days=days_diff_min)

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
