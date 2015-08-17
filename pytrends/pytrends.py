from __future__ import absolute_import, print_function, unicode_literals

from .connect import GoogleConnection
from .parse import parse_data


class GoogleTrends(object):
    """
    Class to download and parse data from Google Trends.
    """
    def __init__(self, username, password):
        self.connection = GoogleConnection(username, password)

    def query(self, terms, as_topics=None,
              date_filter=None, granularity='day',
              category_filter=None, geo_filter=None, search_filter=None):
        """
        Parameters
        ----------
        terms : list of str
            list of search terms for which to get google trends data;
            may be either raw "search terms" or (Freebase-based) "topics"
        as_topics : list of bool, optional
            a list of boolean values matched to corresponding items in `terms`,
            where `True` indicates that the term is to be treated as a topic,
            and `False` indicates that the term is to be treated as a search term;
            if None (default), all terms are assumed to be "search terms",
            so a same-length list of False values is automatically generated
        date_filter : 2-tuple of str or datetime, optional
            if None (default), effective value is 2004 - present
        granularity : str {'day', 'week'}, optional
            TBD
        category_filter : str, optional
            if None (default), results from 'all categories' are returned
        geo_filter : str, optional
            if None (default), results from 'worldwide' searches are returned
        search_filter : str {'web', 'images', 'news', 'froogle', 'youtube'}, optional
            if None (default), only results from 'web' searches are returned
        """
        raise NotImplementedError()

    def request_report(self, keywords, hl='en-US', cat=None, geo=None,
                        date=None, use_topic=False):
        #use_topic prevents re-urlencoding of topic id's.
        if use_topic:
            query_param = 'q=' + keywords
        else:
            query_param = str(urllib.parse.urlencode({'q':keywords}))

        #This logic handles the default of skipping parameters
        #Parameters that are set to '' will not filter the data requested.
        if cat is not None:
            cat_param = '&cat=' + cat
        else:
            cat_param = ''
        if date is not None:
            date_param = '&' + str(urllib.parse.urlencode({'date':date}))
        else:
            date_param = ''
        if geo is not None:
            geo_param = '&geo=' + geo
        else:
            geo_param = ''
        hl_param = '&hl=' + hl

        #These are the default parameters and shouldn't be changed.
        cmpt_param = "&cmpt=q"
        content_param = "&content=1"
        export_param = "&export=1"

        combined_params = query_param + cat_param + date_param \
                          + geo_param + hl_param + cmpt_param + content_param + export_param

        print("Now downloading information for:")
        print("http://www.google.com/trends/trendsReport?" + combined_params)

        self.raw_data = self.opener.open("http://www.google.com/trends/trendsReport?" + combined_params).read()

        if self.raw_data in ["You must be signed in to export data from Google Trends"]:
            logging.error("You must be signed in to export data from Google Trends")
            raise Exception(self.raw_data)

    def save_csv(self, path, trend_name):
        fileName = path + trend_name + ".csv"
        f = open(fileName, "wb")
        f.write(self.raw_data)
        f.close()

    def get_data(self):
        return self.raw_data
