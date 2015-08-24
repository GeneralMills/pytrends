from __future__ import absolute_import, print_function, unicode_literals

from random import random
import re
import time

from fake_useragent import UserAgent

from .compat import build_opener, CookieJar, urlencode, HTTPCookieProcessor


class GoogleConnection(object):
    """
    Class to connect to Google Trends by logging in with a valid
    Google username and password.
    """
    _CACHE = {}

    def __init__(self, username, password, wait=3.0):
        """
        Initialize hard-coded URLs, HTTP headers, and login parameters
        needed to connect to Google Trends, then connect.
        """
        self.avg_wait = wait
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
        self._set_last_call_time(time.time())

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

    def _set_last_call_time(self, timestamp):
        self.last_call_time = timestamp

    def _wait_for_rate_limit(self):
        """
        Check the time elapsed since the last call to Google; if less than the desired
        wait time (a randomized value; average equal to `wait` set in `__init__()`),
        pause code until the desired wait time has elapsed.
        """
        wait_time = (2 * self.avg_wait * random()) + 0.1  # add small safety factor
        time_since_last_call = time.time() - self.last_call_time
        if time_since_last_call < wait_time:
            sleep_time = wait_time - time_since_last_call
            # print('Rate limit (sleeping {} seconds ...)'.format(sleep_time))
            time.sleep(sleep_time)

    def _randomize_header_ua(self):
        """
        Set a randomized User Agent in headers, update opener's headers list.
        """
        self.headers['User-Agent'] = self.fake_ua.chrome
        self.opener.addheaders = list(self.headers.items())

    def clear_cache(self):
        self._CACHE = {}

    def download_data(self, query):
        """
        Download raw CSV file matching Google Trends `query` as a single string.
        Data is cached locally to minimize unnecessary calls.
        """
        # check the cache first
        if query in self._CACHE:
            print('\nFetching cached data for:\n{}'.format(query))
            return self._CACHE[query]
        self._randomize_header_ua()
        self._wait_for_rate_limit()
        print('\nDownloading data for:\n{}'.format(query))
        data = self.opener.open(query).read()
        self._set_last_call_time(time.time())
        data = data.decode(encoding='utf-8')
        # TODO: is there a better way to handle this error? (how to provoke it?)
        if data in ['You must be signed in to export data from Google Trends']:
            print('You must be signed in to export data from Google Trends!')
            raise Exception(data)
        # cache the data for this call
        self._CACHE[query] = data

        return data
