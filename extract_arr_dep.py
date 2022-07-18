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

#%% Extract:

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36'}
    
url_country_filter = "https://www.skyscanner.net/g/monthviewservice/SI/EUR/en-GB/calendar/SOF/ZAG/2022-05/2022-05/?profile=minimalmonthviewgridv2&apikey=6f4cb8367f544db99cd1e2ea86fb2627"
response_cnt  = requests.request("GET", url_country_filter , headers=headers)
traces = json.loads(response_cnt.text)['Traces']
prices = json.loads(response_cnt.text)['PriceGrids']

flights = pd.DataFrame({tr_id:x.split('*')
                        for tr_id,x in traces.items()}).T.reset_index()

flights.columns = ['trace_id','last_update','dir_indir',
                   'dep_ap','arr_ap','date','airline','cn']

flights.date = pd.to_datetime(flights.date, dayfirst=True)

if False:
    ls = []
    for date_1 in flights.date:
        for date_2 in flights.date:
            if (date_2 - date_1) == dt.timedelta(days = 3):
                ls.append([date_1,date_2])