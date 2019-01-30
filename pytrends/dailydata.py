# Split up search requests to get daily Google Trend data
# Important: data needs to be rescaled due to the way the index is generated
from datetime import datetime, timedelta, date
from pytrends.request import TrendReq
import pandas as pd


# The maximum for a timeframe for which we get daily data is 270.
# Therefore we could go back 269 days. However, since there might
# be issues when rescaling, e.g. zero entries, we should have an
# overlap that does not consist of only one period. Therefore,
# I limit the step size to 250. This leaves 19 periods for overlap.
def get_historical_daily_interest(kw_list, start_date, end_date=None,
                                  verbose=False):
    # Check if kw_list is an actual list, even if only 1 word
    if not isinstance(kw_list, list):
        raise ValueError('kw_list must be a list containing at least one word')
    # Check if start and end date are of the datetime.datetime.date class
    if not isinstance(start_date, date):
        raise ValueError(
            'start_date is not an instance of datetime.date class')
    if end_date is None:
        end_date = datetime.today().date()
    else:
        if not isinstance(end_date, date):
            raise ValueError(
                'end_date is not an instance of datetime.date class')
    if end_date <= start_date:
        raise ValueError('end_date comes before start_date')

    maxstep = 269
    overlap = 40
    step = maxstep - overlap + 1

    # Login to Google. Only need to run this once, the rest of requests
    # will use the same session.
    pytrend = TrendReq()

    # Run the first time
    old_date = end_date

    # Go back in time
    new_date = old_date - timedelta(days=step)

    # Create new timeframe for which we download data
    timeframe = new_date.strftime('%Y-%m-%d')+' '+old_date.strftime('%Y-%m-%d')
    pytrend.build_payload(kw_list=kw_list, timeframe=timeframe)
    interest_over_time_df = pytrend.interest_over_time()

    # RUN ITERATIONS

    while new_date > start_date:

        # Save the new date from the previous iteration.
        # Overlap == 1 would mean that we start where we
        # stopped on the iteration before, which gives us
        # indeed overlap == 1.
        old_date = new_date + timedelta(days=overlap-1)

        # Update the new date to take a step into the past
        # Since the timeframe that we can apply for daily data
        # is limited, we use step = maxstep - overlap instead of
        # maxstep.
        new_date = new_date - timedelta(days=step)
        # If we went past our start_date, use it instead
        if new_date < start_date:
            new_date = start_date

        # New timeframe
        timeframe = new_date.strftime(
            '%Y-%m-%d')+' '+old_date.strftime('%Y-%m-%d')
        if verbose:
            print(timeframe)

        # Download data
        pytrend.build_payload(kw_list=kw_list, timeframe=timeframe)
        temp_df = pytrend.interest_over_time()
        if (temp_df.empty):
            raise ValueError(
                'Google sent back an empty dataframe. Possibly there were'
                ' no searches at all during the this period! Set start_date'
                ' to a later date.')
        # Renormalize the dataset and drop last line
        for kw in kw_list:
            beg = new_date
            end = old_date - timedelta(days=1)

            # Since we might encounter zeros, we loop over the
            # overlap until we find a non-zero element
            for t in range(1, overlap+1):
                if temp_df[kw].iloc[-t] != 0:
                    scaling = interest_over_time_df[kw].iloc[t-1] / \
                        temp_df[kw].iloc[-t]
                    break
                elif t == overlap:
                    print(
                        'Did not find non-zero overlap, set scaling to zero!'
                        ' Increase Overlap!')
                    scaling = 0
            # Apply scaling
            temp_df.loc[beg:end, kw] = temp_df.loc[beg:end, kw]*scaling
        interest_over_time_df = pd.concat(
            [temp_df[:-overlap], interest_over_time_df])

    # Save dataset
    return interest_over_time_df
