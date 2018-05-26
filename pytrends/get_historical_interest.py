import pandas as pd 
from datetime import datetime, timedelta
import time
from pytrends.request import TrendReq

def get_historical_interest(TrendReq, keywords, year_start=2017, month_start=1, day_start=1, hour_start=0, year_end=2018, month_end=1, day_end=1, hour_end= 0, cat=0, geo='', gprop='', sleep=0):
    """Gets historical hourly data for method of choice by chunking requests to 1 week at a time (which is what Google allows)"""

    # construct datetime obejcts - raises ValueError if invalid parameters       
    start_date = datetime(year_start, month_start, day_start, hour_start)
    end_date = datetime(year_end, month_end, day_end, hour_end)

    # the timeframe has to be in 1 week intervals or Google will reject it 
    delta = timedelta(days=7)

    df = pd.DataFrame()

    date_iterator = start_date
    date_iterator += delta 

    while True:
        if (date_iterator > end_date):
            # has retrieved all of the data 
            break

        # format date to comply with API call 
        start_date_str = start_date.strftime('%Y-%m-%dT%H')
        date_iterator_str = date_iterator.strftime('%Y-%m-%dT%H')
        tf = start_date_str + ' ' + date_iterator_str

        try: 
            TrendReq.build_payload(keywords,cat, tf, geo, gprop)
            week_df = TrendReq.interest_over_time()
            df = df.append(week_df)
        except Exception as e:
        	print(e)
        	pass

    	start_date += delta
    	date_iterator += delta 

        # just in case you are rate-limited by Google. Recommended is 60 if you are. 
        if sleep > 0:
            time.sleep(sleep)

    return df 

pytrends = TrendReq()

historical = get_historical_interest(pytrends, ['Bitcoin'], 2018,3,1,0,2018,5,1,0)
print(historical)