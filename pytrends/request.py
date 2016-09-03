from __future__ import absolute_import, print_function, unicode_literals
import sys
import requests
import json
import re
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
        self.url_login = "https://accounts.google.com/ServiceLogin"
        self.url_auth = "https://accounts.google.com/ServiceLoginAuth"
        # custom user agent so users know what "new account signin for Google" is
        if custom_useragent is None:
            self.custom_useragent = {'User-Agent': 'PyTrends'}
        else:
            self.custom_useragent = {'User-Agent': custom_useragent}
        self._connect()
        self.results = None

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
            if u.has_attr('value'):
                dico[u['name']] = u['value']
        # override the inputs with out login and pwd:
        dico['Email'] = self.username
        dico['Passwd'] = self.password
        self.ses.post(self.url_auth, data=dico)

    def trend(self, payload, return_type=None):
        payload['cid'] = 'TIMESERIES_GRAPH_0'
        payload['export'] = 3
        req_url = "http://www.google.com/trends/fetchComponent"
        req = self.ses.get(req_url, params=payload)
        # strip off js function call 'google.visualization.Query.setResponse();
        text = req.text[62:-2]
        # replace series of commas ',,,,'
        text = text.replace(',,,,', '')
        # replace js new Date(YYYY, M, 1) calls with ISO 8601 date as string
        pattern = re.compile(r'new Date\(\d{4},\d{1,2},1\)')
        for match in re.finditer(pattern, text):
            # slice off 'new Date(' and ')' and split by comma
            csv_date = match.group(0)[9:-1].split(',')
            year = csv_date[0]
            # js date function is 0 based... why...
            month = str(int(csv_date[1]) + 1).zfill(2)
            # covert into "YYYY-MM-DD" including quotes
            str_dt = '"' + year + '-' + month + '-01"'
            text = text.replace(match.group(0), str_dt)
        try:
            self.results = json.loads(text)
        except json.decoder.JSONDecodeError:
            print("JSON did not parse. See server response below for details.")
            print(req.text)
        if return_type == 'json' or return_type is None:
            return self.results
        if return_type == 'dataframe':
            self._trend_dataframe()
            return self.results

    def toprelated(self, payload):
        payload['cid'] = 'RISING_QUERIES_0_0'
        payload['export'] = 3
        if 'hl' not in payload:
            payload['hl'] = 'en-US'
        req_url = "http://www.google.com/trends/fetchComponent"
        req = self.ses.get(req_url, params=payload)
        # strip off google.visualization.Query.setResponse();
        text = req.text[62:-2]
        try:
            self.results = json.loads(text)
        except json.decoder.JSONDecodeError:
            print("JSON did not parse. See server response below for details.")
            print(req.text)
        return self.results

    def top30in30(self):
        form = {'ajax': '1', 'pn': 'p1', 'htv': 'm'}
        req_url = "http://www.google.com/trends/hottrends/hotItems"
        req = self.ses.post(req_url, data=form)
        try:
            self.results = req.json()
        except json.decoder.JSONDecodeError:
            print("JSON did not parse. See server response below for details.")
            print(req.text)
        return self.results

    def hottrends(self, payload):
        req_url = "http://hawttrends.appspot.com/api/terms/"
        req = self.ses.get(req_url, params=payload)
        try:
            self.results = req.json()
        except json.decoder.JSONDecodeError:
            print("JSON did not parse. See server response below for details.")
            print(req.text)
        return self.results

    def hottrendsdetail(self, payload):
        req_url = "http://www.google.com/trends/hottrends/atom/feed"
        req = self.ses.get(req_url, params=payload)
        # returns XML rss feed!
        self.results = req.text
        return self.results

    def topcharts(self, payload):
        form = {'ajax': '1'}
        req_url = "http://www.google.com/trends/topcharts/category"
        req = self.ses.post(req_url, params=payload, data=form)
        try:
            self.results = req.json()
        except json.decoder.JSONDecodeError:
            print("JSON did not parse. See server response below for details.")
            print(req.text)
        return self.results

    def suggestions(self, keyword):
        kw_param = quote(keyword)
        req = self.ses.get("https://www.google.com/trends/api/autocomplete/" + kw_param)
        # response is invalid json but if you strip off ")]}'," from the front it is then valid
        try:
            self.results = json.loads(req.text[5:])
        except json.decoder.JSONDecodeError:
            print("JSON did not parse. See server response below for details.")
            print(req.text)
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
