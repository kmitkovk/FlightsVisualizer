# -*- coding: utf-8 -*-
"""
Created on Sun May  1 14:17:36 2022

@author: krasimirk
"""

import datetime as dt
import pandas as pd
import numpy as np
import requests
import json


#%% Import data:

df_all = pd.read_csv(
    r"data/data_flights.csv", parse_dates=["timestamp", "departure_date"]
).drop(["Unnamed: 0", "trace_id", "origin", "dest_city_code"], axis=1)

df = df_all[df_all.flight.isin(["EIN_ZAG", "ZAG_EIN"])]


#%% Transform data:
# transform so you take latest tick
# https://stackoverflow.com/questions/27488080/python-pandas-filter-rows-after-groupby
df = df[
    df.timestamp == df.groupby(["flight", "departure_date"]).timestamp.transform(max)
]

deps = df[df.flight.str.startswith("ZAG")].drop(["timestamp"], axis=1)
arrs = df[df.flight.str.startswith("EIN")].drop(["timestamp"], axis=1)

#%% Extract:
days_diff_max = 5
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
    ]
    matching_return_flights.loc[:, "d_delta"] = (
        matching_return_flights.departure_date - origin_dep_date
    )
    matching_return_flights.loc[:, "total_fare"] = (
        matching_return_flights.price + origin_dep_price
    )

    matching_return_flights["outbound_date"] = origin_dep_date
    # matching_return_flights["id_trip"] = str(c) + "_" + origin + "_"

    df_matching = pd.concat([df_matching, matching_return_flights])

df_matching = df_matching.sort_values('outbound_date').reset_index()
df_matching['flight'] = df_matching.index.astype('str') + "_" + df_matching.flight
df_matching.departure_date = df_matching.departure_date.dt.strftime('%Y-%m-%d')
df_matching.outbound_date = df_matching.outbound_date.dt.strftime('%Y-%m-%d')
df_matching.d_delta = df_matching.d_delta.dt.days
