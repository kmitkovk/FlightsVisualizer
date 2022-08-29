# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 11:47:14 2021

@author: krasimirk

File purpose:
    1. Extract destination country details based on:
        - origin airports (nearby airports of choice)
        - months ahead for which the search is performed
    2. Extract the cities list and details from the destination country
    3. Record those on a .csv file in folder 'data'
    
!!! Important:
    - get_destination_countries and get_destination_cities is to be run only
        occasionally since those do not update very often\
    - the more frequent calls could be done when looking using the
        function get_destination_cities_dates_prices
    
"""

import sys
import time
import random
import requests
import pandas as pd
from typing import List
from collections import defaultdict

from config import HEADERS, SLEEP_TIME_SHORT, SLEEP_TIME_LONG, ORIGIN_AIRPORTS
from scripts.utils import check_missing_airports, save_new_airports


#%% Orig-Dest_Country filter

# this function and get_destination_cities should run only once per week
# this function should not save to database as this is done by get_destination_cities
def get_destination_countries(
    origins: List[str],
    departure_month_year: str,
    max_price: int = 100,
    only_direct: bool = True,
) -> pd.DataFrame:
    """
    Maps destination countries given origin cities.
    Later version will have cachining mechanism to check for existing data.

    Parameters
    ----------
    origins : List[str]
        Aiport code(s) which for now need to be looked up on skyscraper.
    departure_month_year : str
        Formatted string of type yyyy-mm as in '2022-12' for Dec 2022.
        Current input here is one month as routes of origin-destiantion are
        mostly fixed - airlines don't tend to change their routes often.
        Providing only one month also saves on calls to the API, thus better.
    max_price : int, optional
        Limits the return dataframe to the max price. The default is EUR100.
    only_direct : bool, optional
        Search only direct flights. The default is True.

    Returns
    -------
    pd.DataFrame
        Dataframe with origins-destination country details.
        Columns returned:
            origin:str -> three-letter code of the origin city
            dest_cnt_ISO_2:str -> ISO2 format of the destination country
            name_dest_cnt:str -> destination country name
            direct_price_dest_cnt:float -> starting price for the flight
            timestamp:datetime -> timestamp of moment of accessing the data

    """
    # defines the main data frame which will contain all origins-destination_countries
    df = pd.DataFrame()
    for c, origin in enumerate(origins):
        counter = f"{c+1}/{len(origins)} origins"
        # original: "https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/v3/bvweb/SI/EUR/en-GB/destinations/TSF/anywhere/2021-11/2021-11/?profile=minimalcityrollupwithnamesv2&include=image;holiday;hotel;adverts&apikey=8aa374f4e28e4664bf268f850f767535&isMobilePhone=false&isOptedInForPersonalised=true"
        p1 = "https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/"
        p2 = f"v3/bvweb/SI/EUR/en-GB/destinations/{origin}/anywhere/"
        p3 = f"{departure_month_year}/?profile=minimalcityrollupwithn"
        p4 = "amesv2&include=image;holiday;hotel;adverts&apikey=8aa374f4e28e46"
        p5 = "64bf268f850f767535&isMobilePhone=false&isOptedInForPersonalised=true"

        url_country_filter = p1 + p2 + p3 + p4 + p5

        sleep = random.random() * SLEEP_TIME_SHORT + 1
        print(round(sleep, 1), f"sleep at: {origin} ; {counter} ")
        time.sleep(sleep)
        response_cnt = requests.request("GET", url_country_filter, headers=HEADERS)
        try:
            json_data_cnt = response_cnt.json()["PlacePrices"]
        except Exception as e:
            raise ValueError(f'Code broke on origin cnt "{origin}" with error:\n{e}')
            print(f'\n\n\n   response:\n{response_cnt}\n\n\n')
            print("Exiting main loop!")
            break
        if only_direct:
            df_orig_dest_cnts = pd.DataFrame(json_data_cnt)
            df_orig_dest_cnts = df_orig_dest_cnts[
                (df_orig_dest_cnts.Direct == True)
                & (df_orig_dest_cnts.DirectPrice <= max_price)
            ]
            df_orig_dest_cnts["origin"] = origin
            df_orig_dest_cnts["timestamp"] = pd.Timestamp("now").floor("Min")
            df_orig_dest_cnts = df_orig_dest_cnts[
                ["origin", "Id", "Name", "DirectPrice", "timestamp"]
            ]
            df = pd.concat([df, df_orig_dest_cnts])
        else:
            # TODO fix the non-direct flights
            raise Exception("For now only direct flights are being processed")
    # TODO cache the origin->destination data
    return df.rename(
        columns={
            "Id": "dest_cnt_ISO_2",
            "Name": "name_dest_cnt",
            "DirectPrice": "direct_price_dest_cnt",
        }
    )


#%% Orig-Dest_City filter

# this function and get_destination_countries should run only once per week
# this function saves to the database
def get_destination_cities(
    df_destination_countries: pd.DataFrame,
    departure_month_year: str,
    only_direct: bool = True,
    max_price: int = 100,
) -> pd.DataFrame:

    """
    Maps destination countries given origin cities.
    Later version will have cachining mechanism to check for existing data.

    Parameters
    ----------
    df_destination_countries : pd.DataFrame
        DataFrame from the get_destination_countries return functuion:
            origin:str -> three-letter code of the origin city
            dest_cnt_ISO_2:str -> ISO2 format of the destination country
            name_dest_cnt:str -> destination country name
            direct_price_dest_cnt:float -> starting price for the flight
            timestamp:datetime -> timestamp of moment of accessing the data
    departure_month_year : str
        Formatted string of type yyyy-mm as in '2022-12' for Dec 2022.
        Current input here is one month as routes of origin-destiantion are
        mostly fixed - airlines don't tend to change their routes often.
        Providing only one month also saves on calls to the API, thus better.
    max_price : int, optional
        Limits the return dataframe to the max price. The default is EUR100.
    only_direct : bool, optional
        Search only direct flights. The default is True.

    Returns
    -------
    pd.DataFrame
        Dataframe with origins-destination city details.
        Columns returned:
            origin:str -> three-letter code of the origin city
            dest_cnt_ISO_2:str -> ISO2 format of the destination country
            dest_city_code:str -> four-letter code of the destination city
            name_dest_city:str -> ISO2 format of the destination country
            name_dest_cnt:str -> destination city name
            image_url_city:str -> city image url
            direct_price_dest_city:float -> starting price for the flight
            timestamp:datetime -> timestamp of moment of accessing the data

    """
    df = pd.DataFrame()
    df_itterable = df_destination_countries[["origin", "dest_cnt_ISO_2"]]
    for c, row in enumerate(df_itterable.iterrows()):
        counter = f"{c+1}/{df_itterable.shape[0]}"
        origin = row[1].origin
        dest_cnt_ISO_2 = row[1].dest_cnt_ISO_2
        p1 = "https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/"
        p2 = f"v3/bvweb/SI/EUR/en-GB/destinations/{origin}/{dest_cnt_ISO_2}"
        p3 = f"/{departure_month_year}/?profile=minimalcityrollupwithnamesv2&include=image;"
        p4 = "holiday;hotel;adverts&apikey=8aa374f4e28e4664bf268f850f767535&"
        p5 = "isMobilePhone=false&isOptedInForPersonalised=true"
        url_cities_filter = p1 + p2 + p3 + p4 + p5

        sleep = random.random() * SLEEP_TIME_SHORT + 1
        print(
            round(sleep, 1), f"sleep at: {origin}-{dest_cnt_ISO_2} ; {counter} cities"
        )
        time.sleep(sleep)
        response_cnt = requests.request("GET", url_cities_filter, headers=HEADERS)
        try:
            json_data_cnt = response_cnt.json()["PlacePrices"]
        except Exception as e:
            raise ValueError(
                f"Code broke on origin-cities: {origin}-{dest_cnt_ISO_2} with error:\n{e}"
            )
            print(f'\n\n\n   response:\n{response_cnt}\n\n\n')
        if only_direct:
            df_orig_dest_cities = pd.DataFrame(json_data_cnt)
            if 'DirectPrice' not in df_orig_dest_cities.columns:
                continue
            df_orig_dest_cities = df_orig_dest_cities[
                (df_orig_dest_cities.Direct == True)
                & (df_orig_dest_cities.DirectPrice <= max_price)
                & (df_orig_dest_cities.DirectPrice > 0)
            ]
            df_orig_dest_cities["origin"] = origin
            df_orig_dest_cities["dest_cnt_ISO_2"] = dest_cnt_ISO_2
            df_orig_dest_cities = df_orig_dest_cities[
                [
                    "origin",
                    "dest_cnt_ISO_2",
                    "Id",
                    "Name",
                    "CountryName",
                    "DirectPrice",
                    "ImageUrl",
                ]
            ]
            df_orig_dest_cities["timestamp"] = pd.Timestamp("now").floor("Min")
            df = pd.concat([df, df_orig_dest_cities])
        else:
            # TODO fix the non-direct flights
            raise Exception("For now only direct flights are being processed")
            print("Exiting main loop!")
            break
    # TODO cache the origin->destination data
    return df.rename(
        columns={
            "Id": "dest_city_code",
            "Name": "name_dest_city",
            "CountryName": "name_dest_cnt",
            "ImageUrl": "image_url_city",
            "DirectPrice": "direct_price_dest_city",
        }
    )


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
        trace_id:str -> id of the trace the price is backed out with
        flight:str -> origin-dest_airport pair such as SOF_ZAG
        departure_date:object -> date of departure of flight
        price:float -> price of flight
        origin:str -> three-letter code of the origin city (not 'from'!)
        dest_city_code:str -> four-letter code of the destination city
        timestamp:datetime -> timestamp of moment of accessing the data

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

                sleep = random.random() * SLEEP_TIME_LONG + 1

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
                    print(f'\n\n\n   response:\n{response_cnt}\n\n\n')
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
                        for c, i in enumerate(json_data_cnt["PriceGrids"]["Grid"][0])
                        if "Direct" in json_data_cnt["PriceGrids"]["Grid"][0][c]
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
                    df_flights["origin"] = origin
                    df_flights["dest_city_code"] = dest_city_code
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
    return df.loc[
        :,
        [
            "trace_id",
            "flight",
            "departure_date",
            "price",
            "origin",
            "dest_city_code",
            "timestamp",
        ],
    ]


#%% Selection (temp)

month1 = "2022-10"
test_airports = [ORIGIN_AIRPORTS["Sofia"]]
test_airports = [ORIGIN_AIRPORTS[i] for i in ORIGIN_AIRPORTS if i != 'Sofia']

if False:
    dest_countries = get_destination_countries(test_airports, month1)

    dest_cities = get_destination_cities(dest_countries, month1)

    dest_cities_dates_prices = get_destination_cities_dates_prices(
        dest_cities.loc[:, ["origin", "dest_city_code"]],
        [month1],
        [month1],
    )

    if False:
        old_test = pd.read_csv(
            r"data/data_flights.csv", parse_dates=["timestamp"]
        ).drop("Unnamed: 0", axis=1)
        df = pd.concat([old_test, dest_cities_dates_prices])
        df.to_csv(r"data/data_flights.csv")
        
        
df_missing_airports = check_missing_airports(
    df_cities=dest_cities, df_flights=dest_cities_dates_prices
)
if not df_missing_airports.empty:
    save_new_airports(df_to_update=df_missing_airports)
#%% -----END-----
