from __future__ import absolute_import, print_function, unicode_literals

import copy
import csv
from datetime import datetime
from io import open
import re
import sys
if sys.version_info[0] == 2:  # Python 2
    from cookielib import CookieJar
    from cStringIO import StringIO
    from urllib import urlencode
    from urllib2 import build_opener, HTTPCookieProcessor
else:  # Python 3
    from http.cookiejar import CookieJar
    from io import StringIO
    from urllib.parse import urlencode
    from urllib.request import build_opener, HTTPCookieProcessor


class pyGTrends(object):
    """
    Google Trends API
    """
    def __init__(self, username, password):
        # TODO switch to updating fake user agent https://github.com/hellysmile/fake-useragent
        """
        Initialize hard-coded URLs, HTTP headers, and login parameters
        needed to connect to Google Trends, then connect.
        """
        self.login_params = {
            'continue': 'http://www.google.com/trends',
            'PersistentCookie': 'yes',
            'Email': username,
            'Passwd': password}
        # fake user agent
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

    def request_report(self, keywords, hl='en-US', cat=None, geo=None,
                        date=None, use_topic=False):
        # use_topic prevents re-urlencoding of topic id's.
        if use_topic:
            query_param = 'q=' + keywords
        else:
            query_param = str(urlencode({'q':keywords}))

        # This logic handles the default of skipping parameters
        # Parameters that are set to '' will not filter the data requested.
        # See Readme.md for more information
        if cat is not None:
            cat_param = '&cat=' + cat
        else:
            cat_param = ''
        if date is not None:
            date_param = '&' + str(urlencode({'date':date}))
        else:
            date_param = ''
        if geo is not None:
            geo_param = '&geo=' + geo
        else:
            geo_param = ''
        hl_param = '&hl=' + hl

        # These are the default parameters and shouldn't be changed.
        cmpt_param = "&cmpt=q"
        content_param = "&content=1"
        export_param = "&export=1"

        combined_params = query_param + cat_param + date_param \
                          + geo_param + hl_param + cmpt_param + content_param + export_param

        print("Now downloading information for:")
        print("http://www.google.com/trends/trendsReport?" + combined_params)

        self.raw_data = self.opener.open("http://www.google.com/trends/trendsReport?" + combined_params).read()

        if self.raw_data in ["You must be signed in to export data from Google Trends"]:
            print("You must be signed in to export data from Google Trends")
            raise Exception(self.raw_data)

    def save_csv(self, path, trend_name):
        fileName = path + trend_name + ".csv"
        with open(fileName, mode='wb') as f:
            f.write(self.raw_data)

    def get_data(self):
        return self.raw_data.decode(encoding='utf-8')


def parse_data(data):
    """
    Parse data in a Google Trends CSV export (as `str`) into JSON format
    with str values coerced into appropriate Python-native objects.

    Parameters
    ----------
    data : str
        CSV data as text, output by `pyGTrends.get_data()`

    Returns
    -------
    parsed_data : dict of lists
        contents of `data` parsed into JSON form with appropriate Python types;
        sub-tables split into separate dict items, keys are sub-table "names",
        and data values parsed according to type, e.g.
        '10' => 10, '10%' => 10, '2015-08-06' => `datetime.datetime(2015, 8, 6, 0, 0)`
    """
    parsed_data = {}
    for i, chunk in enumerate(re.split(r'\n{2,}', data)):
        if i == 0:
            match = re.search(r'^(.*?) interest: (.*)\n(.*?); (.*?)$', chunk)
            if match:
                source, query, geo, period = match.groups()
                parsed_data['info'] = {'source': source, 'query': query,
                                       'geo': geo, 'period': period}
        else:
            rows = [row for row in csv.reader(StringIO(chunk)) if row]
            if not rows:
                continue
            label, parsed_rows = _parse_rows(rows)
            if label in parsed_data:
                parsed_data[label+'_1'] = parsed_data.pop(label)
                parsed_data[label+'_2'] = parsed_rows
            else:
                parsed_data[label] = parsed_rows

    return parsed_data


def _infer_dtype(val):
    """
    Using regex, infer a limited number of dtypes for string `val`
    (only dtypes expected to be found in a Google Trends CSV export).
    """
    if re.match(r'\d{4}-\d{2}(?:-\d{2})?', val):
        return 'date'
    elif re.match(r'[+-]?\d+$', val):
        return 'int'
    elif re.match(r'[+-]?\d+%$', val):
        return 'pct'
    elif re.match(r'[a-zA-Z ]+', val):
        return 'text'
    else:
        msg = "val={0} dtype not recognized".format(val)
        raise ValueError(msg)


def _convert_val(val, dtype):
    """
    Convert string `val` into Python-native object according to its `dtype`:
    '10' => 10, '10%' => 10, '2015-08-06' => `datetime.datetime(2015, 8, 6, 0, 0)`,
    ' ' => None, 'foo' => 'foo'
    """
    if not val.strip():
        return None
    elif dtype == 'date':
        match = re.match(r'(\d{4}-\d{2}-\d{2})', val)
        if match:
            return datetime.strptime(match.group(), '%Y-%m-%d')
        else:
            return datetime.strptime(re.match(r'(\d{4}-\d{2})', val).group(), '%Y-%m')
    elif dtype == 'int':
        return int(val)
    elif dtype == 'pct':
        return int(val[:-1])
    else:
        return val


def _parse_rows(rows, header='infer'):
    """
    Parse sub-table `rows` into JSON form and convert str values into appropriate
    Python types; if `header` == `infer`, will attempt to infer if header row
    in rows, otherwise pass True/False.
    """
    if not rows:
        raise ValueError('rows={0} is invalid'.format(rows))
    rows = copy.copy(rows)
    label = rows[0][0].replace(' ', '_').lower()

    # HACK: Google replaces rising search percentages with "Breakout" if
    # the increase is greater than 5000: https://support.google.com/trends/answer/4355000
    # for parsing's sake, let's just set it equal to that high threshold value
    for i, row in enumerate(rows):
        for j, val in enumerate(row[1:]):
            if val == 'Breakout':
                rows[i][j+1] = '5000%'

    if header == 'infer':
        if len(rows) >= 3:
            if _infer_dtype(rows[1][-1]) != _infer_dtype(rows[2][-1]):
                header = True
            else:
                header = False
        else:
            header = False
    if header is True:
        colnames = rows[1]
        data_idx = 2
    else:
        colnames = None
        data_idx = 1

    data_dtypes = [_infer_dtype(val) for val in rows[data_idx]]
    if any(dd == 'pct' for dd in data_dtypes):
        label += '_pct'

    parsed_rows = []
    for row in rows[data_idx:]:
        vals = [_convert_val(val, dtype) for val, dtype in zip(row, data_dtypes)]
        if colnames:
            parsed_rows.append({colname:val for colname, val in zip(colnames, vals)})
        else:
            parsed_rows.append(vals)

    return label, parsed_rows
