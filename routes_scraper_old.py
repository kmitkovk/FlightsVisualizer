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
    
"""

import os
import json
import time
import random
import requests
import numpy as np
import pandas as pd

from config import headers, sleep_time

#%% Selection

allow_requests = True

max_price = 100  # limit the price
print("Currenty max price only applies to direct fligthts \n\n\n")
print("Apply to indirect flights \n\n\n")

origins = ["ZAG"]
# origins = ['TSF', 'LJU', 'TRS', 'ZAG']
outbound_yr_m = "2022-08"
inbound_yr_m = "2022-08"
show_indirect_prices_countries = False
show_indirect_prices_cities = False

origin_airports = {
    "Treviso": "tsf",
    "Trieste": "trs",
    "Zagreb": "zag",
    "Ljubljana": "lju",
}

#%% Caching dirs
curr_dir = os.getcwd()
data_loc = os.path.join(curr_dir + "\data")
cache_loc = os.path.join(curr_dir + "\data\cache")
routes_data_loc = os.path.join(curr_dir + "\data\routes_data")
dir_p_outb = (outbound_yr_m[2:5] + outbound_yr_m[-2:]).replace("-", "")
dir_p_inb = (inbound_yr_m[2:5] + inbound_yr_m[-2:]).replace("-", "")
joint_in_out = "\\" + dir_p_outb + "-" + dir_p_inb
in_out_path = curr_dir + "\data\cache" + joint_in_out

try:
    os.mkdir(in_out_path)
    print("making a new folder")
except FileExistsError:
    print("in-outbound dir already exists")
print("continuing")

with open(data_loc + '\\city_data.json', 'r') as file: city_codes = file.read()


routes = {}
dest_countries_prices = {}
# origin = origins[0]
for origin in origins:
    # original: "https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/v3/bvweb/SI/EUR/en-GB/destinations/TSF/anywhere/2021-11/2021-11/?profile=minimalcityrollupwithnamesv2&include=image;holiday;hotel;adverts&apikey=8aa374f4e28e4664bf268f850f767535&isMobilePhone=false&isOptedInForPersonalised=true"
    p1 = "https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/v3/bvweb/SI/EUR/en-GB/"
    p2 = f"destinations/{origin}/anywhere/{outbound_yr_m}/{inbound_yr_m}/?profile=minimalcityrollupwithnamesv2&include=image;"
    p3 = "holiday;hotel;adverts&apikey=8aa374f4e28e4664bf268f850f767535&isMobilePhone=false&isOptedInForPersonalised=true"

    url_country_filter = p1 + p2 + p3

    # cache origin data
    origin_loc = in_out_path + f"\\{origin}_{dir_p_outb + '-' + dir_p_inb}"
    os.mkdir(origin_loc)

    if allow_requests:  # Cache and check
        sleep = random.random() * sleep_time
        print(round(sleep, 1), f" seconds currently at origin: {origin}")
        time.sleep(sleep)
        response_cnt = requests.request("GET", url_country_filter, headers=headers)
    try:
        json_data_cnt = json.loads(response_cnt.text)["PlacePrices"]
    except:
        raise ValueError(
            f""" Code broke on origin country: {origin}
                             key "PlacePrices" no in the json, check the get response!"""
        )
    df_cnt = pd.DataFrame(json_data_cnt)
    df_cnt.to_csv(origin_loc + f"\\{origin}_to.csv")
    if show_indirect_prices_countries == False:
        df_cnt = df_cnt[~df_cnt.DirectPrice.isin([0, np.NaN])]
    if max_price != None:
        df_cnt = df_cnt[df_cnt.DirectPrice <= max_price]
    dest_countries_prices[f"{origin}"] = {
        i.Id: {
            "country": i.Name,
            "d_price": i.DirectPrice,
            "ind_price": i.IndirectPrice, 
        }
        for i in df_cnt.itertuples()
    }
    routes[origin] = {i.Id: None for i in df_cnt.itertuples()}
    # routes[origin] = {i.Name:None for i in df_cnt.itertuples()}

    #%% City filter

    for country in dest_countries_prices[origin].keys():
        p1 = "https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/v3/bvweb/SI/EUR/en-GB/"
        p2 = f"destinations/{origin}/{country}/{outbound_yr_m}/{inbound_yr_m}/?profile=minimalcityrollupwithnamesv2&include=image;"
        p3 = "holiday;hotel;adverts&apikey=8aa374f4e28e4664bf268f850f767535&isMobilePhone=false&isOptedInForPersonalised=true"
        url_cities_filter = p1 + p2 + p3

        if allow_requests:  # Cache and check
            sleep = random.random() * sleep_time
            out_of = len(dest_countries_prices[origin].keys()) - 1
            c_out_of = list(dest_countries_prices[origin].keys()).index(country)
            print(
                round(sleep, 1),
                f" seconds currently at origin and destination: {origin}, {country} ; {c_out_of} out of {out_of}",
            )
            time.sleep(sleep)
            response_cit = requests.request("GET", url_cities_filter, headers=headers)
        try:
            json_data_cit = json.loads(response_cit.text)["PlacePrices"]
        except:
            raise ValueError(
                f""" Code broke on origin and destination: {origin}, {country}
                                 key "PlacePrices" no in the json, check the get response!"""
            )
        df_cit = pd.DataFrame(json_data_cit)
        df_cit.to_csv(origin_loc + f"\\{origin}_to_{country}.csv")
        if show_indirect_prices_cities == False:
            df_cit = df_cit[~df_cit.DirectPrice.isin([0, np.NaN])]
        df_cit["IndirectPrice"] = (
            np.NaN if "IndirectPrice" not in df_cit.columns else df_cit["IndirectPrice"]
        )

        routes[origin][country] = {
            i.Name: {
                "city_code": i.Id,
                "d_price": i.DirectPrice,
                "ind_price": i.IndirectPrice,
                "country_name": i.CountryName,
                "image_url": i.ImageUrl,
            }
            for i in df_cit.itertuples()
        }
#%% Find geo coordinates

"""There is also a google API for this which is better but maybe more 
    limited to number of calls in the script locatiion_scraper.py """


def find_geo_coors(city_country):  # using city only is not accurate
    coordinates = {}
    link_geo_api = f"http://api.positionstack.com/v1/forward?access_key=53fd1242060dbfc196a1f76ff3bc4ebf&query={city_country}"
    resp = requests.get(link_geo_api)
    return json.loads(resp.text)


#%% Update city codes
# df_cc.to_csv(r'D:\Code\Others\FlightsScraper\data\city_data.csv', index = False)
if False:
    df_cc = pd.DataFrame([], columns=["Id", "Name", "CountryName", "ImageUrl"])

    date_locs = [i for i in os.listdir(path=routes_data_loc) if "json" not in i]
    for date_fold in date_locs:
        if len(os.listdir(path=routes_data_loc + f"\\{date_fold}")) == 0:
            continue
        for origin_fold in os.listdir(path=routes_data_loc + f"\\{date_fold}"):
            dests = [
                i
                for i in os.listdir(
                    path=routes_data_loc + f"\\{date_fold}" + f"\\{origin_fold}"
                )
                if len(i) > 11
            ]  # check if origin + dest file
            for dest in dests:
                df_dest = pd.read_csv(
                    routes_data_loc
                    + f"\\{date_fold}"
                    + f"\\{origin_fold}"
                    + f"\\{dest}"
                )
                df_dest = df_dest[~df_dest.Id.isin(df_cc.Id)]
                df_cc = df_cc.append(df_dest[["Id", "Name", "CountryName", "ImageUrl"]])
    mp = {}
    for c, i in enumerate(df_cc.itertuples()):
        print(c, " out of ", df_cc.shape[0])
        try:
            fcs = find_geo_coors(i.CityName + ", " + i.CountryName)["data"][0]

            mp[i.CityName] = {
                "country": fcs["country"],
                "lon": fcs["longitude"],
                "lat": fcs["latitude"],
            }
        except:
            print("no data for ", i.CityName, " ", i.CountryName)
            print(find_geo_coors(i.CityName + ", " + i.CountryName))
