pytrends
=========

### About

**Pseudo API for Google Trends**

* Allows simple interface for automating downloads of csv reports from Google Trends.
* Main feature is to help trick google into thinking the script is actually a browser.


* Only good until Google changes their backend again :-P

**Installation**

```pip install pytrends```

**Requirements**
* Written for both Python 2.7+ and Python 3.3+
* Requires a google account to use.
* Requires fake-useragent python library (installed automatically with pip)

**Caveats**
* This is not an official or supported API
* Google may change aggregation level for items with very large or very small search volume

## Connect to Google
**pyGTrends(google_username, google_password)**

**Parameters**
* google_username
  - a valid gmail address
* google_password
  - password for the gmail account

### Request a Report
**request_report(keywords, hl='en-US', cat=None, geo=None, date=None, gprop=None)**

**Parameters**
* Keywords
  - the words to get data for
  - Example ```"Pizza"```
  - Up to five terms with a comma and space: ```"Pizza, Italian, Spaghetti, Breadsticks, Sausage"```
* Advanced Keywords
  - When using Google Trends dashboard Google may provide suggested narrowed search terms. 
  - For example ```"iron"``` will have a drop down of ```"Iron Chemical Element, Iron Cross, Iron Man, etc"```. 
  - Find the encoded topic by using the get_suggestions() function and choose the most relevant one for you. 
  - For example: ```https://www.google.com/trends/explore#q=%2Fm%2F025rw19&cmpt=q```
  - ```"%2Fm%2F025rw19"``` is the topic "Iron Chemical Element" to use this with pytrends
* hl
  - Language to return result headers in
  - Two letter language abbreviation
  - For example English is ```"en"```
  - Defaults to english
* cat
  - Category to narrow results
  - Find available cateogies by inspecting the url when manually using Google Trends. The category starts after ```cat=``` and ends before the next ```&```
  - For example: ```"https://www.google.com/trends/explore#q=pizza&cat=0-71"```
  - ```"0-71"``` is the category
  - Defaults to no category
* geo
  - Two letter country abbreviation
  - For example United States is ```"US"```
  - Defaults to World
  - More detail available for States/Provinces by specifying additonal abbreviations
  - For example: Alabama would be ```US-AL```
  - For example: England would be ```GB-ENG```
* tz
  - Timezone using Etc/GMT
  - For example US CST is ```"Etc/GMT+5"```
* date
  - Date to start from
  - Defaults to all available data, 2004 - present.
  - Custom Timeframe Pattern:
    - By Month: ```"MM/YYYY #m"``` where # is the number of months from that date to pull data for
      - For example: ``"10/2009 61m"`` would get data from October 2009 to October 2014
      - Less than 4 months will return Daily level data
      - More than 36 months will return monthly level data
      - 4-36 months will return weekly level data
  - Current Time Minus Time Pattern:
    - By Month: ```"today #-m"``` where # is the number of months from that date to pull data for
      - For example: ``"today 61-m"`` would get data from today to 61months ago
      - 1-3 months will return daily intervals of data
      - 4-36 months will return weekly intervals of data
      - 36+ months will return monthly intervals of data
      - **NOTE** Google uses UTC date as *'today'*
    - Daily: ```"today #-d"``` where # is the number of days from that date to pull data for
      - For example: ``"today 7-d"`` would get data from the last week
      - 1 day will return 8min intervals of data
      - 2-8 days will return Hourly intervals of data
      - 8-90 days will return Daily level data
    - Hourly: ```"now #-H"``` where # is the number of hours from that date to pull data for
      - For example: ``"now 1-H"`` would get data from the last hour
      - 1-3 hours will return 1min intervals of data
      - 4-26 hours will return 8min intervals of data
      - 27-34 hours will return 16min intervals of data
* gprop
  - What search data we want
  - Defaults to web searches
  - Can be ```images```, ```news```, ```youtube``` or ```froogle``` (for Google Shopping results)

### Save a Report to file
**save_csv(path, trend_name)**

**Parameters**
* path
  - Output path
* trend_name
  - Human readable name for file

### Get Google Term Suggestions
**get_suggestions(keyword)**

**Parameters**
* keyword
  - keyword to get suggestions for
  
**Returns JSON**
```{"default": {"topics": [{"mid": "/m/0663v","title": "Pizza","type": "Dish"}]}}```
* Use the ```mid``` value for the keyword in future searches for a more refined trend set
### Credits

* Connecting to google code heavily based off Sal Uryasev's pyGTrends

* With some ideas pulled from Matt Reid's Google Trends API
  - https://bitbucket.org/mattreid9956/google-trend-api/overview
