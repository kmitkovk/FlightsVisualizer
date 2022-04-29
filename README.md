# Flights Scraper

## Objective:
- hover over airport to highligh country (like in ICIS)
- calculate all weekend retreats, if not per cities then per countries (IT)


## Current workflow:
1. For every origin scrape countries
2. For every country scrape cities
3. Map those to the map

### TODO Instrucitons:
1. Scrape origin countries once a month too
2. Scrape country/city overview only once a month
   - this is because those don't change so often
   - and you will be getting the prices from step 2 below
   - also, you reduce the number of calls
3. One dail or weekly basis (depending on how often you want to have prices updated), scrape `origin-city`
4. Create weekend retreat, graphical UI based on # on vacation for the next 2 months (?)
4. Map on map