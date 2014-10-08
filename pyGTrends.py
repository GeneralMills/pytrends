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
        self.url_Export = "http://www.google.com/trends/viz"
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

    def download_report(self, topicFg, trendName='Unknown', hl='en-US', cat='0-71', keywords='Unknown', geo='US',
                        date='all', cmpt='q', content=1, export=1):
        """
        download a specific report
        date, geo, geor, graph, sort, scale and sa
        are all Google Trends specific ways to slice the data
        """
        param1 = urllib.parse.urlencode({
            "hl": hl,
            "cat": cat
        })

        # prevent reencoding of topic id's
        if topicFg == True:
            param2 = param1 + "&q=" + keywords
        else:
            param2 = param1 + "&" + urllib.parse.urlencode({'q': keywords})

        params = param2 + "&" + urllib.parse.urlencode({
            "geo": geo,
            "date": date,
            "cmpt": cmpt,
            "content": str(content),
            "export": str(export)
        })

        self.raw_data = self.opener.open("http://www.google.com/trends/trendsReport?" + params).read()

        if self.raw_data in ["You must be signed in to export data from Google Trends"]:
            logging.error("You must be signed in to export data from Google Trends")
            raise Exception(self.raw_data)

    def csv(self, path, trendName='Unknown'):
        fileName = path + trendName.replace(" ", "_").replace("/", "_").replace(",", "_") + ".csv"
        f = open(fileName, "wb")
        f.write(self.raw_data)
        f.close()

    def get_data(self):
        return self.raw_data


