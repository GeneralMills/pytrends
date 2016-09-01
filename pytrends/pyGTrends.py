from __future__ import absolute_import, print_function, unicode_literals
import sys
import requests
import json
if sys.version_info[0] == 2:  # Python 2
    from urllib import quote
else:  # Python 3
    from urllib.parse import quote


class pyGTrends(object):
    """
    Google Trends API
    """
    def __init__(self):
        # TODO add quota error handling
        self.results = None

    def trend(self, payload):
        payload['cid'] = 'TIMESERIES_GRAPH_0'
        payload['export'] = 3
        req_url = "http://www.google.com/trends/fetchComponent"
        req = requests.get(req_url, params=payload)
        self.results = req.json

    def toprelated(self, payload):
        payload['cid'] = 'RISING_QUERIES_0_0'
        payload['export'] = 3
        if 'hl' not in payload:
            payload['hl'] = 'en-US'
        req_url = "http://www.google.com/trends/fetchComponent"
        req = requests.get(req_url, params=payload)
        self.results = req.json

    def top30in30(self):
        form = {'ajax': '1', 'pn': 'p1', 'htv': 'm'}
        req_url = "http://www.google.com/trends/hottrends/hotItems"
        req = requests.post(req_url, data=form)
        self.results = req.json

    def hottrends(self, payload):
        req_url = "http://hawttrends.appspot.com/api/terms/"
        req = requests.get(req_url, params=payload)
        self.results = req.json

    def hottrendsdetail(self, payload):
        req_url = "http://www.google.com/trends/hottrends/atom/feed"
        req = requests.get(req_url, params=payload)
        self.results = req.json

    def topcharts(self, form):
        form['ajax'] = '1'
        req_url = "http://www.google.com/trends/topcharts/category"
        req = requests.post(req_url, data=form)
        self.results = req.json

    def suggestions(self, keyword):
        kw_param = quote(keyword)
        req = requests.get("https://www.google.com/trends/api/autocomplete/" + kw_param)
        # response is invalid json but if you strip off ")]}'," from the front it is then valid
        json_data = json.loads(req.text[5:])
        self.results = json_data