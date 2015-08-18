from __future__ import absolute_import, print_function, unicode_literals

import re

from fake_useragent import UserAgent

from .compat import build_opener, CookieJar, urlencode, HTTPCookieProcessor

# TODO: add a simple cache to minimize unnecessary calls?
# TODO: add rate-limiting to avoid angering the Google gods?

class GoogleConnection(object):
    """
    Class to connect to Google Trends by logging in with a valid
    Google username and password.
    """
    def __init__(self, username, password):
        """
        Initialize hard-coded URLs, HTTP headers, and login parameters
        needed to connect to Google Trends, then connect.
        """
        self.login_params = {
            'continue': 'http://www.google.com/trends',
            'PersistentCookie': 'yes',
            'Email': username,
            'Passwd': password}
        self.headers = {
            'Referrer': 'https://www.google.com/accounts/ServiceLoginBoxAuth',
            'Content-type': 'application/x-www-form-urlencoded',
            'Accept': 'text/plain'}
        # Note: 'User-Agent' is randomly assigned in `_randomize_header_ua()`
        self.fake_ua = UserAgent()
        self.url_ServiceLoginBoxAuth = 'https://accounts.google.com/ServiceLoginBoxAuth'
        self.url_Export = 'http://www.google.com/trends/trendsReport'
        self.url_CookieCheck = 'https://www.google.com/accounts/CheckCookie?chtml=LoginDoneHtml'
        self.url_PrefCookie = 'http://www.google.com'
        self._connect()

    def _connect(self):
        """
        Connect to Google Trends. Use cookies.
        """
        self.cj = CookieJar()
        self.opener = build_opener(HTTPCookieProcessor(self.cj))
        self._randomize_header_ua()

        resp = self.opener.open(self.url_ServiceLoginBoxAuth).read()
        resp = re.sub(r'\s\s+', ' ', resp.decode(encoding='utf-8'))

        galx = re.compile('<input name="GALX"[\s]+type="hidden"[\s]+value="(?P<galx>[a-zA-Z0-9_-]+)">')
        m = galx.search(resp)
        if not m:
            raise Exception('Cannot parse GALX out of login page')
        self.login_params['GALX'] = m.group('galx')
        params = urlencode(self.login_params).encode('utf-8')
        self.opener.open(self.url_ServiceLoginBoxAuth, params)
        self.opener.open(self.url_CookieCheck)
        self.opener.open(self.url_PrefCookie)

    def _randomize_header_ua(self):
        """
        Set a randomized User Agent in headers, update opener's headers list.
        """
        self.headers['User-Agent'] = self.fake_ua.chrome
        self.opener.addheaders = list(self.headers.items())

    def download_data(self, query):
        """
        Download raw CSV file matching Google Trends `query` as a single string.
        """
        self._randomize_header_ua()
        data = self.opener.open(query).read()
        data = data.decode(encoding='utf-8')
        # TODO: is there a better way to handle this error? (how to provoke it?)
        if data in ['You must be signed in to export data from Google Trends']:
            print('You must be signed in to export data from Google Trends!')
            raise Exception(data)

        return data
