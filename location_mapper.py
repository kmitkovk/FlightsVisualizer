# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 11:47:14 2021

@author: krasimirk
"""

import urllib.request, urllib.parse, urllib.error
import requests
import json
import ssl


def find_geo_coors_ps_api(city_country):  # using city only is not accurate
    coordinates = {}
    link_geo_api = f"http://api.positionstack.com/v1/forward?access_key=53fd1242060dbfc196a1f76ff3bc4ebf&query={city_country}"
    resp = requests.get(link_geo_api)
    return json.loads(resp.text)


def find_geo_coors_google_api():
    """This is a google API for this which is better but maybe more
    limited to number of calls in the script locatiion_scraper.py"""
    api_key = False
    # If you have a Google Places API key, enter it here
    # api_key = 'AIzaSy___IDByT70'
    # https://developers.google.com/maps/documentation/geocoding/intro
    if api_key is False:
        api_key = 42
        serviceurl = "http://py4e-data.dr-chuck.net/json?"
    else:
        serviceurl = "https://maps.googleapis.com/maps/api/geocode/json?"
    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    while True:
        address = input("Enter location: ")
        if len(address) < 1:
            break
        parms = dict()
        parms["address"] = address
        if api_key is not False:
            parms["key"] = api_key
        url = serviceurl + urllib.parse.urlencode(parms)
        print("Retrieving", url)
        uh = urllib.request.urlopen(url, context=ctx)
        data = uh.read().decode()
        print("Retrieved", len(data), "characters")
        try:
            js = json.loads(data)
        except:
            js = None
        if not js or "status" not in js or js["status"] != "OK":
            print("==== Failure To Retrieve ====")
            print(data)
            continue
        print(json.dumps(js, indent=4))
        lat = js["results"][0]["geometry"]["location"]["lat"]
        lng = js["results"][0]["geometry"]["location"]["lng"]
        print("lat", lat, "lng", lng)
        location = js["results"][0]["formatted_address"]
        print(location)
