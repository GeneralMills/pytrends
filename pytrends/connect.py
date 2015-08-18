from __future__ import absolute_import, print_function, unicode_literals

import re

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
        self.headers = [
            ('Referrer', 'https://www.google.com/accounts/ServiceLoginBoxAuth'),
            ('Content-type', 'application/x-www-form-urlencoded'),
            ('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0 Safari/535.21'),
            ('Accept', 'text/plain')]
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
        self.opener.addheaders = self.headers

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

    def download_data(self, query):
        """
        Download raw CSV file matching Google Trends `query` as a single string.
        """
        data = self.opener.open(query).read()
        data = data.decode(encoding='utf-8')
        # TODO: is there a better way to handle this error? (how to provoke it?)
        if data in ['You must be signed in to export data from Google Trends']:
            print('You must be signed in to export data from Google Trends!')
            raise Exception(data)

        return data
