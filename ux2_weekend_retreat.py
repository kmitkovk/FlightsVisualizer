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

                
if False:
    d = df_all_flights.copy()
    zag = d[d.flight.str.startswith('ZAG')]
    tsf = d[d.flight.str.startswith('TSF')]
    tsf = [i[-3:] for i in tsf.flight.unique()]
    zag = [i[-3:] for i in zag.flight.unique()]
    t = set(tsf)
    z = set(zag)
    t.intersection(z)



if False:
    ls = []
    for date_1 in flights.date:
        for date_2 in flights.date:
            if (date_2 - date_1) == dt.timedelta(days = 3):
                ls.append([date_1,date_2])
                