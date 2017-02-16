import pytrends

# Login to Google. Only need to run this once, the rest of requests will use the same session.
req = pytrends.TrendReq()

# Create payload and capture API tokens. Only needed for interest_over_time(), interest_by_region() & related_queries()
req.build_payload(kw_list=['pizza', 'bagel'], geo='IN')

# Interest Over Time
interest_over_time_df = req.interest_over_time()
print(interest_over_time_df.head(1))

# Interest by Region

interest_by_region_df = req.interest_by_region()
print(interest_by_region_df.head(1))

# Related Queries, returns a dictionary of dataframes
related_queries_dict = req.related_queries()
print(related_queries_dict)

# Get Google Hot Trends data
trending_searches_df = pytrends.trending_searches()
print(trending_searches_df.head(1))

# Get Google Top Charts
top_charts_df = pytrends.top_charts(cid='actors', date=201611)
print(top_charts_df.head(1))

# Get Google Keyword Suggestions
suggestions_dict = pytrends.suggestions(keyword='pizza')
print(suggestions_dict)