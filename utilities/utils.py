# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 11:47:14 2021

@author: krasimirk
"""

#%% Imports

import pandas as pd

#%% Functions
def check_if_existing_aiport():
    pass

def save_unexisting_airports():
    """record airports that were not found for later manual check and update"""
    #HAVE A PROVISION FOR THE GB UK descrepancy
    
    #airport codes databse (also saved in repo):
    #https://raw.githubusercontent.com/datasets/airport-codes/master/data/airport-codes.csv
    
    pass

def save_second_function_month():
    """if second funct (cities) scraped once for the origins, BETTER CACHE THAT"""
    pass

def check_existing_countries():
    pass

def check_existing_cities():
    pass

def check_exisiting_airports():
    pass

def create_flight_id():
    """
    flight_IDs should be added for a pair of flight,date e.g. ZAG-SOF, 2022-09-09
    This is needed so that TimeStampTicks can be saved and flights can be
        differenciated across ticks e.g. there could be the same flight 
        of ZAG-SOF, 2022-09-09 but with different ticks (update/scrape time)
        
    one thing to note tho is that those IDs should expire as days go by
        therefore maybe this should be done on the fly aka:
            when queriying based on timestamptick
    """
    pass

