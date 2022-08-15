# -*- coding: utf-8 -*-
"""
Created on Sat Aug  6 23:08:53 2022

@author: krasimirk
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Aug  6 23:08:07 2022

@author: krasimirk
"""


import os
import sys
import json
import time
import random
import requests
import numpy as np
import pandas as pd
from typing import List
from collections import defaultdict

from config import HEADERS, SLEEP_TIME_SHORT, SLEEP_TIME_LONG, ORIGIN_AIRPORTS



#%% Orig-Dest_City dates and prices

# this function can be run to update prices and dates every other day
# this function will be used primarily in UX2 and UX3
def get_destination_cities_dates_prices(
    df_destination_cities: pd.DataFrame,
    outbound_months_year: List[str],
    inbound_months_year: List[str],
    only_direct: bool = True,
    max_price: int = 100,
) -> pd.DataFrame:

    """
    Pulls destination cities outbound and inbound dates for given months

    Parameters
    ----------
    df_destination_cities : pd.DataFrame
        DataFrame from the get_destination_cities return functuion:
            origin:str -> three-letter code of the origin city
            dest_city_code:str -> four-letter code of the destination city
    outbound_months_year : List[str]
        List of formatted strings of type yyyy-mm as in '2022-12' for Dec 2022.
        Providing only one month saves on calls to the API, thus better.
    inbound_months_year : List[str]
        List of formatted strings of type yyyy-mm as in '2022-12' for Dec 2022.
        Providing only one month saves on calls to the API, thus better.
    max_price : int, optional
        Limits the return dataframe to the max price. The default is EUR100.
    only_direct : bool, optional
        Search only direct flights. The default is True.

    Returns
    -------
    pd.DataFrame
        .................................................

    """
    df = pd.DataFrame()
    # if 2nd loop with dates breaks then break the main loop of cities
    break_loop_1 = False
    for c, row in enumerate(df_destination_cities.iterrows()):
        if not break_loop_1:
            counter = f"{c+1}/{df_destination_cities.shape[0]}"
            origin = row[1].origin
            dest_city_code = row[1].dest_city_code

            outb_inb_months_pairs = [
                [outb, "outb"] for outb in outbound_months_year
            ] + [[inb, "inb"] for inb in inbound_months_year]

            for month_pair in outb_inb_months_pairs:

                sleep = random.random() * SLEEP_TIME_LONG

                if month_pair[1] == "outb":
                    p1 = "https://www.skyscanner.net/g/monthviewservice/SI/EUR/en-GB/calendar/"
                    p2 = f"{origin}/{dest_city_code}/{month_pair[0]}/?apikey=6f4cb8367f544db99cd1e2ea86fb2627"
                    url_dates_prices = p1 + p2

                    print(
                        round(sleep, 1),
                        f"sleep at: {origin}-{dest_city_code} ; {counter} cities ; month_pair: {month_pair}",
                    )
                else:
                    p1 = "https://www.skyscanner.net/g/monthviewservice/SI/EUR/en-GB/calendar/"
                    p2 = f"{dest_city_code}/{origin}/{month_pair[0]}/?apikey=6f4cb8367f544db99cd1e2ea86fb2627"
                    url_dates_prices = p1 + p2

                    print(
                        round(sleep, 1),
                        f"sleep at: {dest_city_code}-{origin} ; {counter} cities ; month_pair: {month_pair}",
                    )
                time.sleep(sleep)
                response_cnt = requests.request(
                    "GET", url_dates_prices, headers=HEADERS
                )
                try:
                    json_data_cnt = response_cnt.json()
                except Exception as e:
                    raise ValueError(
                        f"Code broke on origin-cities: {origin}-{dest_city_code} with error:\n{e}"
                    )
                    break_loop_1 = True
                    # Save data up till break
                    df.to_csv(r"data/recovery_file_dest_price_dates.csv")
                    break
                if only_direct:
                    # Extract only direct flights
                    direct_flights = [
                        [key, json_data_cnt["Traces"][key].split("*")]
                        for key in json_data_cnt["Traces"]
                        if json_data_cnt["Traces"][key].split("*")[1] == "D"
                    ]

                    price_grids_dict = [
                        i
                        for c,i in enumerate(json_data_cnt["PriceGrids"]["Grid"][0])
                        if 'Direct' in json_data_cnt["PriceGrids"]["Grid"][0][c]
                    ]
                    prices_traces = defaultdict()
                    for i in price_grids_dict:
                        if "Direct" in i:
                            prices_traces[i["Direct"]["TraceRefs"][0]] = i["Direct"][
                                "Price"
                            ]
                    df_flights = pd.DataFrame(
                        [[i[0], *i[1], prices_traces[i[0]]] for i in direct_flights],
                        columns=[
                            "trace_id",
                            "update_time",
                            "dir_indid",
                            "from",
                            "to",
                            "departure_date",
                            "provider_1",
                            "provider_2",
                            "price",
                        ],
                    ).drop(
                        ["update_time", "dir_indid", "provider_1", "provider_2"], axis=1
                    )

                    df_flights = df_flights[df_flights.price < max_price]
                    df_flights["timestamp"] = pd.Timestamp("now").floor("Min")

                    df = pd.concat([df, df_flights])
                else:
                    # TODO fix the non-direct flights
                    raise Exception("For now only direct flights are being processed")
        else:
            print("Exiting main loop!")
            break

            # TODO cache the origin->destination data
    df["flight"] = df["from"] + "_" + df["to"]
    df.departure_date = pd.to_datetime(df.departure_date, format="%Y%m%d").dt.date
    return df.loc[:, ["trace_id", "flight", "departure_date", "price", "timestamp"]]


debug_test_calendar=pd.DataFrame({'origin': {14: 'ZAG'}, 'dest_city_code': {14: 'COLO'}})
test_price_cal = get_destination_cities_dates_prices(
        debug_test_calendar, ["2022-09"], ["2022-09"]
    )