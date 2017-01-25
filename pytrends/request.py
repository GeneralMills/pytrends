from __future__ import absolute_import, print_function, unicode_literals
import sys
import requests
import json
import re
import pandas as pd
from bs4 import BeautifulSoup
if sys.version_info[0] == 2:  # Python 2
    from urllib import quote_plus, quote
else:  # Python 3
    from urllib.parse import quote_plus, quote


class TrendReq(object):
    """
    Google Trends API
    """
    def __init__(self, username, password, custom_useragent=None):
        """
        Initialize hard-coded URLs, HTTP headers, and login parameters
        needed to connect to Google Trends, then connect.
        """
        self.username = username
        self.password = password
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

        # intialize user defined payload
        self.payload = dict()

        # intialize widget payloads
        self.interest_overtime_widget = dict()
        self.interest_by_region_widget = dict()
        self.related_queries_widget = dict()

    def _connect(self):
        """
        Connect to Google.
        Go to login page GALX hidden input value and send it back to google + login and password.
        http://stackoverflow.com/questions/6754709/logging-in-to-google-using-python
        """
        self.ses = requests.session()
        login_html = self.ses.get(self.url_login, headers=self.custom_useragent)
        soup_login = BeautifulSoup(login_html.content, "lxml").find('form').find_all('input')
        dico = {}
        for u in soup_login:
            if u.has_attr('value') and u.has_attr('name'):
                dico[u['name']] = u['value']
        # override the inputs with out login and pwd:
        dico['Email'] = self.username
        dico['Passwd'] = self.password
        self.ses.post(self.url_auth, data=dico)

    def _build_payload(self, payload):
        self.payload = payload
        # TODO set default values, and check if new ones added
        token_payload = dict()
        token_payload['hl'] = self.payload['hl']
        token_payload['tz'] = payload['tz']
        token_payload['property'] = payload['property']
        token_payload['req'] = {'comparisonItem': [], 'category': payload['cat']}
        kw_list = payload['kw_list']
        kw_time = payload['timeframe']
        geo = payload['geo']
        for kw in kw_list:
            keyword_payload = {'keyword': kw, 'time': kw_time, 'geo': geo}
            token_payload['req']['comparisonItem'].append(keyword_payload)

        # requests will mangle this if it is not a string
        token_payload['req'] = json.dumps(token_payload['req'])
        self.token_payload = token_payload
        return

    def tokens(self, payload):
        self._build_payload(payload)
        req_url = "https://www.google.com/trends/api/explore"
        req = self.ses.get(req_url, params=self.token_payload)
        # strip off garbage characters that break json parser
        widget_json = req.text[4:]
        widget_dict = json.loads(widget_json)['widgets']
        # assign requests
        for widget in widget_dict:
            if widget['title'] == 'Interest over time':
                self.interest_overtime_widget = widget
            if widget['title'] == 'Interest by region':
                self.interest_by_region_widget = widget
            if widget['title'] == 'Related queries':
                self.related_queries_widget = widget
        return

    def interest_over_time(self):
        req_url = "https://www.google.com/trends/api/widgetdata/multiline/csv"
        overtime_payload = dict()
        # convert to string as requests will mangle
        overtime_payload['req'] = json.dumps(self.interest_overtime_widget['request'])
        overtime_payload['token'] = self.interest_overtime_widget['token']
        overtime_payload['tz'] = self.payload['tz']
        req = self.ses.get(req_url, params=overtime_payload)
        print(req.text)

    def related(self, related_type):
        endpoint = related_type.upper() + '_QUERIES_0_0'
        req_url = "http://www.google.com/trends/fetchComponent"
        req = self.ses.get(req_url, params=self.related_queries_payload)
        try:
            if self.google_rl in req.text:
                raise RateLimitError
            # strip off google.visualization.Query.setResponse();
            text = req.text[62:-2]
            self.results = json.loads(text)
        except ValueError:
            raise ResponseError(req.content)
        return self.results

    def top30in30(self):
        form = {'ajax': '1', 'pn': 'p1', 'htv': 'm'}
        req_url = "http://www.google.com/trends/hottrends/hotItems"
        req = self.ses.post(req_url, data=form)
        try:
            if self.google_rl in req.text:
                raise RateLimitError
            self.results = req.json()
        except ValueError:
            raise ResponseError(req.content)
        return self.results

    def hottrends(self, payload):
        req_url = "http://hawttrends.appspot.com/api/terms/"
        req = self.ses.get(req_url, params=payload)
        try:
            if self.google_rl in req.text:
                raise RateLimitError
            self.results = req.json()
        except ValueError:
            raise ResponseError(req.content)
        return self.results

    def hottrendsdetail(self, payload):
        req_url = "http://www.google.com/trends/hottrends/atom/feed"
        req = self.ses.get(req_url, params=payload)
        try:
            if self.google_rl in req.text:
                raise RateLimitError
            # returns XML rss feed!
            self.results = req.text
        except ValueError:
            raise ResponseError(req.content)
        return self.results

    def topcharts(self, payload):
        form = {'ajax': '1'}
        req_url = "http://www.google.com/trends/topcharts/category"
        req = self.ses.post(req_url, params=payload, data=form)
        try:
            if self.google_rl in req.text:
                raise RateLimitError
            self.results = req.json()
        except ValueError:
            raise ResponseError(req.content)
        return self.results

    def suggestions(self, keyword):
        kw_param = quote(keyword)
        req = self.ses.get("https://www.google.com/trends/api/autocomplete/" + kw_param)
        # response is invalid json but if you strip off ")]}'," from the front it is then valid
        try:
            if self.google_rl in req.text:
                raise RateLimitError
            self.results = json.loads(req.text[5:])
        except ValueError:
            raise ResponseError(req.content)
        return self.results

    def _trend_dataframe(self):
        # Only for trends
        df = pd.DataFrame()
        headers = []
        for col in self.results['table']['cols']:
            headers.append(col['label'])
        for row in self.results['table']['rows']:
            row_dict = {}
            for i, value in enumerate(row['c']):
                row_dict[headers[i]] = value['v']
            df = df.append(row_dict, ignore_index=True)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        self.results = df
        return self.results


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class RateLimitError(Error):
    """Exception raised for exceeding rate limit"""

    def __init__(self):
        self.message = "Exceeded Google's Rate Limit. Please use time.sleep() to space requests."
        print(self.message)


class ResponseError(Error):
    """Exception raised for exceeding rate limit"""

    def __init__(self, content):
        self.message = "Response did not parse. See server response for details."
        self.server_error = BeautifulSoup(content, "lxml").findAll("div", {"class": "errorSubTitle"})[0].get_text()
        print(self.message)
        print(self.server_error)


