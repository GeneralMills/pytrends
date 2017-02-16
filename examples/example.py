import pytrends

# Create payload and capture API tokens. Only needed for interest_over_time(), interest_by_region() & related_queries()
req = pytrends.TrendReq(kw_list=['pizza', 'bagel'])

# Interest Over Time
interest_over_time_df = req.interest_over_time()

# Interest by Region
interest_by_region_df = req.interest_by_region()

# Related Queries, returns a dictionary of dataframes
related_queries_dict = req.related_queries()

# These functions allow you to pull curated trands as maintained by Google

# Get Google Hot Trends data
trending_searches_df = pytrends.trending_searches()

# Get Google Top Charts
top_charts_df = pytrends.top_charts(cid='actors', date=201611)

# Get Google Keyword Suggestions
suggestions_dict = pytrends.suggestions(keyword='pizza')
