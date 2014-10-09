import http.client
import urllib
from urllib import request
from urllib import parse
import re
import logging
import http.cookiejar


class pyGTrends(object):
    """
    Google Trends API
    """

    def __init__(self, username, password):
        """
        provide login and password to be used to connect to Google Analytics
        all immutable system variables are also defined here
        website_id is the ID of the specific site on google analytics
        """
        self.login_params = {
            "continue": "http://www.google.com/trends",
            "PersistentCookie": "yes",
            "Email": username,
            "Passwd": password,
        }
        self.headers = [("Referrer", "https://www.google.com/accounts/ServiceLoginBoxAuth"),
                        ("Content-type", "application/x-www-form-urlencoded"),
                        ("User-Agent",
                         "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0 Safari/535.21"),
                        ("Accept", "text/plain")]
        self.url_ServiceLoginBoxAuth = "https://accounts.google.com/ServiceLoginBoxAuth"
        self.url_Export = "http://www.google.com/trends/trendsReport"
        self.url_CookieCheck = "https://www.google.com/accounts/CheckCookie?chtml=LoginDoneHtml"
        self.url_PrefCookie = "http://www.google.com"
        self.header_dictionary = {}
        self._connect()

    def _connect(self):
        """
        connect to Google Trends
        """

        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
        self.opener.addheaders = self.headers

        galx = re.compile('<input name="GALX"[\s]+type="hidden"[\s]+value="(?P<galx>[a-zA-Z0-9_-]+)">')

        resp = self.opener.open(self.url_ServiceLoginBoxAuth).read()
        resp = re.sub(r'\s\s+', ' ', bytes.decode(resp))

        m = galx.search(resp)
        # print(resp)
        if not m:
            raise Exception("Cannot parse GALX out of login page")
        self.login_params["GALX"] = m.group("galx")
        params = urllib.parse.urlencode(self.login_params).encode("utf-8")
        self.opener.open(self.url_ServiceLoginBoxAuth, params)
        self.opener.open(self.url_CookieCheck)
        self.opener.open(self.url_PrefCookie)

    def request_report(self, trend_name, keywords, hl='en-US', cat=None, geo=None,
                        date=None, use_topic=False):

        # prevent re-urlencoding of topic id's
        if use_topic == True:
            query_param = {'q': keywords}
        else:
            query_param = urllib.parse.urlencode({'q': keywords})

        #handle default of skipping parameters, which will default to give all available data
        if cat is not None:
            cat_param = '&' + urllib.parse.urlencode({'cat':cat})
        else:
            cat_param = ''
        if date is not None:
            date_param = '&' + urllib.parse.urlencode({'date':date})
        else:
            date_param = ''
        if geo is not None:
            geo_param = '&' + urllib.parse.urlencode({'geo':geo})
        else:
            geo_param = ''

        #default params
        hl_param = '&' + urllib.parse.urlencode({'hl':hl})
        cmpt_param = "&cmpt=q"
        content_param = "&content=1"
        export_param = "&export=1"

        combined_params = query_param + cat_param + date_param \
                          + geo_param + hl_param + cmpt_param + content_param + export_param
        print(combined_params)

        self.raw_data = self.opener.open("http://www.google.com/trends/trendsReport?" + combined_params).read()

        if self.raw_data in ["You must be signed in to export data from Google Trends"]:
            logging.error("You must be signed in to export data from Google Trends")
            raise Exception(self.raw_data)

    def csv(self, path, trend_name):
        fileName = path + trend_name + ".csv"
        f = open(fileName, "wb")
        f.write(self.raw_data)
        f.close()

    def get_data(self):
        return self.raw_data


