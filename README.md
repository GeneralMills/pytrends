pytrends
========

Introduction
------------

Unofficial API for Google Trends

Allows simple interface for automating downloading of reports from Google Trends. Main feature is to allow the script to login to Google on your behalf to enable a higher rate limit. Only good until Google changes their backend again :-P. When that happens feel free to contribute!


Table of contens
----------------

* [Installation](#installation)

* [API](#api)

  * [API Methods](#api-methods)

  * [API Payload Keys](#api-payload-keys)

    * [trend](#trend)
    * [related](#related)
    * [top30in30](#top30in30)
    * [hottrends](#hottrends)
    * [hottrendsdetail](#hottrendsdetail)
    * [topcharts](#topcharts)
    * [suggestions](#suggestions)

  * [Caveats](#caveats)

* [Credits](#credits)
	
<hr>

Installation
------------

::

    pip install pytrends

Requirements

* Written for both Python 2.7+ and Python 3.3+
* Requires a google account to use.
* Requires BeautifulSoup4, Requests, lxml, Pandas

[back to top](#introduction)

<hr>

API
---

Connect to Google
^^^^^^^^^^^^^^^^^

::

    pytrends = TrendReq(google_username, google_password, custom_useragent=None)

Parameters

* username

  - *Required*
  - a valid gmail address

* password

  - *Required*
  - password for the gmail account

* custom_useragent

  - name to identify requests coming from your script

[back to top](#API)

<hr>

API Methods
^^^^^^^^^^^

The following API methods are available:

* [trend](#trend): returns the historical trend data to a provided keyword or an array of keywords.

* [related](#related): returns the related keywords to a provided keyword or an array of keywords along with it's percentage of correlation.

* [hottrends](#hottrends): returns the current top 20 trending searches for a given location.

* [hottrendsdetail](#hottrendsdetail): same as the [hotTrends](#hottrends) results except with more detail such as links, publication date, approximate traffic, etc.

* [top30in30](#top30in30): returns the top 30 searches in the past 30 days

* [topcharts](#topcharts): returns the trending charts for a given date and location.  Charts contain information such as title, description, source, a jumpFactory, etc.

* [suggestions](#suggestions): returns a list of additional suggested keywords that can be used to refine a trend search

[back to top](#api-methods)

<hr>

API Payload Keys
^^^^^^^^^^^^^^^^

Many API methods use `payload` here is a set of known keys that can be used.

* `q`

  - keywords to get data for
  - Example ```{'q': 'Pizza'}```
  - Up to five terms in a comma seperated string: ```{'q': 'Pizza, Italian, Spaghetti, Breadsticks, Sausage'}```

    * Advanced Keywords

      - When using Google Trends dashboard Google may provide suggested narrowed search terms. 
      - For example ```"iron"``` will have a drop down of ```"Iron Chemical Element, Iron Cross, Iron Man, etc"```. 
      - Find the encoded topic by using the get_suggestions() function and choose the most relevant one for you. 
      - For example: ```https://www.google.com/trends/explore#q=%2Fm%2F025rw19&cmpt=q```
      - ```"%2Fm%2F025rw19"``` is the topic "Iron Chemical Element" to use this with pytrends

* `hl`

  - Language to return result headers in
  - Two letter language abbreviation
  - For example US English is ```{'hl': 'en-US'}```
  - Defaults to US english

* `cat`

  - Category to narrow results
  - Find available cateogies by inspecting the url when manually using Google Trends. The category starts after ```cat=``` and ends before the next ```&```
  - For example: ```"https://www.google.com/trends/explore#q=pizza&cat=0-71"```
  - ```{'cat': '0-71'}``` is the category
  - Defaults to no category

* `geo`

  - Two letter country abbreviation
  - For example United States is ```{'geo': 'US'```
  - Defaults to World
  - More detail available for States/Provinces by specifying additonal abbreviations
  - For example: Alabama would be ```{'geo': 'US-AL'}```
  - For example: England would be ```{'geo': 'GB-ENG'}```

* `tz`

  - Timezone using Etc/GMT
  - For example US CST is ```{'tz': 'Etc/GMT+5'}```

* `date`

  - Date to start from
  - Defaults to all available data, 2004 - present.
  - Custom Timeframe Pattern:

    - By Month: ```{'date': 'MM/YYYY #m'}``` where # is the number of months from that date to pull data for

      - For example: ``{'date': '10/2009 61m'}`` would get data from October 2009 to October 2014
      - Less than 4 months will return Daily level data
      - More than 36 months will return monthly level data
      - 4-36 months will return weekly level data

  - Current Time Minus Time Pattern:

    - By Month: ```{'date': 'today #-m'}``` where # is the number of months from that date to pull data for

      - For example: ``{'date': 'today 61-m'}`` would get data from today to 61months ago
      - 1-3 months will return daily intervals of data
      - 4-36 months will return weekly intervals of data
      - 36+ months will return monthly intervals of data
      - **NOTE** Google uses UTC date as *'today'*

    - Daily: ```{'date': 'today #-d'}``` where # is the number of days from that date to pull data for

      - For example: ``{'date': 'today 7-d'}`` would get data from the last week
      - 1 day will return 8min intervals of data
      - 2-8 days will return Hourly intervals of data
      - 8-90 days will return Daily level data

    - Hourly: ```{'date': 'now #-H'}``` where # is the number of hours from that date to pull data for

      - For example: ``{'date': 'now 1-H'}`` would get data from the last hour
      - 1-3 hours will return 1min intervals of data
      - 4-26 hours will return 8min intervals of data
      - 27-34 hours will return 16min intervals of data

* `gprop`

  - What search data we want
  - Example ```{'gprop': 'images'}```
  - Defaults to web searches
  - Can be ```images```, ```news```, ```youtube``` or ```froogle``` (for Google Shopping results)

[back to top](#api-payload-keys)

<hr>

trend
^^^^^

::

    pytrends.trend(payload, return_type=None)

Parameters

* `payload`

  - *Required*
  - a dictionary of key, values

* `return_type`

  - 'dataframe' returns a Pandas Dataframe
  - 'json' returns json
  
Returns JSON or Dataframe

[back to top](#trend)

<hr>

related
^^^^^^^

::

    pytrends.related(payload)

Parameters

* `payload`

  - *Required*
  - a dictionary of key, values

* `related_type`

  - *Required*
  - 'top' returns top related data
  - 'rising' returns rising related data
  
Returns JSON

[back to top](#related)

<hr>

top30in30
^^^^^^^^^

::

    pytrends.top30in30()

Returns JSON

[back to top](#top30in30)

<hr>

hottrends
^^^^^^^^^

::

    pytrends.hottrends(payload)

Parameters

* `payload`

  - *Required*
  - a dictionary of key, values

Returns JSON

[back to top](#hottrends)

<hr>

hottrendsdetail
^^^^^^^^^^^^^^^

::

    pytrends.hottrendsdetail(payload)

Parameters

* `payload`

  - *Required*
  - a dictionary of key, values
  
Returns XML RSS Feed

[back to top](#hottrendsdetail)

<hr>

topcharts
^^^^^^^^^

::

    pytrends.topcharts(payload)

Parameters

* `payload`

  - *Required*
  - a dictionary of key, values

Returns JSON

[back to top](#topcharts)

<hr>

suggestions
^^^^^^^^^^^

::

    pytrends.suggestions(keyword)

Parameters

* `keyword`

  - *Required*
  - keyword to get suggestions for
  
Returns JSON

[back to top](#suggestions)

Caveats
-------

* This is not an official or supported API
* Google may change aggregation level for items with very large or very small search volume
* Google will send you an email saying that you had a new login after running this.
* Rate Limit is not pubically known, trail and error suggest it is around 10/min

Credits
-------

* Major JSON revision ideas taken from pat310's JavaScript library

  - https://github.com/pat310/google-trends-api

* Connecting to google code heavily based off Stack Overflow post

  - http://stackoverflow.com/questions/6754709/logging-in-to-google-using-python

* With some ideas pulled from Matt Reid's Google Trends API

  - https://bitbucket.org/mattreid9956/google-trend-api/overview
