pytrends
=========

### About

**Pseudo API for Google Trends**

* Allows simple interface to automating downloads of csv reports from Google Trends.

* Main feature is to help you trick google into thinking you are pulling from a browser.

### Credits

* Heavily based off Sal Uryasev's pyGTrends

* With some ideas pulled from Matt Reid's Google Trends API for python 2.x
  - https://bitbucket.org/mattreid9956/google-trend-api/overview

**Requirements**
* Written for Python 3.3
* Requires a google account to use.

### Request a Report

**Parameters**
* keywords
  - the words you wish you get data for
* hl
  - language
  - find available parameters by inspecting the url when manually using Google Trends
* cat
  - category
  - find available parameters by inspecting the url when manually using Google Trends
* geo
  - geographical area
  - find available parameters by inspecting the url when manually using Google Trends
* date
  - date to start from
  - "MM/YYYY #m" where # is the number of months from that date to pull data for
  - "10/2009 61m" would get data from October 2009 to October 2014
* use_topic
  - set to true if you wish to avoid URLencoding the keywords

### Save a Report to file
**Parameters**
* path
  - output path
* trend_name
  - human readable name for file

### Building a Google Trends URL
**Google Trends URL**
* http://www.google.com/trends/trendsReport?hl=en-US&q=pizza&cmpt=q&content=1&export=1

**Available Parameters**
* hl
  - Language
  - defaults to english
* cat
  - category
  - not used by default
* q
  - keyword(s)
  - Example "Pizza"
  - Alternately: "Pizza + Italian"
  - Alternately: "iron - chemical element" topic name is "%2Fm%2F025rw19" and needs use_topics=True
* geo
  - geographic area
  - defaults to world
* date
  - date 
  - not used by default
  - format is starting date: "MM/YYYY #m" where # is the number of months
  - "10/2009 61m" would get data from October 2009 to October 2014

