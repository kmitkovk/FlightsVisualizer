# -*- coding: utf-8 -*-
"""
Created on Sat Aug  5 17:48:40 2023

@author: krasimir.kerliev
"""

import json
import requests
import pandas as pd

# %%
headers = {
    "authority": "www.skyscanner.net",
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "referer": "https://www.skyscanner.net/transport/flights-from/sof/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "x-skyscanner-locale": "en-GB",
    "x-skyscanner-market": "SI",
    "x-skyscanner-currency": "EUR",
    "x-skyscanner-channelid": "banana",
}

max_price = 100
year = 2023
month = 9
origin = "SOF"

# entity_code:
headers["referer"] = f"https://www.skyscanner.net/transport/flights-from/{origin}/"
url_origin = f"https://www.skyscanner.net/g/banana/tallyman/context?qp_prevScreen=HOMEPAGE&path=/transport/flights-from/{origin}/"
response_origin = requests.request("GET", url_origin, headers=headers)

# %% Extract countries
# t = {"cookie": """traveller_context=9b6c0a6f-169a-4962-b740-c4ff9d33071f; __Secure-anon_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImM3ZGZlYjI2LTlmZjUtNDY4OC1iYjc3LWRiNTY2NWUyNjFkZSJ9.eyJhenAiOiIyNWM3MGZmZDAwN2JkOGQzODM3NyIsImh0dHBzOi8vc2t5c2Nhbm5lci5uZXQvbG9naW5UeXBlIjoiYW5vbnltb3VzIiwiaHR0cHM6Ly9za3lzY2FubmVyLm5ldC91dGlkIjoiOWI2YzBhNmYtMTY5YS00OTYyLWI3NDAtYzRmZjlkMzMwNzFmIiwiaHR0cHM6Ly9za3lzY2FubmVyLm5ldC9jc3JmIjoiMWUwYjJiOTE4MmIxNTc5NzFjZDZjNGMyZjYwYTY3MjIiLCJodHRwczovL3NreXNjYW5uZXIubmV0L2p0aSI6IjkzMmI0OGYxLTU4MTktNDM5ZC04MWU0LWQ3N2QwYWQwNzNkMCIsImlhdCI6MTY3MzcyMjg5MSwiZXhwIjoxNzM2Nzk0ODkxLCJhdWQiOiJodHRwczovL2dhdGV3YXkuc2t5c2Nhbm5lci5uZXQvaWRlbnRpdHkiLCJpc3MiOiJodHRwczovL3d3dy5za3lzY2FubmVyLm5ldC9zdHRjL2lkZW50aXR5L2p3a3MvcHJvZC8ifQ.SVGEcEF-qMVPgRQwt1kuh_TvMcaa-5t97B6hfH_aiuEoPxmo9ex66uT4KRWv32Uh3HK9JZcQeBIZ7F-duBU6u5k2aIT0omfAqJYMcSop2pPSCILGAEK7zllyHLvA9mPhJ2vKRZiScH1PKJrBQ6jaF3FfmNZmM4ob-TFElRX8WQlaOM_xPAxK3Om-ZJ2gWAoO1XC0Fw-wxm8cK3by8IQpq_ClN7J9ioFd2YMaj1JwVOt-3eeet952XHIWRAnyGa-ePdE5atcYyIo-XjpQO3svpLlQzjB6YrGJtYRmYQmhjSdodqZWY6UDTOZB7bA8aO2P8zjJ4_MVKPM9rJPSLzntWA; __Secure-anon_csrf_token=1e0b2b9182b157971cd6c4c2f60a6722; ssculture=locale:::en-GB&market:::SI&currency:::EUR; __Secure-ska=f679c0f7-1112-48fc-9e0a-88db084fdec2; device_guid=f679c0f7-1112-48fc-9e0a-88db084fdec2; preferences=9b6c0a6f169a4962b740c4ff9d33071f; _ga=GA1.2.331722869.1673722894; _pxvid=db9a4144-943d-11ed-a9fa-7a414a766941; __pxvid=dce91a5b-943d-11ed-b89c-0242ac120003; gdpr=information:::true&adverts:::true&version:::2; __gsas=ID=10d968404fe228b8:T=1673722910:S=ALNI_Makd6_bucQ6bPgX8fbOEGHbbc4jMA; g_state={"i_p":1682072708576,"i_l":1}; abgroup=32183586; jha=AQBSFYK0RArRzVCQrx0LyiCik6qZZGPdmWQA; _gac_UA-246109-1=1.1687805285.Cj0KCQjw7uSkBhDGARIsAMCZNJs6pkQCRgZ0__gzVBgxZtCwJxNWvGWuKXIDxMeC8V6ryYnt8Vc1d8gaAnnPEALw_wcB; _gcl_au=1.1.265621826.1689761261; QSI_S_ZN_0VDsL2Wl8ZAlxlA=v:0:0; _pxhd=ZMjUK4Xf9SGOQRRrTx4uGrjG/UX7U1qMRbw1OjrnB8tY2KJIaaQiE1endlBYq8MCQKgrWkRgeOZhznuXRpnpmg==:tVLUxpLcRIeWoBqPFpshXOIRk2Ck9WHMujfSuWMNXQn21NhbD28h93pqDdlhEWpPnxRLjYOl5KmyhEffQ2PSYchRDee7XEBFFQQG8ZNJI2U=; ssab=Alternatives_Inventory_Via_Ads_Acorn_V9:::a&Autosuggest_Flight_NearBy_Airport_2_V3:::b&Datepicker_One_Way_Return_Experiment_V7:::b&Experiment_Alternatives_Inventory_Hide_Result_V9:::b&MAT_carhire_dv_quote_insurance_policies_on_Desktop_V3:::b&Multi_city_search_Nav_Card_on_Desktop_V3:::a&dummy_jekyll2_V0:::a&filter_wrong_pricing_options_V5:::b&fps_mr_fqs_flights_ranking_haumea_v5__25i_web_V3:::a&fps_ttlr_early_timeout_banana_V83:::a&fps_ttlr_early_timeout_web_V21:::a; experiment_allocation_id=da2ab33556001490971d59b60dd17d771c87fe340ed40af79a8d590ef7d99554; ssaboverrides=; pxcts=6292373d-339b-11ee-92d6-6e4647585166; _gid=GA1.2.1485691199.1691245844; __hs_opt_out=yes; _uetsid=0e85fa90339e11ee9bcc5fcf83b3a0c5; _uetvid=df2ff880943d11edaee8698143592b81; _px3=a683a2eab745568473c07b7f928d3f67798ca20325aaccf059c1f3636fd32485:f/EDgwq5KcF3oaBtPe/z7p+T8zpWltH1A1GdWSXXc1/LVRUo6GQbvobNAPiSkTI5/TsudxjMC2mKwffcCg9VCg==:1000:t0VDbHQBZt1qpWb7mtixUeGExamstUS3Hw1ESfuLFJN1rLUVb5MAYFKKH1G7b1+HCqJQjsGsxP0/wQb4aT1s3bXgtXlRQst4eV8sz9wf+uVI3d+dxYwapnGLgDAnmdCqlsS2i1siFkhpjm0MQ+17PnIubzobqZZjfATFbVHVN8QyMW6cn6MaCp814xUXN+3smUPupzPrW4OF7eru9MQB4A==; scanner=currency:::EUR&legs:::SOF|2023-09|everywhere&tripType:::one-way&rtn:::false&preferDirects:::false&outboundAlts:::false&inboundAlts:::false&from:::SOF&to:::everywhere&oym:::2309&oday&wy:::0&iym:::2309&iday:::07&cabinclass:::Economy&adults:::1&adultsV2:::1&children:::0&childrenV2&infants:::0""",}

origin_id = response_origin.json()["context"]["flightSearch"]["origin"]["entityId"]


url_countries = "https://www.skyscanner.net/g/radar/api/v2/web-unified-search/"
headers["referer"] = f"https://www.skyscanner.net/transport/flights-from/{origin}/"

pl_json = {'adults': 1,
           'childAges': [],
           'legs': [{'legOrigin': {'@type': 'entity', 'entityId': origin_id},
                     'legDestination': {'@type': 'everywhere'},
                     'dates': {'@type': 'month', 'year': year, 'month': month}}]}

payload = json.dumps(pl_json)
# payload = f'{"adults":1,"childAges":[],"legs":[\r\n  {\r\n    "legOrigin": {\r\n      "@type": "entity",\r\n      "entityId": "95673503"\r\n    },\r\n    "legDestination": {\r\n      "@type": "everywhere"\r\n    },\r\n    "dates": {\r\n      "@type": "month",\r\n      "year": 2023,\r\n      "month": 9\r\n    }\r\n  }\r\n]}'
response_cnt = requests.request("POST", url_countries, headers=headers, data=payload)
json_data_cnt = response_cnt.json()


cnt_dict = {
    "name_dest_cnt": [],
    "dest_cnt_ISO_2": [],
    "cnt_skys_id": [],
    "direct_price_dest_cnt": [],
}
for i in json_data_cnt["everywhereDestination"]["results"]:
    if i["type"] == "ADVERT":
        continue
    if "direct" in i["content"]["flightQuotes"].keys():
        cnt = i["content"]["location"]["name"]
        cnt_code = i["content"]["location"]["skyCode"]
        cnt_id = i["content"]["location"]["id"]
        cnt_price = i["content"]["flightQuotes"]["direct"]["price"]
        cnt_price = int(cnt_price.strip(" €"))

        if cnt_price > max_price:
            continue
        cnt_dict["name_dest_cnt"] += [cnt]
        cnt_dict["dest_cnt_ISO_2"] += [cnt_code]
        cnt_dict["cnt_skys_id"] += [cnt_id]
        cnt_dict["direct_price_dest_cnt"] += [cnt_price]
df = pd.DataFrame(cnt_dict)
df["origin"] = origin
df["timestamp"] = pd.Timestamp("now").floor("Min")


# %% Extract city destinations

dest_id = '29475378'

pl_json = {'adults': 1,
           'childAges': [],
           'legs': [{'legOrigin': {'@type': 'entity', 'entityId': origin_id},
                     'legDestination': {'@type': 'entity','entityId': dest_id},
                     'dates': {'@type': 'month', 'year': year, 'month': month}}]}

payload = json.dumps(pl_json)
# payload = f'{"adults":1,"childAges":[],"legs":[\r\n  {\r\n    "legOrigin": {\r\n      "@type": "entity",\r\n      "entityId": "95673503"\r\n    },\r\n    "legDestination": {\r\n      "@type": "everywhere"\r\n    },\r\n    "dates": {\r\n      "@type": "month",\r\n      "year": 2023,\r\n      "month": 9\r\n    }\r\n  }\r\n]}'
response_cnt = requests.request("POST", url_countries, headers=headers, data=payload)
json_data_cnt = response_cnt.json()


res = json_data_cnt['countryDestination']['results']


