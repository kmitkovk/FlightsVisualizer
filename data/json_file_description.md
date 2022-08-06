# Data files describtion (.json)

## example_json_dest_countries.json 
* gets destination countries from a given origin
* in this example we have ZAG to anywhere for Aug 2022
* [URL page](https://www.skyscanner.net/transport/flights-from/zag/?adults=1&adultsv2=1&cabinclass=economy&children=0&childrenv2=&inboundaltsenabled=false&infants=0&originentityid=27537474&outboundaltsenabled=false&oym=2208&preferdirects=true&ref=home&rtn=0)
* [URL json](https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/v3/bvweb/SI/EUR/en-GB/destinations/ZAG/anywhere/2022-08/?profile=minimalcityrollupwithnamesv2&include=image;hotel;adverts&apikey=8aa374f4e28e4664bf268f850f767535&isMobilePhone=false&isOptedInForPersonalised=true)

## example_json_dest_cities.json
* gets destination cities from the countries in example_json_dest_countries.json
* details include `CityName, CountryName, DirectPrice, IndirectPrice, ImageUrl`
* [URL json](https://www.skyscanner.net/g/browse-view-bff/dataservices/browse/v3/bvweb/SI/EUR/en-GB/destinations/ZAG/DE/2022-08/?profile=minimalcityrollupwithnamesv2&include=image;hotel&apikey=8aa374f4e28e4664bf268f850f767535&isMobilePhone=false)

## explore_calendar.json
* gives detail on flights from origin to city in a given month
* details include `dates and prices`
* [URL page](https://www.skyscanner.net/transport/flights/zag/mila/220818/?adultsv2=1&cabinclass=economy&childrenv2=&inboundaltsenabled=false&outboundaltsenabled=false&preferdirects=true&priceSourceId=&priceTrace=202208041021*D*ZAG*BGY*20220818*ryan*FR&qp_prevCurrency=EUR&qp_prevPrice=56&qp_prevProvider=ins_month&rtn=0)
* [URL json](https://www.skyscanner.net/g/monthviewservice/SI/EUR/en-GB/calendar/ZAG/MILA/2022-08/?profile=minimalmonthviewgridv2&apikey=6f4cb8367f544db99cd1e2ea86fb2627) 

## explore_itinieries.json
* `this appears useless` as it comes from a selection of a single date on a calendar for Aug 2022 ZAG-Milan (Bergamo)
* also, it doesn't seem queriable as the link is encrypted
* I tested the nested data and it all refers to one day (18-Aug-2022)
* Also, not a lot of useful infomation is present for cities except <ins>`some city IDs`</ins>
* [URL json](https://www.skyscanner.net/g/conductor/v1/fps3/search/8bd5ac34-11c3-48d1-8335-d353310dd0f1?geo_schema=skyscanner&carrier_schema=skyscanner&response_include=query%3Bdeeplink%3Bsegment%3Bstats%3Bfqs%3Bpqs) 

<BR><BR>

## Important notes from [Flights API](https://www.partners.skyscanner.net/contact/affiliates?hsLang=en):

Our Flights API is available on a commercial basis only. We select partners on case-by-case basis, so it's essential that you include as much information as possible in your application below. 

If you are an established business with a large audience or a start-up with a strong business plan, you may be selected to get access to our Flights API.

Please note, we `cannot give access to`:
* students and other individuals (i.e. `working on a non-commercial basis`)
* start-ups without a robust business plan 
* businesses with low-traffic sites