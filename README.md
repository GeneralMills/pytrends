# pytrends

## Introduction

Unofficial API for Google Trends

Allows simple interface for automating downloading of reports from Google Trends. Main feature is to allow the script to login to Google on your behalf to enable a higher rate limit. Only good until Google changes their backend again :-P. When that happens feel free to contribute!


## Table of contens

* [Installation](#installation)

* [API](#api)

  * [API Methods](#api-methods)

  * [API Payload Keys](#api-payload-keys)

    * [interest_over_time](#interest_over_time)
    * [interest_by_region](#interest_by_region)
    * [related_queries](#related_queries)
    * [trending_searches](#trending_searches)
    * [top_charts](#top_charts)
    * [suggestions](#suggestions)

  * [Caveats](#caveats)

* [Credits](#credits)

## Installation

    pip install pytrends

## Requirements

* Written for both Python 2.7+ and Python 3.3+
* Requires a google account to use.
* Requires BeautifulSoup4, Requests, lxml, Pandas

[back to top](#introduction)

## API

### Connect to Google

    pytrends = TrendReq(google_username, google_password, hl='en-US', tz=360, custom_useragent=None)

#### Parameters

* google_username

  - *Required*
  - a valid gmail address

* google_password

  - *Required*
  - password for the gmail account

* hl

  - Localization to return results in. Defaults to US English.
  
* tz

  - Timezone to base requests from. Defaults to CST (Central Standard Time) UTC/GMT -6 hours

* custom_useragent

  - name to identify requests coming from your script

[back to top](#API)

## API Methods

The following API methods are available:

* [interest_over_time](#interest_over_time): returns historical, indexed data for when the keyword was searched most as shown on Google Trends' Interest Over Time section.

* [interest_by_region](#related): returns data for where the keyword is most searched as shown on Google Trends' Interest by Region section.

* [related_queries](#related_queries): returns data for the related keywords to a provided keyword  shown on Google Trends' Related Queries section.

* [trending_searches](#trending_searches): returns data for latest trending searches shown on Google Trends' Trending Searches section.

* [top_charts](#top_charts): returns the data for a given topic shown in Google Trends' Top Charts section.

* [suggestions](#suggestions): returns a list of additional suggested keywords that can be used to refine a trend search.

[back to top](#api-methods)

## Common API parameters

Many API methods use the following:

* `kw_list`

  - keywords to get data for
  - Example ```['Pizza']```
  - Up to five terms in a list: ```['Pizza, Italian, Spaghetti, Breadsticks, Sausage']```

    * Advanced Keywords

      - When using Google Trends dashboard Google may provide suggested narrowed search terms.
      - For example ```"iron"``` will have a drop down of ```"Iron Chemical Element, Iron Cross, Iron Man, etc"```. 
      - Find the encoded topic by using the get_suggestions() function and choose the most relevant one for you. 
      - For example: ```https://www.google.com/trends/explore#q=%2Fm%2F025rw19&cmpt=q```
      - ```"%2Fm%2F025rw19"``` is the topic "Iron Chemical Element" to use this with pytrends
      - You can also use `pytrends.suggestions()` to automate this.

* `hl`

  - Language to return result headers in
  - Two letter language abbreviation
  - For example US English is ```'en-US'```
  - Defaults to US english

* `cat`

  - Category to narrow results
  - Find available cateogies by inspecting the url when manually using Google Trends. The category starts after ```cat=``` and ends before the next ```&```
  - For example: ```"https://www.google.com/trends/explore#q=pizza&cat=71"```
  - ```'71'``` is the category
  - Defaults to no category

* `geo`

  - Two letter country abbreviation
  - For example United States is ```'US'```
  - Defaults to World
  - More detail available for States/Provinces by specifying additonal abbreviations
  - For example: Alabama would be ```'US-AL'```
  - For example: England would be ```'GB-ENG'```

* `tz`

  - Timezone Offset
  - For example US CST is ```'360'```

* `timeframe`

  - Date to start from
  - Defaults to last 5yrs, `'today 5-y'`.
  - Everything `'all'`
  - Single year, `'all_2008'`
  - Specific dates, 'YYYY-MM-DD YYYY-MM-DD' example `'2016-12-14 2017-01-25'`

  - Current Time Minus Time Pattern:

    - By Month: ```'today #-m'``` where # is the number of months from that date to pull data for
      - For example: ``{'date': 'today 61-m'}`` would get data from today to 61months ago
      - **NOTE** Google uses UTC date as *'today'*

    - Daily: ```'today #-d'``` where # is the number of days from that date to pull data for
      - For example: ``{'date': 'today 7-d'}`` would get data from the last week

    - Hourly: ```'now #-H'``` where # is the number of hours from that date to pull data for
      - For example: ``{'date': 'now 1-H'}`` would get data from the last hour

* `gprop`

  - What search data we want
  - Example ```'images'```
  - Defaults to web searches
  - Can be ```images```, ```news```, ```youtube``` or ```froogle``` (for Google Shopping results)

[back to top](#api-payload-keys)

## Interest Over Time

    pytrends.interest_over_time()

Returns pandas.Dataframe

[back to top](#interest_over_time)

## Interest by Region

    pytrends.interest_by_region(resolution='REGION')

### Parameters

* `resolution`

  - 'CITY' returns city level data
  - 'REGION' returns country level data

Returns pandas.DataFrame

[back to top](#interest_by_region)

## Related Queries

    pytrends.related_queries()

Returns dictionary of pandas.DataFrames

[back to top](#related_queries)

## Trending Searches

    pytrends.trending_searches()
Returns pandas.DataFrame

[back to top](#trending_searches)

top_charts

    pytrends.topcharts(date, cid, geo='US', cat='')

Parameters

* `date`

  - *Required*
  - YYYYMM integer or string value
  - Example `'201611'` for November 2016 Top Chart data
  
* `cid`

  - *Required*
  - Topic to get data for
  - Example `'athletes'`

Returns pandas.DataFrame

[back to top](#top_charts)

## Suggestions

    pytrends.suggestions(keyword)

Parameters

* `keyword`

  - *Required*
  - keyword to get suggestions for
  
Returns dictionary

[back to top](#suggestions)

Caveats
-------

* This is not an official or supported API
* Google may change aggregation level for items with very large or very small search volume
* Google will send you an email saying that you had a new login after running this.
* Rate Limit is not pubically known, let me know if you have a consistent estimate.

Credits
-------

* Major JSON revision ideas taken from pat310's JavaScript library

  - https://github.com/pat310/google-trends-api

* Connecting to google code heavily based off Stack Overflow post

  - http://stackoverflow.com/questions/6754709/logging-in-to-google-using-python

* With some ideas pulled from Matt Reid's Google Trends API

  - https://bitbucket.org/mattreid9956/google-trend-api/overview
