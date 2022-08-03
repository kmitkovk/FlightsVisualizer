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

import os
import json
import time
import random
import requests
import numpy as np
import pandas as pd
from typing import List

from config import headers, sleep_time

#%% Selection (temp)

origin_airports = {
    "Treviso": "tsf",
    "Trieste": "trs",
    "Zagreb": "zag",
    "Ljubljana": "lju",
}

test_airport = [origin_airports["Zagreb"].upper()]
test_month_year = "2022-08"

#%% Orig-Dest_Country filter


def get_destination_countries(
    origins: List[str],
    departure_month_year: str,
    max_price: int = 100,
    only_direct: bool = True,
    sleep_time: int = 5,
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
    sleep_time : int, optional
        Time to delay the scraper in seconds. The default is 5 seconds.
        The choice is randomized with the module random.
        This is needed as the SS server can recognize too many calls and block.

    Returns
    -------
    pd.DataFrame
        Dataframe with origins-destination country details.
        Columns returned:
            ISO_2:str
            Name:str -> destination country name
            DirectPrice:float -> starting price for the flight (not used yet)

    """

    for origin in origins:
        # original: "https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/v3/bvweb/SI/EUR/en-GB/destinations/TSF/anywhere/2021-11/2021-11/?profile=minimalcityrollupwithnamesv2&include=image;holiday;hotel;adverts&apikey=8aa374f4e28e4664bf268f850f767535&isMobilePhone=false&isOptedInForPersonalised=true"
        p1 = "https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/"
        p2 = f"v3/bvweb/SI/EUR/en-GB/destinations/{origin}/anywhere/"
        p3 = f"{departure_month_year}/?profile=minimalcityrollupwithn"
        p4 = "amesv2&include=image;holiday;hotel;adverts&apikey=8aa374f4e28e46"
        p5 = "64bf268f850f767535&isMobilePhone=false&isOptedInForPersonalised=true"

        url_country_filter = p1 + p2 + p3 + p4 + p5

        sleep = random.random() * sleep_time
        print(round(sleep, 1), f" seconds currently at origin: {origin}")
        time.sleep(sleep)
        response_cnt = requests.request("GET", url_country_filter, headers=headers)
        try:
            json_data_cnt = response_cnt.json()["PlacePrices"]
        except Exception as e:
            raise ValueError(f'Code broke on origin cnt "{origin}" with error:\n{e}')
        if only_direct:
            df_orig_dest_cnts = pd.DataFrame(json_data_cnt)
            df_orig_dest_cnts = df_orig_dest_cnts[
                (df_orig_dest_cnts.Direct == True)
                & (df_orig_dest_cnts.DirectPrice <= max_price)
            ]
            df_orig_dest_cnts = df_orig_dest_cnts[["Id", "Name", "DirectPrice"]]
        else:
            # TODO fix the non-direct flights
            raise Exception("For now only direct flights are being processed")
    # TODO cache the origin->destination data
    return df_orig_dest_cnts.rename(columns={"Id": "ISO_2"})


# test = get_destination_countries(test_airport, test_month_year)
# print(test)


#%% Orig-Dest_City filter


def get_destination_cities():

    pass


#%% Orig-Dest_City dates and prices


def get_destination_cities_dates_prices():
    pass
