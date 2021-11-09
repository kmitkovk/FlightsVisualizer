# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 11:47:14 2021

@author: krasimirk
"""
import json
import time
import random
import requests
import numpy as np
import pandas as pd

sleep_time = 3 #in seconds so we will randomly get up to 3 seconds sleep
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36'}


#%% Selection

allow_requests = False

max_price = 100 #limit the price
print('Currenty max price only applies to direct fligthts \n\n\n')

origins = ['LJU']
outbound_yr_m = '2021-11'
inbound_yr_m = '2021-11'
show_indirect_prices_countries = False
show_indirect_prices_cities = False


#%% Country filter

routes = {}
dest_countries_prices = {}

# origin = origins[0]
for origin in origins:
    #original: "https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/v3/bvweb/SI/EUR/en-GB/destinations/TSF/anywhere/2021-11/2021-11/?profile=minimalcityrollupwithnamesv2&include=image;holiday;hotel;adverts&apikey=8aa374f4e28e4664bf268f850f767535&isMobilePhone=false&isOptedInForPersonalised=true"
    p1 = 'https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/v3/bvweb/SI/EUR/en-GB/' 
    p2 = f'destinations/{origin}/anywhere/{outbound_yr_m}/{inbound_yr_m}/?profile=minimalcityrollupwithnamesv2&include=image;'
    p3 = 'holiday;hotel;adverts&apikey=8aa374f4e28e4664bf268f850f767535&isMobilePhone=false&isOptedInForPersonalised=true'
    
    url_country_filter = p1 + p2 + p3
    
    
    if allow_requests: #Cache and check
        sleep = random.random() * sleep_time
        print(round(sleep,1),f' seconds currently at origin: {origin}')
        time.sleep(sleep)    
        response_cnt  = requests.request("GET", url_country_filter , headers=headers)
    
    try:
        json_data_cnt = json.loads(response_cnt.text)['PlacePrices']
    except:
        raise ValueError(f""" Code broke on origin country: {origin}
                             key "PlacePrices" no in the json, check the get response!""")
        
    df_cnt = pd.DataFrame(json_data_cnt)
    if show_indirect_prices_countries == False:
        df_cnt = df_cnt[~df_cnt.DirectPrice.isin([0,np.NaN])]
    
    if max_price != None:
        df_cnt = df_cnt[df_cnt.DirectPrice <= max_price]
    
    
    dest_countries_prices[f'{origin}'] = {i.Id:{'country':i.Name,
                                                'd_price': i.DirectPrice,
                                                'ind_price':i.IndirectPrice}
                                                        for i in df_cnt.itertuples()}
    routes[origin] = {i.Id:None for i in df_cnt.itertuples()}
    # routes[origin] = {i.Name:None for i in df_cnt.itertuples()}
    
    #%% City filter
    
    for country in dest_countries_prices[origin].keys():
        p1 = 'https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/v3/bvweb/SI/EUR/en-GB/'
        p2 = f'destinations/{origin}/{country}/{outbound_yr_m}/{inbound_yr_m}/?profile=minimalcityrollupwithnamesv2&include=image;'
        p3 = 'holiday;hotel;adverts&apikey=8aa374f4e28e4664bf268f850f767535&isMobilePhone=false&isOptedInForPersonalised=true'
        url_cities_filter = p1 + p2 + p3
        
        if allow_requests: #Cache and check
            sleep = random.random() * sleep_time
            print(round(sleep,1),f' seconds currently at origin and destination: {origin}, {country}')
            time.sleep(sleep)   
            response_cit = requests.request("GET", url_cities_filter, headers=headers)
            
        try:
            json_data_cit = json.loads(response_cit.text)['PlacePrices']
        except:
            raise ValueError(f""" Code broke on origin and destination: {origin}, {country}
                                 key "PlacePrices" no in the json, check the get response!""")


        df_cit = pd.DataFrame(json_data_cit)
        if show_indirect_prices_cities == False:
            df_cit = df_cit[~df_cit.DirectPrice.isin([0,np.NaN])]
        
        routes[origin][country] = {i.Name:{'city_code':i.Id,
                                           'd_price':i.DirectPrice,
                                           'ind_price':i.IndirectPrice} for i in df_cit.itertuples()}
