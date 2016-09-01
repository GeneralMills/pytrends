from pytrends.pyGTrends import pyGTrends

# create pytrend object
pytrends = pyGTrends()

trend_payload = {'q': ['Pizza, Italian, Spaghetti, Breadsticks, Sausage'], 'cat': '0-71'}
# trend
trend = pytrends.trend(trend_payload)

# toprelated
toprelated = pytrends.toprelated(trend_payload)

# top30in30
top30in30 = pytrends.top30in30()

country_payload = {'geo': 'US'}
# hottrends
hottrends = pytrends.hottrends(country_payload)

# hottrendsdetail
hottrendsdetail = pytrends.hottrendsdetail(country_payload)

chart_form = {'date': '201601', 'geo': 'US'}
# alltopcharts
alltopcharts = pytrends.topcharts(chart_form)

keyword = 'pizza'
# suggestions
suggestions = pytrends.suggestions(keyword)