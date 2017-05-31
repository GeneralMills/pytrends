from __future__ import absolute_import, print_function, unicode_literals
import sys
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
from pytrends import exceptions

if sys.version_info[0] == 2:  # Python 2
    from urllib import quote
else:  # Python 3
    from urllib.parse import quote


class TrendReq(object):
    """
    Google Trends API
    """

    GET_METHOD = 'get'
    POST_METHOD = 'post'

    LOGIN_URL = 'https://accounts.google.com/ServiceLogin'
    AUTH_URL = 'https://accounts.google.com/ServiceLoginAuth'

    GENERAL_URL = 'https://www.google.com/trends/api/explore'
    INTEREST_OVER_TIME_URL = 'https://www.google.com/trends/api/widgetdata/multiline'
    INTEREST_BY_REGION_URL = 'https://www.google.com/trends/api/widgetdata/comparedgeo'
    RELATED_QUERIES_URL = 'https://www.google.com/trends/api/widgetdata/relatedsearches'
    TRENDING_SEARCHES_URL = 'https://trends.google.com/trends/hottrends/hotItems'
    TOP_CHARTS_URL = 'https://trends.google.com/trends/topcharts/chart'
    SUGGESTIONS_URL = 'https://www.google.com/trends/api/autocomplete/'

    def __init__(self, google_username, google_password, hl='en-US', tz=360, geo='', custom_useragent='PyTrends',
                 proxies=None):
        """
        Initialize hard-coded URLs, HTTP headers, and login parameters
        needed to connect to Google Trends, then connect.
        """
        self.username = google_username
        self.password = google_password
        # google rate limit
        self.google_rl = 'You have reached your quota limit. Please try again later.'
        # custom user agent so users know what "new account signin for Google" is
        self.custom_useragent = {'User-Agent': custom_useragent}
        self._connect(proxies=proxies)
        self.results = None

        # set user defined options used globally
        self.tz = tz
        self.hl = hl
        self.geo = geo
        self.kw_list = list()

        # intialize widget payloads
        self.interest_over_time_widget = dict()
        self.interest_by_region_widget = dict()
        self.related_queries_widget_list = list()

    def _connect(self, proxies=None):
        """
        Connect to Google.
        Go to login page GALX hidden input value and send it back to google + login and password.
        http://stackoverflow.com/questions/6754709/logging-in-to-google-using-python
        """
        self.ses = requests.session()
        if proxies:
            self.ses.proxies.update(proxies)
        login_html = self.ses.get(TrendReq.LOGIN_URL, headers=self.custom_useragent)
        soup_login = BeautifulSoup(login_html.content, 'lxml').find('form').find_all('input')
        form_data = dict()
        for u in soup_login:
            if u.has_attr('value') and u.has_attr('name'):
                form_data[u['name']] = u['value']
        # override the inputs with out login and pwd:
        form_data['Email'] = self.username
        form_data['Passwd'] = self.password
        self.ses.post(TrendReq.AUTH_URL, data=form_data)

    def _get_data(self, url, method=GET_METHOD, trim_chars=0, **kwargs):
        """Send a request to Google and return the JSON response as a Python object

        :param url: the url to which the request will be sent
        :param method: the HTTP method ('get' or 'post')
        :param trim_chars: how many characters should be trimmed off the beginning of the content of the response
            before this is passed to the JSON parser
        :param kwargs: any extra key arguments passed to the request builder (usually query parameters or data)
        :return:
        """
        if method == TrendReq.POST_METHOD:
            response = self.ses.post(url, **kwargs)
        else:
            response = self.ses.get(url, **kwargs)

        # check if the response contains json and throw an exception otherwise
        # Google mostly sends 'application/json' in the Content-Type header,
        # but occasionally it sends 'application/javascript
        # and sometimes even 'text/javascript
        if 'application/json' in response.headers['Content-Type'] or \
                        'application/javascript' in response.headers['Content-Type'] or \
                                        'text/javascript' in response.headers['Content-Type']:

            # trim initial characters
            # some responses start with garbage characters, like ")]}',"
            # these have to be cleaned before being passed to the json parser
            content = response.text[trim_chars:]

            # parse json
            return json.loads(content)
        else:
            # this is often the case when the amount of keywords in the payload for the IP
            # is not allowed by Google
            raise exceptions.ResponseError('The request failed: Google returned a '
                                           'response with code {0}.'.format(response.status_code), response=response)

    def build_payload(self, kw_list, cat=0, timeframe='today 5-y', geo='', gprop=''):
        """Create the payload for related queries, interest over time and interest by region"""
        self.kw_list = kw_list
        self.geo = geo
        token_payload = {
            'hl': self.hl,
            'tz': self.tz,
            'req': {'comparisonItem': [], 'category': cat},
            'property': gprop,
        }

        # build out json for each keyword
        for kw in self.kw_list:
            keyword_payload = {'keyword': kw, 'time': timeframe, 'geo': self.geo}
            token_payload['req']['comparisonItem'].append(keyword_payload)
        # requests will mangle this if it is not a string
        token_payload['req'] = json.dumps(token_payload['req'])
        # get tokens
        self._tokens(token_payload)
        return

    def _tokens(self, token_payload):
        """Makes request to Google to get API tokens for interest over time, interest by region and related queries"""

        # make the request and parse the returned json
        widget_dict = self._get_data(
            url=TrendReq.GENERAL_URL,
            method=TrendReq.GET_METHOD,
            params=token_payload,
            trim_chars=4,
        )['widgets']

        # order of the json matters...
        first_region_token = True
        # assign requests
        for widget in widget_dict:
            if widget['title'] == 'Interest over time':
                self.interest_over_time_widget = widget
            if widget['title'] == 'Interest by region' and first_region_token:
                self.interest_by_region_widget = widget
                first_region_token = False
            if widget['title'] == 'Interest by subregion' and first_region_token:
                self.interest_by_region_widget = widget
                first_region_token = False
            # response for each term, put into a list
            if widget['title'] == 'Related queries':
                self.related_queries_widget_list.append(widget)
        return

    def interest_over_time(self):
        """Request data from Google's Interest Over Time section and return a dataframe"""

        over_time_payload = {
            # convert to string as requests will mangle
            'req': json.dumps(self.interest_over_time_widget['request']),
            'token': self.interest_over_time_widget['token'],
            'tz': self.tz
        }

        # make the request and parse the returned json
        req_json = self._get_data(
            url=TrendReq.INTEREST_OVER_TIME_URL,
            method=TrendReq.GET_METHOD,
            trim_chars=5,
            params=over_time_payload,
        )

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

    def interest_by_region(self, resolution='COUNTRY'):
        """Request data from Google's Interest by Region section and return a dataframe"""

        # make the request
        region_payload = dict()
        if self.geo == '':
            self.interest_by_region_widget['request']['resolution'] = resolution
        # convert to string as requests will mangle
        region_payload['req'] = json.dumps(self.interest_by_region_widget['request'])
        region_payload['token'] = self.interest_by_region_widget['token']
        region_payload['tz'] = self.tz

        # parse returned json
        req_json = self._get_data(
            url=TrendReq.INTEREST_BY_REGION_URL,
            method=TrendReq.GET_METHOD,
            trim_chars=5,
            params=region_payload
        )
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
        """Request data from Google's Related Queries section and return a dictionary of dataframes

        If no top and/or rising related queries are found, the value for the key "top" and/or "rising" will be None
        """

        # make the request
        related_payload = dict()
        result_dict = dict()
        for request_json in self.related_queries_widget_list:
            # ensure we know which keyword we are looking at rather than relying on order
            kw = request_json['request']['restriction']['complexKeywordsRestriction']['keyword'][0]['value']
            # convert to string as requests will mangle
            related_payload['req'] = json.dumps(request_json['request'])
            related_payload['token'] = request_json['token']
            related_payload['tz'] = self.tz

            # parse the returned json
            req_json = self._get_data(
                url=TrendReq.RELATED_QUERIES_URL,
                method=TrendReq.GET_METHOD,
                trim_chars=5,
                params=related_payload,
            )

            # top queries
            try:
                top_df = pd.DataFrame(req_json['default']['rankedList'][0]['rankedKeyword'])
                top_df = top_df[['query', 'value']]
            except KeyError:
                # in case no top queries are found, the lines above will throw a KeyError
                top_df = None

            # rising queries
            try:
                rising_df = pd.DataFrame(req_json['default']['rankedList'][1]['rankedKeyword'])
                rising_df = rising_df[['query', 'value']]
            except KeyError:
                # in case no rising queries are found, the lines above will throw a KeyError
                rising_df = None

            result_dict[kw] = {'top': top_df, 'rising': rising_df}
        return result_dict

    def trending_searches(self):
        """Request data from Google's Trending Searches section and return a dataframe"""

        # make the request
        forms = {'ajax': 1, 'pn': 'p1', 'htd': '', 'htv': 'l'}
        req_json = self._get_data(
            url=TrendReq.TRENDING_SEARCHES_URL,
            method=TrendReq.POST_METHOD,
            data=forms,
        )['trendsByDateList']
        result_df = pd.DataFrame()

        # parse the returned json
        sub_df = pd.DataFrame()
        for trenddate in req_json:
            sub_df['date'] = trenddate['date']
            for trend in trenddate['trendsList']:
                sub_df = sub_df.append(trend, ignore_index=True)
        result_df = pd.concat([result_df, sub_df])
        return result_df

    def top_charts(self, date, cid, geo='US', cat=''):
        """Request data from Google's Top Charts section and return a dataframe"""

        # create the payload
        chart_payload = {'ajax': 1, 'lp': 1, 'geo': geo, 'date': date, 'cat': cat, 'cid': cid}

        # make the request and parse the returned json
        req_json = self._get_data(
            url=TrendReq.TOP_CHARTS_URL,
            method=TrendReq.POST_METHOD,
            params=chart_payload,
        )['data']['entityList']
        df = pd.DataFrame(req_json)
        return df

    def suggestions(self, keyword):
        """Request data from Google's Keyword Suggestion dropdown and return a dictionary"""

        # make the request
        kw_param = quote(keyword)
        parameters = {'hl': self.hl}

        req_json = self._get_data(
            url=TrendReq.SUGGESTIONS_URL + kw_param,
            params=parameters,
            method=TrendReq.GET_METHOD,
            trim_chars=5
        )['default']['topics']
        return req_json
