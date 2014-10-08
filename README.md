PyGTrends
=========

### About

Pseudo API for Google Trends 

Written for Python 3.3

Heavily based off Matt Reid's Google Trends API

https://bitbucket.org/mattreid9956/google-trend-api/overview

Which is in turn based off of Sal Uryasev's pyGTrends.

This program allows you to load a csv file with a list of terms to download csv's for.

### Input

**Csv requires three columns**

**Trend_Name**

* human readable, short name to use for naming the resulting file)
  
**Topic_Flag**

* enables use of google's proprietary topic id which are already URLencoded
  
* Example: "iron - chemical element" topic shows up as "%2Fm%2F025rw19" as the q= parameter in the URL if you do it manually.
  
**API_Query**

* keywords to search or topic id
