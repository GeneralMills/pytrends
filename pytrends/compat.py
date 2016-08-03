import sys

# Python 3
if sys.version_info[0] == 3:
    string_type = str
    from csv import reader as csv_reader
    from http.cookiejar import CookieJar
    from io import StringIO
    from urllib.parse import quote, urlencode
    from urllib.request import build_opener, HTTPCookieProcessor

# Python 2
else:
    string_type = basestring
    from cookielib import CookieJar
    from StringIO import StringIO
    from urllib import quote, urlencode
    from urllib2 import build_opener, HTTPCookieProcessor

    # Python 2's csv module can't handle unicode (UGH WHY?!)
    # here's a workaround (https://docs.python.org/2.7/library/csv.html#examples)
    import csv
    def _unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
        # csv.py doesn't do Unicode; encode temporarily as UTF-8:
        csv_reader = csv.reader(_utf_8_encoder(unicode_csv_data),
                                dialect=dialect, **kwargs)
        for row in csv_reader:
            # decode UTF-8 back to Unicode, cell by cell:
            yield [unicode(cell, 'utf-8') for cell in row]
    def _utf_8_encoder(unicode_csv_data):
        for line in unicode_csv_data:
            yield line.encode('utf-8')
    csv_reader = _unicode_csv_reader
