from pytrends.request import TrendReq

# enter your own credentials
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
trending_searches_df = pytrend.trending_searches()

# Get Google Top Charts
top_charts_df = pytrend.top_charts(cid='actors', date=201611)

# Get Google Keyword Suggestions
suggestions_dict = pytrend.suggestions(keyword='pizza')
