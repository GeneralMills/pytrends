from pytrends.request import trendReq

google_username = "XXX@gmail.com"
google_password = "XXXX"
path = ""

# connect to Google
custom_useragent = {'User-Agent': 'My Pytrends Script'}
pytrend = trendReq(google_username, google_password, custom_useragent)

trend_payload = {'q': ['Pizza, Italian, Spaghetti, Breadsticks, Sausage'], 'cat': '0-71'}
# trend
pytrend.trend(trend_payload)
print(pytrend.get_json())

# # toprelated
# toprelated = pytrends.toprelated(trend_payload).get_json()
#
# # top30in30
# top30in30 = pytrends.top30in30().get_json()
#
# country_payload = {'geo': 'US'}
# # hottrends
# hottrends = pytrends.hottrends(country_payload).get_json()
#
# # hottrendsdetail
# hottrendsdetail = pytrends.hottrendsdetail(country_payload).get_json()
#
# chart_form = {'date': '201601', 'geo': 'US'}
# # alltopcharts
# alltopcharts = pytrends.topcharts(chart_form).get_json()
#
# keyword = 'pizza'
# # suggestions
# suggestions = pytrends.suggestions(keyword).get_json()