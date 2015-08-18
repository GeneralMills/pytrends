import sys
# Python 2
if sys.version_info[0] == 2:
    from cookielib import CookieJar
    from cString import StringIO
    from urllib import quote, urlencode
    from urllib2 import build_opener, HTTPCookieProcessor
# Python 3
else:
    from http.cookiejar import CookieJar
    from io import StringIO
    from urllib.parse import quote, urlencode
    from urllib.request import build_opener, HTTPCookieProcessor
