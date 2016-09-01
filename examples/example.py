from pytrends.pyGTrends import pyGTrends

# create pytrend object
pytrends = pyGTrends()

trend_payload = {'q': ['Pizza, Italian, Spaghetti, Breadsticks, Sausage'], 'cat': '0-71'}
# trend
trend = pytrends.trend(trend_payload).get_json()

# toprelated
toprelated = pytrends.toprelated(trend_payload).get_json()

# top30in30
top30in30 = pytrends.top30in30().get_json()

country_payload = {'geo': 'US'}
# hottrends
hottrends = pytrends.hottrends(country_payload).get_json()

# hottrendsdetail
hottrendsdetail = pytrends.hottrendsdetail(country_payload).get_json()

chart_form = {'date': '201601', 'geo': 'US'}
# alltopcharts
alltopcharts = pytrends.topcharts(chart_form).get_json()

keyword = 'pizza'
# suggestions
suggestions = pytrends.suggestions(keyword).get_json()