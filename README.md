PyGTrends
=========

### About

**Pseudo API for Google Trends**

Written for Python 3.3, requires a google account to use.

Heavily based off Matt Reid's Google Trends API

https://bitbucket.org/mattreid9956/google-trend-api/overview

Which is in turn based off of Sal Uryasev's pyGTrends.

This program allows you to load a csv file with a list of terms to download csv's for.

### Defaults
* Geo defaults to US
* Language defaults to US English
* Category defaults to Food and Drink
* Date defaults to 5yrs ago to today

### Input

**Csv requires three columns**

**Trend_Name**

* human readable, short name to use for naming the resulting file)
  
**Topic_Flag**

* enables use of google's proprietary topic id which are already URLencoded
  
* Example: "iron - chemical element" topic shows up as "%2Fm%2F025rw19" as the q= parameter in the URL if you do it manually.
  
**API_Query**

* keywords to search or topic id

### Building a URL

**Google Trends URL**
* http://www.google.com/trends/trendsReport?hl=en-US&cat=0-71&q=einkorn&geo=US&date=10%2F2011%2037m&cmpt=q&content=1&export=1

**Parameters**
* hl : Language
* cat: category
* q: keyword(s)
* geo: geographic area
* date: format is starting date: "MM/YYYY #m" where # is the number of months.
* cmpt: default is q
* content: default is 1
* export: default is 1

