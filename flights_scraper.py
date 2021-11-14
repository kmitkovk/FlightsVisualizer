# -*- coding: utf-8 -*-
"""
Created on Sat Oct 30 13:14:18 2021

@author: krasimirk
"""
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import webbrowser
import requests
import json
import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
pio.renderers.default = "browser"

import os


from plotly.offline import plot
import re
import webbrowser

#%% TODO
"""
    1. Cache the aiports, cities and cooradination on the ones already scraped
    2. Show direct and indirect prices (data already there)
    3. On point click redirect to calendar for booking
    4. Inlclude image URL on hover
"""   

#%% Instructions
"""
    1. Select airport and travel months and replace in selection below
    2. Run open url and open all the countries with price < 50eur
        - start from bottom to top and click on the arrows to open
    3. Right click and Inspect, then copy the whole HTML element (copy element)
    4. Save the file to folder and run 'Scrape and Parse' section 
"""    

# oym= 2111 #outbound year month #November 2021
# iym= 2111 #inbound year month #November 2021

# origin_airports = {'Treviso':'tsf',
#                    'Trieste':'trs',
#                    'Zagreb':'zag',
#                    'Ljubljana':'lju'}

# city = list(origin_airports.keys())[0]

# for city in list(origin_airports.keys()):
#     p1 = f'https://www.skyscanner.net/transport/flights-from/{origin_airports[city]}/?adults=1&adultsv2=1&cabinclass=economy&'
#     p2 = f'children=0&childrenv2=&inboundaltsenabled=false&infants=0&iym={iym}&originentityid=27547373&'
#     p3 = f'outboundaltsenabled=false&oym={oym}&preferdirects=false&preferflexible=false&ref=home&rtn=1'
#     link = p1+p2+p3
    # webbrowser.open(link)


#%% Scrape and parse

#https://beautiful-soup-4.readthedocs.io/en/latest/#navigating-the-tree

# routes = {}
# for airport in origin_airports.keys():
#     file = fr'D:\Code\Others\FlightsScraper\{airport}_to_anywhere.txt'
#     with open(file, 'r', encoding='utf8') as f:
#         html = f.read()
#     soup = BeautifulSoup(html, 'html.parser')
    
    
#     countries_cities = {}
#     for country in soup.find_all("li", class_="browse-list-category open"):
#         cnt = country.find_all("h3")[0].text
#         cities = country.find_all("h3")[1:]
#         prices = country.find_all("span", class_="price flightLink") #[0].text.split()[1]
#         prices_clean = [int(price.text.split()[1]) for price in prices]
#         cities_clean = [city.text for city in cities]
#         countries_cities[cnt] = dict(zip(cities_clean, prices_clean))
#         # print(f'Cities: {[city.text for city in cities]}\nPrice: {price_clean}\n\n\n')
#         # print(f'Cities: {cities}\nPrice: {price}\n\n\n')

#     routes[airport] = countries_cities

# # unique_countries = list(set([country for origin in routes.keys() 
# #                              for country in routes[origin].keys()]))

# city_countries = [(cities,country) for origin in routes.keys() 
#                                    for country in routes[origin].keys() 
#                                       for cities in routes[origin][country]]


#%% Map coordinates
#map for geojson

# def find_geo_coors(city_country): #using city only is not accurate
#     coordinates = {}
#     link_geo_api = f'http://api.positionstack.com/v1/forward?access_key=53fd1242060dbfc196a1f76ff3bc4ebf&query={city_country}'
#     resp = requests.get(link_geo_api)
#     return json.loads(resp.text)

# coordinates_dest = {}
# for city, country in city_countries:
#     if city not in coordinates_dest.keys():
#         coordinates_dest[city] = find_geo_coors(city + ', ' + country)

# coordinates_origin = {}
# for city in origin_airports.keys():
#     coordinates_origin[city] = find_geo_coors(city)

#%% Visualize 
#https://plotly.com/python/lines-on-maps/
#https://plotly.com/python/scattermapbox/
#https://community.plotly.com/t/hyperlink-to-markers-on-map/17858/6


#%%% Cached data use:

direct_only = True
iym= 2111 #inbound year month #November 2021
oym= 2111 #outbound year month #November 2021

origin_airports = {'Treviso':'TSF',
                   'Trieste':'TRS',
                   'Ljubljana':'LJU',
                   'Zagreb':'ZAG'}


curr_dir = os.getcwd()
cache_loc = os.path.join(curr_dir + '\data\cache')    
city_data = pd.read_csv(os.path.join(curr_dir + '\data\city_data.csv'))
    

routes_data_loc = os.path.join(curr_dir + f'\\data\\routes_data\{iym}-{oym}')

try:
    print(os.listdir(path = routes_data_loc))
except:
    raise Exception('Deprature-arrival folder does not exist, scrape the data first!')

dest_columns_and_rename = {'Id':'dest_city_code',
                          'Name':'dest_city',
                          'CountryName':'dest_country_name',
                          'ImageUrl':'dest_link_picture',
                          'Direct':'direct_flag',
                          'IndirectPrice':'dest_price_indir',
                          'DirectPrice':'dest_price_dir'}

# df_routes = pd.DataFrame([], columns = ['orig_city', 'orig_country',
#                                         'orig_city_code', 'orig_country_code',
#                                         'dest_country_name','dest_country_code',
#                                         'dest_direct_price', 'dest_indirect_price',
#                                         'dest_link_picture', 'dest_link_booking',
#                                         'dest_lat', 'dest_lon','direct_flag',
#                                         'dest_price_dir', 'dest_price_indir', 
#                                         'dest_city', 'dest_city_code',
#                                         ])

df_routes = pd.DataFrame([], columns = ['orig_code'] + list(dest_columns_and_rename.values()))

for origin_fold in os.listdir(path = routes_data_loc):
    destinations_files = [i for i in os.listdir(path = routes_data_loc +
                                    f'\\{origin_fold}') if 'to_' in i] # check if origin + dest file
    
    origin_code = origin_fold.split('_')[0]
    for dest in destinations_files:
        df_dest = pd.read_csv(routes_data_loc + f'\\{origin_fold}' + f'\\{dest}')
        df_dest = df_dest.loc[:,dest_columns_and_rename.keys()].rename(columns = dest_columns_and_rename)
        df_dest['orig_code'] = origin_code 
        df_routes = df_routes.append(df_dest, sort = False)
        
        print('fix handling indirect/direct prices as well as direct prices NaNs')
        if direct_only:
            df_routes = df_routes[~ df_routes.dest_price_dir.isna()]
            
df_routes = df_routes.merge(city_data, how = 'left', left_on = 'dest_city_code', right_on = 'Id').drop(
                            ['Id', 'CityName', 'CountryName', 'CountyCode', 'ImageUrl'], axis = 1)
        
origins_data = {code.upper():{'orig_city':name,
                            'orig_country':city_data[city_data.CityName == name].CountryName.values[0],
                            'orig_country_code':city_data[city_data.CityName == name].CountyCode.values[0],
                            'orig_lon':city_data[city_data.CityName == name].lon.values[0],
                            'orig_lat':city_data[city_data.CityName == name].lat.values[0]} 
                                                       for name,code in origin_airports.items()}

#%%% PLOT
# colors = px.colors.sequential.Viridis
# colors = ['red','green','darkorange','blue']
colors = ['rgb(102,102,102)','rgb(27,158,119)','rgb(217,95,2)','#750D86'] #px.colors.qualitative.Dark2 #https://plotly.com/python/discrete-color/
skip = int(len(colors)/len(routes.keys()))
assert len(colors) >= len(routes.keys()), 'Not enough colors for all cities'
count = 0

price_cap = 70
num_dest = 0
# dest_offset = 0 # offset destination if there are more than two routes to it
# cities = [city[0] for city in city_countries]
# dest_repetition = {city:{'rep':cities.count(city),'offset':0} 
#                    for city in cities if cities.count(city) > 1}
#duplicates handle
# df_routes[df_routes.dest_city.duplicated()]
#%%
fig = go.Figure()
for origin in origins_data.keys():
    orig_df = df_routes[df_routes.orig_code == origin]

    orig_lon = origins_data[origin]['orig_lon']
    orig_lat = origins_data[origin]['orig_lat']

    show_legend = True
    
    # fig.add_trace( #LINES
    #     go.Scattermapbox(
    #     # lon = [orig_lon, dest_lon + offset],
    #     lon = [[orig_lon for i in orig_df], orig_df.lon],
    #     lat = [[orig_lat for i in orig_df], orig_df.lat],
    #     # name = f'from {origin}',
    #     # legendgroup=origin,
    #     # showlegend=show_legend,
    #     showlegend=False,
    #     mode = 'lines',
    #     # text = [city + f' from {origin} from €{price}'],
    #     # hoverinfo = 'text',
    #     # line = dict(width = 1,color = colors[count]),
    #     # opacity = 1- (price/price_cap),
    #                 )
    #             )
    #%%
    fig = go.Figure(go.Scattermapbox(
        lat=['45.5017'],
        lon=['-73.5673'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=14
        ),
        text=['Montreal'],
    ))
    fig.show()
    #%%
    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
    lon = [orig_lon],
    lat = [orig_lat],
    mode = 'markers'))
    
    fig.show()
    #%%
    fig.add_trace(go.Scattermapbox( # MARKERS for the points of origins (moved this sections below because of hovers
    lon = [orig_lon],
    lat = [orig_lat],
    text = [origin],
    name = origin,
    legendgroup=origin,
    hoverinfo = 'text',
    showlegend = True,
    mode = 'markers',
                        ))
    #%%
    # count += skip

y_offset = 0
for city in origins_data.keys():
    p1 = f'https://www.skyscanner.net/transport/flights-from/{origin_airports[city]}/?adults=1&adultsv2=1&cabinclass=economy&'
    p2 = f'children=0&childrenv2=&inboundaltsenabled=false&infants=0&iym={iym}&originentityid=27547373&'
    p3 = f'outboundaltsenabled=false&oym={oym}&preferdirects=false&preferflexible=false&ref=home&rtn=1'
    link = p1+p2+p3
    fig.add_annotation(x=1.023, y=0.905-y_offset,
                        text = f"<sub><a href='{link}'>link</a></sub>",
                        showarrow=False,
                )
    y_offset += 0.039

fig.update_layout( #https://plotly.com/python/mapbox-layers/
    title_text = f'Number of destinations at price €{price_cap} - {num_dest}',
    legend_title_text='<br><b>From airport:</b><br>'+'<sub>[double-click to filter]</sub><br>',
    title_x=0.5,
    # autosize=True,
    # hovermode='closest',
    mapbox_style="carto-positron", #"open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain", "stamen-toner" or "stamen-watercolor" 
    mapbox=dict(
        # accesstoken=mapbox_access_token,
        center=dict(lat = 46.063562, lon = 14.48854),
        zoom=3.5),
                )

# fig.show()
if False:
    fig.write_html(r'D:\Code\Others\FlightsScraper\visual.html')

#% % custom data with links
if True:
    plot_div = plot(fig, output_type='div', include_plotlyjs=True)

    # Get id of html div element that looks like
    # <div id="301d22ab-bfba-4621-8f5d-dc4fd855bb33" ... >
    res = re.search('<div id="([^"]*)"', plot_div)
    div_id = res.groups()[0]
    
    # Build JavaScript callback for handling clicks
    # and opening the URL in the trace's customdata 
    js_callback = """
    <script>
    var plot_element = document.getElementById("{div_id}");
    plot_element.on('plotly_click', function(data){{
        console.log(data);
        var point = data.points[0];
        if (point) {{
            console.log(point.customdata);
            window.open(point.customdata);
        }}
    }})
    </script>
    """.format(div_id=div_id)
    
    # Build HTML string
    html_str = """
    <html>
    <body>
    {plot_div}
    {js_callback}
    </body>
    </html>
    """.format(plot_div=plot_div, js_callback=js_callback)
    
    # Write out HTML file
    with open(r'D:\Code\Others\FlightsScraper\hyperlink_fig.html', 'w') as f:
        f.write(html_str)

# fig.update_layout( # this is for the simpler map -> Scattergeo vs Scattermapbox
#     title_text = f'Number of destinations at price €{price_cap} - {num_dest}',
#     # showlegend = True,
#     geo = dict(
#         # scope = ["africa","asia", "europe", "north america", "south america"],
#         # projection_type = 'azimuthal equal area', #natural earth
#         projection_type = 'robinson',
#         center = dict(lat = 46.063562, lon = 14.48854),
#         projection = dict(scale = 5),
#         landcolor = 'rgb(243, 243, 243)',
#         countrycolor = 'rgb(204, 204, 204)',
#     ),
# )
# webbrowser.get(r'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s').open(r'D:\Code\Others\FlightsScraper\hyperlink_fig.html')





# for origin in routes.keys():
#     orig_lon = coordinates_origin[origin]['data'][0]['longitude']
#     orig_lat = coordinates_origin[origin]['data'][0]['latitude']
#     show_legend = True
#     for country in routes[origin]:
#         for city in routes[origin][country].keys():
#                 dest_lon = coordinates_dest[city]['data'][0]['longitude']
#                 dest_lat = coordinates_dest[city]['data'][0]['latitude']
#                 price = routes[origin][country][city]
#                 if price >= price_cap:
#                     continue
#                 num_dest += 1
                
#                 if city in dest_repetition.keys():
#                     change_magn = 0.01
#                     offset = dest_repetition[city]['offset']
#                     dest_repetition[city]['offset'] = dest_repetition[city]['offset'] + change_magn
                
#                 fig.add_trace( #LINES
#                     go.Scattermapbox(
#                     lon = [orig_lon, dest_lon + offset],
#                     lat = [orig_lat, dest_lat + offset],
#                     name = f'from {origin}',
#                     legendgroup=origin,
#                     # showlegend=show_legend,
#                     showlegend=False,
#                     mode = 'lines',
#                     text = [city + f' from {origin} from €{price}'],
#                     hoverinfo = 'text',
#                     line = dict(width = 1,color = colors[count]),
#                     opacity = 1- (price/price_cap),
#                                 )
#                             )
#                 if origin == 'Treviso':
#                     try:
#                         link = f'https://www.skyscanner.net/transport/flights/tsf/{codes[city]}/?adultsv2=1&cabinclass=economy&childrenv2=&inboundaltsenabled=false&iym=2111&outboundaltsenabled=false&oym=2111&selectedoday=12&selectediday=12'
#                     except:
#                         link = ''
#                 else:
#                     link = ''
                    
#                 show_legend = False
#                 fig.add_trace(go.Scattermapbox( #MARKERS
#                     lon = [dest_lon + offset],
#                     lat = [dest_lat + offset],
#                     text = [city + f', {country} from €{price}'],
#                     hoverinfo = 'text',
#                     mode = 'markers',
#                     legendgroup=origin,
#                     # showlegend = show_legend,
#                     showlegend = False,
#                     customdata=[link],
#                     line = dict(width = 1,color = colors[count]),
#                     opacity = 1- (price/price_cap),
#                                 )
#                                             )
#     fig.add_trace(go.Scattermapbox( #moved this sections below because of hovers
#     lon = [orig_lon],
#     lat = [orig_lat],
#     text = [origin],
#     name = origin,
#     legendgroup=origin,
#     hoverinfo = 'text',
#     showlegend = True,
#     mode = 'markers',
#     marker = dict(size = 9, color = colors[count])))

#     count += skip

# y_offset = 0
# for city in routes.keys():
#     p1 = f'https://www.skyscanner.net/transport/flights-from/{origin_airports[city]}/?adults=1&adultsv2=1&cabinclass=economy&'
#     p2 = f'children=0&childrenv2=&inboundaltsenabled=false&infants=0&iym={iym}&originentityid=27547373&'
#     p3 = f'outboundaltsenabled=false&oym={oym}&preferdirects=false&preferflexible=false&ref=home&rtn=1'
#     link = p1+p2+p3
#     fig.add_annotation(x=1.023, y=0.905-y_offset,
#                         text = f"<sub><a href='{link}'>link</a></sub>",
#                         showarrow=False,
#                 )
#     y_offset += 0.039

# fig.update_layout( #https://plotly.com/python/mapbox-layers/
#     title_text = f'Number of destinations at price €{price_cap} - {num_dest}',
#     legend_title_text='<br><b>From airport:</b><br>'+'<sub>[double-click to filter]</sub><br>',
#     title_x=0.5,
#     # autosize=True,
#     # hovermode='closest',
#     mapbox_style="carto-positron", #"open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain", "stamen-toner" or "stamen-watercolor" 
#     mapbox=dict(
#         # accesstoken=mapbox_access_token,
#         center=dict(lat = 46.063562, lon = 14.48854),
#         zoom=3.5),
#                 )
