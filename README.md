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

<br>


### TODO immediate:
1. make a timeline of departures
2. then make a timeline of arrivals back
3. and then try to match all
4. and finally create a graph

### TODO Instrucitons:
1. Scrape origin countries once a month too
2. Scrape country/city overview only once a month
   - this is because those don't change so often
   - and you will be getting the prices from step 2 below
   - also, you reduce the number of calls
3. On daily or weekly basis (depending on how often you want to have prices updated), scrape `origin-city`
4. Extra-> hover over airport to highligh country (like in ICIS)
