from __future__ import absolute_import, print_function, unicode_literals
import sys
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
if sys.version_info[0] == 2:  # Python 2
    from urllib import quote
else:  # Python 3
    from urllib.parse import quote


class TrendReq(object):
    """
    Google Trends API
    """
    def __init__(self, google_username, google_password, hl='en-US', tz=360, custom_useragent=None):
        """
        Initialize hard-coded URLs, HTTP headers, and login parameters
        needed to connect to Google Trends, then connect.
        """
        self.username = google_username
        self.password = google_password
        # google rate limit
        self.google_rl = 'You have reached your quota limit. Please try again later.'
        self.url_login = "https://accounts.google.com/ServiceLogin"
        self.url_auth = "https://accounts.google.com/ServiceLoginAuth"
        # custom user agent so users know what "new account signin for Google" is
        if custom_useragent is None:
            self.custom_useragent = {'User-Agent': 'PyTrends'}
        else:
            self.custom_useragent = {'User-Agent': custom_useragent}
        self._connect()
        self.results = None

        # set user defined options used globally
        self.tz = tz
        self.hl = hl
        self.kw_list = list()

        # intialize widget payloads
        self.interest_overtime_widget = dict()
        self.interest_by_region_widget = dict()
        self.related_queries_widget_list = list()

    def _connect(self):
        """
        Connect to Google.
        Go to login page GALX hidden input value and send it back to google + login and password.
        http://stackoverflow.com/questions/6754709/logging-in-to-google-using-python
        """
        self.ses = requests.session()
        login_html = self.ses.get(self.url_login, headers=self.custom_useragent)
        soup_login = BeautifulSoup(login_html.content, "lxml").find('form').find_all('input')
        form_data = dict()
        for u in soup_login:
            if u.has_attr('value') and u.has_attr('name'):
                form_data[u['name']] = u['value']
        # override the inputs with out login and pwd:
        form_data['Email'] = self.username
        form_data['Passwd'] = self.password
        self.ses.post(self.url_auth, data=form_data)

    def build_payload(self, kw_list, cat=0, timeframe='today 5-y', geo='', gprop=''):
        """Create the payload for related queries, interest over time and interest by region"""
        token_payload = dict()
        self.kw_list = kw_list
        token_payload['hl'] = self.hl
        token_payload['tz'] = self.tz
        token_payload['req'] = {'comparisonItem': [], 'category': cat}
        token_payload['property'] = gprop
        # build out json for each keyword
        for kw in self.kw_list:
            keyword_payload = {'keyword': kw, 'time': timeframe, 'geo': geo}
            token_payload['req']['comparisonItem'].append(keyword_payload)
        # requests will mangle this if it is not a string
        token_payload['req'] = json.dumps(token_payload['req'])
        # get tokens
        self._tokens(token_payload)
        return

    def _tokens(self, token_payload):
        """Makes request to Google to get API tokens for interest over time, interest by region and related queries"""

        # make the request
        req_url = "https://www.google.com/trends/api/explore"
        req = self.ses.get(req_url, params=token_payload)

        # parse the returned json
        # strip off garbage characters that break json parser
        widget_json = req.text[4:]
        widget_dict = json.loads(widget_json)['widgets']
        # order of the json matters...
        first_region_token = True
        # assign requests
        for widget in widget_dict:
            if widget['title'] == 'Interest over time':
                self.interest_over_time_widget = widget
            if widget['title'] == 'Interest by region' and first_region_token:
                self.interest_by_region_widget = widget
                first_region_token = False
            # response for each term, put into a list
            if widget['title'] == 'Related queries':
                self.related_queries_widget_list.append(widget)
        return

    def interest_over_time(self):
        """Request data from Google's Interest Over Time section and return a dataframe"""

        # make the request
        req_url = "https://www.google.com/trends/api/widgetdata/multiline"
        over_time_payload = dict()
        # convert to string as requests will mangle
        over_time_payload['req'] = json.dumps(self.interest_over_time_widget['request'])
        over_time_payload['token'] = self.interest_over_time_widget['token']
        over_time_payload['tz'] = self.tz
        req = self.ses.get(req_url, params=over_time_payload)

        # parse the returned json
        # strip off garbage characters that break json parser
        req_json = json.loads(req.text[5:])
        df = pd.DataFrame(req_json['default']['timelineData'])
        df['date'] = pd.to_datetime(df['time'], unit='s')
        df = df.set_index(['date']).sort_index()
        # split list columns into seperate ones, remove brackets and split on comma
        result_df = df['value'].apply(lambda x: pd.Series(str(x).replace('[', '').replace(']', '').split(',')))
        # rename each column with its search term, relying on order that google provides...
        for idx, kw in enumerate(self.kw_list):
            result_df[kw] = result_df[idx].astype('int')
            del result_df[idx]
        return result_df

    def interest_by_region(self, resolution='CITY'):
        """Request data from Google's Interest by Region section and return a dataframe"""

        # make the request
        req_url = "https://www.google.com/trends/api/widgetdata/comparedgeo"
        region_payload = dict()
        self.interest_by_region_widget['request']['resolution'] = resolution
        # convert to string as requests will mangle
        region_payload['req'] = json.dumps(self.interest_by_region_widget['request'])
        region_payload['token'] = self.interest_by_region_widget['token']
        region_payload['tz'] = self.tz
        req = self.ses.get(req_url, params=region_payload)

        # parse returned json
        # strip off garbage characters that break json parser
        req_json = json.loads(req.text[5:])
        df = pd.DataFrame(req_json['default']['geoMapData'])
        # rename the column with the search keyword
        df = df[['geoName', 'value']].set_index(['geoName']).sort_index()
        # split list columns into seperate ones, remove brackets and split on comma
        result_df = df['value'].apply(lambda x: pd.Series(str(x).replace('[', '').replace(']', '').split(',')))
        # rename each column with its search term
        for idx, kw in enumerate(self.kw_list):
            result_df[kw] = result_df[idx].astype('int')
            del result_df[idx]
        return result_df

    def related_queries(self):
        """Request data from Google's Related Queries section and return a dictionary of dataframes"""

        # make the request
        req_url = "https://www.google.com/trends/api/widgetdata/relatedsearches"
        related_payload = dict()
        result_dict = dict()
        for request_json in self.related_queries_widget_list:
            # ensure we know which keyword we are looking at rather than relying on order
            kw = request_json['request']['restriction']['complexKeywordsRestriction']['keyword'][0]['value']
            # convert to string as requests will mangle
            related_payload['req'] = json.dumps(request_json['request'])
            related_payload['token'] = request_json['token']
            related_payload['tz'] = self.tz
            req = self.ses.get(req_url, params=related_payload)

            # parse the returned json
            # strip off garbage characters that break json parser
            req_json = json.loads(req.text[5:])
            # top queries
            top_df = pd.DataFrame(req_json['default']['rankedList'][0]['rankedKeyword'])
            top_df = top_df[['query', 'value']]
            # rising queries
            rising_df = pd.DataFrame(req_json['default']['rankedList'][1]['rankedKeyword'])
            rising_df = rising_df[['query', 'value']]
            result_dict[kw] = {'top': top_df, 'rising': rising_df}
        return result_dict

    def trending_searches(self):
        """Request data from Google's Trending Searches section and return a dataframe"""

        # make the request
        req_url = "https://www.google.com/trends/hottrends/hotItems"
        forms = {'ajax': 1, 'pn': 'p1', 'htd': '', 'htv': 'l'}
        req = self.ses.post(req_url, data=forms)
        req_json = json.loads(req.text)['trendsByDateList']
        result_df = pd.DataFrame()

        # parse the returned json
        for trenddate in req_json:
            sub_df = pd.DataFrame()
            sub_df['date'] = trenddate['date']
            for trend in trenddate['trendsList']:
                sub_df = sub_df.append(trend, ignore_index=True)
        result_df = pd.concat([result_df, sub_df])
        return result_df

    def top_charts(self, date, cid, geo='US', cat=''):
        """Request data from Google's Top Charts section and return a dataframe"""

        # make the request
        # create the payload
        chart_payload = {'ajax': 1, 'lp': 1}
        chart_payload['geo'] = geo
        chart_payload['date'] = date
        chart_payload['cat'] = cat
        chart_payload['cid'] = cid
        req_url = "https://www.google.com/trends/topcharts/chart"
        req = self.ses.post(req_url, params=chart_payload)

        # parse the returned json
        print(req.text)
        req_json = json.loads(req.text)['data']['entityList']
        df = pd.DataFrame(req_json)
        return df

    def suggestions(self, keyword):
        """Request data from Google's Keyword Suggestion dropdown and return a dictionary"""

        # make the request
        kw_param = quote(keyword)
        req = self.ses.get("https://www.google.com/trends/api/autocomplete/" + kw_param)

        # parse the returned json
        # response is invalid json but if you strip off ")]}'," from the front it is then valid
        req_json = json.loads(req.text[5:])['default']['topics']
        return req_json
