from pytrends.request import TrendReq

google_username = "xxx@gmail.com"
google_password = "xxx"
path = ""

# Login to Google. Only need to run this once, the rest of requests will use the same session.
pytrend = TrendReq(google_username, google_password, custom_useragent='My Pytrends Script')

# Create payload and capture API tokens. Only needed for interest_over_time(), interest_by_region() & related_queries()
pytrend.build_payload(kw_list=['pizza', 'bagel'])

# Interest Over Time
interest_over_time_df = pytrend.interest_over_time()

# Interest by Region
interest_by_region_df = pytrend.interest_by_region()

# Related Queries, returns a dictionary of dataframes
related_queries_dict = pytrend.related_queries()

# Get Google Hot Trends data
hot_trends_df = pytrend.hot_trends()

# Get Google Top Charts
top_chart_df = pytrend.top_charts(cid='athletes', date=201611)

# Get Google Keyword Suggestions
suggestions = pytrend.suggestions(keyword='pizza')
