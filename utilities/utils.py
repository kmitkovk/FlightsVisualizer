# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 11:47:14 2021

@author: krasimirk
"""

#%% Imports

import pandas as pd

#%% Functions
def check_missing_airports(df_cities, df_flights):
    """
    check if a list of airport exist and try to auto-map and save the
    ones which are present in the bigger database"""

    df_airports_ss = pd.read_csv(r"../data/data_airports.csv", index_col="Unnamed: 0")

    df_new_flights = df_flights.loc[:, ["flight", "dest_city_code", "origin"]]
    df_new_flights = df_new_flights[
        df_new_flights.flight.apply(lambda x: x[-3:]) != df_new_flights.origin
    ]

    df_new_flights["target_code"] = df_new_flights.flight.apply(lambda x: x[-3:])
    df_new_flights = df_new_flights.dropna().loc[:, ["target_code", "dest_city_code"]]
    df_new_unique = df_new_flights.drop_duplicates()

    df_missing = df_new_unique[
        ~df_new_unique.target_code.isin(df_airports_ss.airport_code_IATA)
    ]

    df_to_update = df_missing.merge(
        df_cities, how="left", left_on="dest_city_code", right_on="dest_city_code"
    ).loc[
        :,
        [
            "target_code",
            "dest_city_code",
            "dest_cnt_ISO_2",
            "name_dest_city",
            "name_dest_cnt",
            "image_url_city",
        ],
    ]

    return df_to_update


def save_new_airports(df_to_update: pd.DataFrame) -> None:
    """
    Pulls destination cities outbound and inbound dates for given months

    Parameters
    ----------
    df_to_update : pd.DataFrame
        DataFrame that needs to be merged with the data_airports_ALL df:
            target_code:str -> Airort
            dest_city_code:str -> airport_code_IATA
            dest_cnt_ISO_2:str -> country_code_iso2
            name_dest_city:str -> city_name
            name_dest_cnt:str -> country_name
            image_url_city:str -> city_image_url

    Returns
    -------
        None

    """
    print("include logging here!! ")
    # airport codes databse (also saved in repo):
    # https://raw.githubusercontent.com/datasets/airport-codes/master/data/airport-codes.csv
    # the discrepancy GB-UK is handled because we are always taking SS database
    df_airports_all = pd.read_csv(r"../data/data_airports_all.csv")

    df_to_save = df_to_update.merge(
        df_airports_all, how="left", left_on="target_code", right_on="iata_code"
    ).loc[
        :,
        [
            "continent",
            "name_dest_cnt",
            "dest_cnt_ISO_2",
            "name_dest_city",
            "municipality",
            "dest_city_code",
            "image_url_city",
            "name",
            "target_code",
            "type",
            "coordinates",
        ],
    ]

    df_to_save[["airport_lat", "airport_lon"]] = df_to_save.coordinates.str.split(
        ",", 1, expand=True
    )

    translation_dict = {
        "name_dest_cnt": "country_name",
        "dest_cnt_ISO_2": "country_code_iso2",
        "name_dest_city": "region_name",
        "municipality": "city_name",
        "dest_city_code": "city_code",
        "image_url_city": "city_image_url",
        "name": "airport_name",
        "target_code": "airport_code_IATA",
        "type": "airport_type",
    }

    df_to_save = df_to_save.drop("coordinates", axis=1).rename(
        columns=translation_dict
    )
    
    
    df_airports_ss_old = pd.read_csv(r"../data/data_airports.csv", index_col="Unnamed: 0")
    df_combined_to_save = pd.concat([df_airports_ss_old, df_to_save])
    df_combined_to_save.to_csv(r"../data/data_airports.csv")
    print('New airports updated!')
    



def save_second_function_month():
    """if second funct (cities) scraped once for the origins, BETTER CACHE THAT"""
    pass


def check_existing_countries():
    pass


def check_existing_cities():
    pass
