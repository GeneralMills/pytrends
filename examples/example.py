from pytrends.request import TrendReq

google_username = "xxx@gmail.com"
google_password = "xxx"
path = ""

# connect to Google
custom_useragent = {'User-Agent': 'My Pytrends Script'}
pytrend = TrendReq(google_username, google_password, custom_useragent)

trend_payload = {'q': ['Pizza, Italian, Spaghetti, Breadsticks, Sausage'], 'cat': '0-71'}
# trend
trend = pytrend.trend(trend_payload)
print(trend)
df = pytrend.trend(trend_payload, return_type='dataframe')
print(df)

# toprelated
toprelated = pytrend.toprelated(trend_payload)

# top30in30
top30in30 = pytrend.top30in30()

country_payload = {'geo': 'US'}
# hottrends
hottrends = pytrend.hottrends(country_payload)

# hottrendsdetail
# returns XML data
hottrendsdetail = pytrend.hottrendsdetail(country_payload)

chart_form = {'date': '201601', 'geo': 'US'}
# alltopcharts
alltopcharts = pytrend.topcharts(chart_form)

keyword = 'pizza'
# suggestions
suggestions = pytrend.suggestions(keyword)

