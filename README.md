# Flights Scraper

## UX1 - <i>Where to?</i>
1. User enters nearby airports
   - the app checks for all connections (destinations) with them
   - checks if the destination coordinates and details are in the DB
   - if not, saves those details in the airports database (ADB)
2. User enters the price range and months
3. The app displays the connections onto the map with price details
   - user can click on the origins and destinations for details

## UX2 - <i>Weekend retreat!</i>
1. User enters nearby airports and price range
2. User enters number of days at disposal and how many months ahead
   - next step,
   - next step,
3. Graphical UI is created to show a grid-like availability

## UX3 - <i>Find another route</i>
1. User enters nearby airports, destination and price range
2. User enters the date for which they are looking for transfer flights
3. User enteres day difference for the transfer flights `(time not available)`
4. The application does:
   - finds all the destinations from origin
   - finds all the destinations from destination
      - except here, to save on calls, run the loop orig-dest_city only on matching cities
   - matches up the flights that are interconnection points
   - matches up the daytime difference given by the user

<br>

## The three main files of data ([description](/data/json_file_description.md)):
1. [origin-countries data](/data/example_json_dest_countries.json)
2. [origin-countries_cities data](/data/example_json_dest_cities.json)
3. [origin-countries_cities calendar data](/data/example_calendar.json)

<br>

# 

### TODO:
1. finish get_destination_cities_dates_prices
2. design the Database for those two outputs
3. !Move onto UX2!
   1. make a timeline of departures
   2. then make a timeline of arrivals back
   3. and then try to match all
   4. and finally create a graph
4. !Move onto UX3!

<br>


### General Instrucitons:
0. For now scrape origin-destinations only once every few weeks
   - occasionally run a scraper if there have been new destinations added
   - however, new destinations could "pop up" because they could be filtered by the price
   - but even then you will just run a loop for the origin-dest_city not origin-dest_country
1. Scrape origin countries once a month too
2. Scrape country/city overview only once a month
   - this is because those don't change so often
   - and you will be getting the prices from step 2 below
   - also, you reduce the number of calls
3. On daily or weekly basis (depending on how often you want to have prices updated), scrape `origin-city`
4. Extra-> hover over airport to highligh country (like in ICIS)
