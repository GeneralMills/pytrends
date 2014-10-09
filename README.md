pytrends
=========

### About

**Pseudo API for Google Trends**

* Allows simple interface for automating downloads of csv reports from Google Trends.
* Main feature is to help you trick google into thinking you are pulling from a browser.


* Only good until Google changes their backend again :-P

**Requirements**
* Written for Python 3.3, probably works for 3.x.
* Requires a google account to use.

## Connect to Google
**pyGTrends(google_username, google_password)**

**Parameters**
* google_username
  - a valid gmail address
* google_password
  - password for the gmail account

### Request a Report
**request_report(keywords, hl='en-US', cat=None, geo=None, date=None, use_topic=False)**

**Parameters**
* keywords
  - the words you wish you get data for
  - Example "Pizza"
  - Alternately: "Pizza + Italian"
  - Alternately: "iron - chemical element" topic name is "%2Fm%2F025rw19" and needs use_topics=True
* hl
  - language
  - find available parameters by inspecting the url when manually using Google Trends
  - defaults to US english
* cat
  - category
  - find available parameters by inspecting the url when manually using Google Trends
  - defaults to none
* geo
  - geographical area
  - find available parameters by inspecting the url when manually using Google Trends
  - defaults to world
* date
  - date to start from
  - defaults to all available data
  - "MM/YYYY #m" where # is the number of months from that date to pull data for
  - "10/2009 61m" would get data from October 2009 to October 2014
* use_topic
  - set to true if you wish to avoid URLencoding the keywords

### Save a Report to file
**save_csv(path, trend_name)**

**Parameters**
* path
  - output path
* trend_name
  - human readable name for file

### Credits

* Connecting to google code heavily based off Sal Uryasev's pyGTrends

* With some ideas pulled from Matt Reid's Google Trends API for python 2.x
  - https://bitbucket.org/mattreid9956/google-trend-api/overview
