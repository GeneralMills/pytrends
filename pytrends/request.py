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
        self.input = dict()

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
        dico = {}
        for u in soup_login:
            if u.has_attr('value') and u.has_attr('name'):
                dico[u['name']] = u['value']
        # override the inputs with out login and pwd:
        dico['Email'] = self.username
        dico['Passwd'] = self.password
        self.ses.post(self.url_auth, data=dico)

    def _build_payload(self):
        # TODO set default values, and check if new ones added
        token_payload = dict()
        token_payload['hl'] = self.input['hl']
        token_payload['tz'] = self.input['tz']
        token_payload['property'] = self.input['property']
        token_payload['req'] = {'comparisonItem': [], 'category': self.input['cat']}
        kw_list = self.input['kw_list']
        kw_time = self.input['timeframe']
        geo = self.input['geo']
        for kw in kw_list:
            keyword_payload = {'keyword': kw, 'time': kw_time, 'geo': geo}
            token_payload['req']['comparisonItem'].append(keyword_payload)

        # requests will mangle this if it is not a string
        token_payload['req'] = json.dumps(token_payload['req'])
        self.token_payload = token_payload
        return

    def tokens(self, payload):
        self.input = payload
        self._build_payload()
        req_url = "https://www.google.com/trends/api/explore"
        req = self.ses.get(req_url, params=self.token_payload)
        # strip off garbage characters that break json parser
        widget_json = req.text[4:]
        widget_dict = json.loads(widget_json)['widgets']
        # order of the json matters...
        first_region_token = True
        first_related_token = True
        # assign requests
        for widget in widget_dict:
            if widget['title'] == 'Interest over time':
                self.interest_overtime_widget = widget
            if widget['title'] == 'Interest by region' and first_region_token:
                self.interest_by_region_widget = widget
                first_region_token = False
            # response for each term, put into a list
            if widget['title'] == 'Related queries':
                self.related_queries_widget_list.append(widget)

        return

    def interest_over_time(self):
        req_url = "https://www.google.com/trends/api/widgetdata/multiline"
        overtime_payload = dict()
        # convert to string as requests will mangle
        overtime_payload['req'] = json.dumps(self.interest_overtime_widget['request'])
        overtime_payload['token'] = self.interest_overtime_widget['token']
        overtime_payload['tz'] = self.input['tz']
        req = self.ses.get(req_url, params=overtime_payload)
        # strip off garbage characters that break json parser
        req_json = json.loads(req.text[5:])
        df = pd.DataFrame(req_json['default']['timelineData'])
        df['date'] = pd.to_datetime(df['time'], unit='s')
        df = df.set_index(['date']).sort_index()
        # split list columns into seperate ones, remove brackets and split on comma
        result_df = df['value'].apply(lambda x: pd.Series(str(x).replace('[', '').replace(']', '').split(',')))
        # rename each column with its search term
        for idx, kw in enumerate(self.input['kw_list']):
            result_df[kw] = result_df[idx].astype('int')
            del result_df[idx]
        return result_df

    def interest_by_region(self):
        req_url = "https://www.google.com/trends/api/widgetdata/comparedgeo"
        region_payload = dict()
        # TODO need to handle this if not filled in
        # self.interest_by_region_widget['request']['resolution'] = self.input['resolution']
        # convert to string as requests will mangle
        region_payload['req'] = json.dumps(self.interest_by_region_widget['request'])
        region_payload['token'] = self.interest_by_region_widget['token']
        region_payload['tz'] = self.input['tz']
        req = self.ses.get(req_url, params=region_payload)
        # strip off garbage characters that break json parser
        req_json = json.loads(req.text[5:])
        df = pd.DataFrame(req_json['default']['geoMapData'])
        # rename the column with the search keyword
        df = df[['geoCode', 'geoName', 'value']].set_index(['geoCode', 'geoName']).sort_index()
        # split list columns into seperate ones, remove brackets and split on comma
        result_df = df['value'].apply(lambda x: pd.Series(str(x).replace('[', '').replace(']', '').split(',')))
        # rename each column with its search term
        for idx, kw in enumerate(self.input['kw_list']):
            result_df[kw] = result_df[idx].astype('int')
            del result_df[idx]
        return result_df

    def related_queries(self):
        req_url = "https://www.google.com/trends/api/widgetdata/relatedsearches"
        related_payload = dict()
        result_dict = dict()
        for request_json in self.related_queries_widget_list:
            # keyword
            kw = request_json['request']['restriction']['complexKeywordsRestriction']['keyword'][0]['value']
            # convert to string as requests will mangle
            related_payload['req'] = json.dumps(request_json['request'])
            related_payload['token'] = request_json['token']
            related_payload['tz'] = self.input['tz']
            req = self.ses.get(req_url, params=related_payload)
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

    def search_topics(self):
        req_url = "https://www.google.com/trends/api/widgetdata/relatedsearches"
        #https://www.google.com/trends/api/widgetdata/relatedsearches?hl=en-US&tz=360&req=%7B%22restriction%22:%7B%22geo%22:%7B%7D,%22time%22:%222012-01-25+2017-01-25%22%7D,%22keywordType%22:%22ENTITY%22,%22metric%22:%5B%22TOP%22,%22RISING%22%5D,%22trendinessSettings%22:%7B%22compareTime%22:%222007-01-23+2012-01-24%22%7D,%22requestOptions%22:%7B%22property%22:%22%22,%22backend%22:%22IZG%22,%22category%22:0%7D,%22language%22:%22en%22%7D&token=APP6_UEAAAAAWIpBfUrqpmfyXpLvhy1-PNqC9yU7prWF
        # TODO add rising vs TOP
        searchtopics_payload = dict()
        # convert to string as requests will mangle
        searchtopics_payload['req'] = json.dumps(self.related_queries_widget['request'])
        searchtopics_payload['token'] = self.related_queries_widget['token']
        searchtopics_payload['tz'] = self.payload['tz']
        req = self.ses.get(req_url, params=searchtopics_payload)
        return req.text

    def search_queries(self):
        # TODO add rising vs TOP
        req_url = "https://www.google.com/trends/api/widgetdata/relatedsearches"
        # https://www.google.com/trends/api/widgetdata/relatedsearches?hl=en-US&tz=360&req=%7B%22restriction%22:%7B%22geo%22:%7B%7D,%22time%22:%222012-01-25+2017-01-25%22%7D,%22keywordType%22:%22QUERY%22,%22metric%22:%5B%22TOP%22,%22RISING%22%5D,%22trendinessSettings%22:%7B%22compareTime%22:%222007-01-23+2012-01-24%22%7D,%22requestOptions%22:%7B%22property%22:%22%22,%22backend%22:%22IZG%22,%22category%22:0%7D,%22language%22:%22en%22%7D&token=APP6_UEAAAAAWIpBfTA9jnC5PimqZEoZ4shRwCFi1cm4
        searchqueries_payload = dict()
        # convert to string as requests will mangle
        searchqueries_payload['req'] = json.dumps(self.related_queries_widget['request'])
        searchqueries_payload['token'] = self.related_queries_widget['token']
        searchqueries_payload['tz'] = self.payload['tz']
        req = self.ses.get(req_url, params=searchqueries_payload)
        return req.text

    def trending_searches(self):

        req_url = "https://www.google.com/trends/hottrends/widget?pn=p1&tn=10&h=413"
        req = self.ses.get(req_url)
        return req.text

    def hottrendsdetail(self, payload):
        # TODO verify
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
        # TODO verify
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
        # TODO verify
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


