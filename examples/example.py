from pytrends.request import trendReq

google_username = "xxx@gmail.com"
google_password = "xxx"
path = ""

# connect to Google
custom_useragent = {'User-Agent': 'My Pytrends Script'}
pytrend = trendReq(google_username, google_password, custom_useragent)

trend_payload = {'q': ['Pizza, Italian, Spaghetti, Breadsticks, Sausage'], 'cat': '0-71'}
# trend
pytrend.trend(trend_payload)
print(pytrend.get_json())

# toprelated
toprelated = pytrend.toprelated(trend_payload)
print(pytrend.get_json())

# top30in30
top30in30 = pytrend.top30in30()
print(pytrend.get_json())

country_payload = {'geo': 'US'}
# hottrends
hottrends = pytrend.hottrends(country_payload)
print(pytrend.get_json())

# hottrendsdetail
hottrendsdetail = pytrend.hottrendsdetail(country_payload)
print(pytrend.get_json())

# chart_form = {'date': '201601', 'geo': 'US'}
# # alltopcharts
# alltopcharts = pytrend.topcharts(chart_form)
# print(pytrend.get_json())
#
keyword = 'pizza'
# suggestions
suggestions = pytrend.suggestions(keyword)
print(pytrend.get_json())
