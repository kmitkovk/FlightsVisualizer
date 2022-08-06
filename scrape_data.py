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
import sys
import json
import time
import random
import requests
import numpy as np
import pandas as pd
from typing import List

from config import HEADERS, SLEEP_TIME, ORIGIN_AIRPORTS

#%% Selection (temp)

# test_airports = [ORIGIN_AIRPORTS["Zagreb"].upper()]
test_airports = [ORIGIN_AIRPORTS[i].upper() for i in ["Zagreb", "Trieste"]]
test_airports = [ORIGIN_AIRPORTS[i].upper() for i in ["Ljubljana", "Treviso"]]
test_month_year = "2022-08"

test_mode = True
if test_mode:
    inp = input(
        """You have enabled test mode, code will run ! (not only functions load)
        If you don't wish to run test, type 'n' and flip test_mode to False
        Do you wish to continue?(y/n): """
    )
    if inp == "n":
        print("Script did not run")
        sys.exit()
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

        sleep = random.random() * SLEEP_TIME
        print(round(sleep, 1), f"sleep at: {origin} ; {counter} ")
        time.sleep(sleep)
        response_cnt = requests.request("GET", url_country_filter, headers=HEADERS)
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


if test_mode:
    test_countries_all = get_destination_countries(test_airports, test_month_year)
    test_countries = test_countries_all.iloc[-8:-2]
    print(test_countries)
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

        sleep = random.random() * SLEEP_TIME
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
        if only_direct:
            df_orig_dest_cities = pd.DataFrame(json_data_cnt)
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


if test_mode:
    test_cities = get_destination_cities(test_countries_all, test_month_year)
    print(test_cities)
    #cache data
    # test_cities.to_csv(r'data/cache_dest_cities.csv')    
    
#%% Orig-Dest_City dates and prices

# this function can be run to update prices and dates every other day
def get_destination_cities_dates_prices():
    pass
