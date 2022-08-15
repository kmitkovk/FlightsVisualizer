# Flights Scraper

## UX1 - <i>Where to?</i>
1. User enters nearby airports
   - the app checks for all connections (destinations) with them
   - checks if the destination coordinates and details are in the DB
   - if not, saves those details in the airports database (ADB)
2. User enters the price range and months
3. The app displays the connections onto the map with price details
   - user can click on the origins and destinations for details
4. When you click on a destination the following could appear:
   - A barchart of the next three months of possible combinations (origin)
   - the barchart will have two series (1) 'to' and (2) 'from' flights

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

--------------------------------------------------------
### TODO
--------------------------------------------------------
- ~~Date range grid~~
- ~~Limit number of months shown for perormance~~
- Days ago - last timestamp
- ~~Fix number of flights in grid (y axis labels) -> nothing to fix (y-axis shrinks it)~~
- ~~Add VCE to datavase~~
- [Route folder](https://docs.microsoft.com/en-us/azure/app-service/configure-language-python#customize-startup-command) so that you could be pushing the latest version to cloud
- Map -> limit to months
- Flight stats page
- Make Map the home or [default page](https://community.plotly.com/t/introducing-dash-pages-a-dash-2-x-feature-preview/57775)
- ``Install SQLAlchemy``
- Add table for country-city data with month and timestamp (to be used for caching)
  - DrawSQL [link](https://drawsql.app/teams/gmat/diagrams/flightvisualizer2)
- Database => transfer files
  - change password database
  - shee the .env emails for explanation
- UX1 -> on hover show data, on click show second chart
- Progress info UX2 ( 20/35 loaded ...35%) -> show this under the loading button with modal!
  - read [here](https://towardsdatascience.com/long-callbacks-in-dash-web-apps-72fd8de25937) or [here](https://dash.plotly.com/long-callbacks) for more info
- Schedule script to track 3 flights (three locations) for price changes
- last update info box
- Up the scrape price to 150 (test before what the incrase it)
- Optimize main scripts:
  - grid selection
  - timeline [upgrades](https://plotly.com/python-api-reference/generated/plotly.express.timeline.html)
  - Python | Pandas Split strings into two List/Columns using str.split()
  - map
  - Try out the [highcharts map](https://towardsdatascience.com/highly-interactive-data-visualization-cd3a9b082370#:~:text=Panel%2DHighcharts%20is%20a%20python,python%20for%20Exploratory%20Data%20Analysis.) again
- App layout improvement -> [mobile verision](https://stackoverflow.com/questions/22985370/making-the-bootstrap-dashboard-example-sidebar-visible-available-on-mobile) and collapsable window
- ~~
--------------------------------------------------------
<br>

## Azure services
### Steps to deploy to azure for new branch:
1. Create web app in azure
2. Go to [configurations](https://portal.azure.com/#@kmitkovkerlievgmail.onmicrosoft.com/resource/subscriptions/ea1de4dc-316d-4041-baf0-5824b53e3cfc/resourcegroups/KMK_RG_GENERIC/providers/Microsoft.Web/sites/flightvis/configuration) and add the environment variables
   * WEBSITE_WEBDEPLOY_USE_SCM and set it to true
   * add other variables and passwords such as databases etc
   * wait 1 minute for the changes to take effect
3. Add the github configuration in [Deployment Center](https://portal.azure.com/#@kmitkovkerlievgmail.onmicrosoft.com/resource/subscriptions/ea1de4dc-316d-4041-baf0-5824b53e3cfc/resourcegroups/KMK_RG_GENERIC/providers/Microsoft.Web/sites/flightvis/vstscd)
4. Deploy and this is going to start building the app and send to github for workactions
   * Workflow actions are set per branch and have specific configuration
   * in order to avoid merges on the old branch, always do git fetch before you commit changes locally 

### Useful links for database handling and debugging
- In this [stackoverflow post](https://stackoverflow.com/questions/68867980/connection-to-microsoft-azure-sql-database-works-in-local-enviornment-but-not-in) there is a very nice description on (1) how to handle the database auth and (2) how to debug remotely
- Another [link](https://docs.microsoft.com/en-us/visualstudio/debugger/remote-debugging?view=vs-2019) on how to deal with the auth from DB in a webapp
- The remote debug [link could be accessed here](https://hedihargam.medium.com/python-sql-database-access-with-managed-identity-from-azure-web-app-functions-14566e5a0f1a)

<br>

### General Instrucitons:
- Last highest number of calls was `~400 calls` (190x2) on date_price data
  - This included 5 cities and intermediary scrape on cnt-city data
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

<br>

