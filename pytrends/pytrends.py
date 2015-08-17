from __future__ import absolute_import, print_function, unicode_literals

from datetime import date, datetime
import sys
if sys.version_info[0] == 2:  # Python 2
    from urllib import quote, urlencode
else:  # Python 3
    from urllib.parse import quote, urlencode

from .connect import GoogleConnection
from .parse import parse_data


class GoogleTrends(object):
    """
    Class to download and parse data from Google Trends.
    """
    def __init__(self, username, password):
        self.search_filters = {'web', 'images', 'news', 'froogle', 'youtube'}
        self.base_url = 'http://www.google.com/trends/trendsReport?'
        self.connection = GoogleConnection(username, password)

    def query(self, terms, is_topic,
              start_date=None, end_date=None,
              category_filter=None, geo_filter=None, search_filter=None):
        """
        Parameters
        ----------
        terms : list of str
            list of search terms for which to get google trends data;
            may be either raw "search terms" or (Freebase-based) "topics"
        is_topic : bool or list of bool
            a list of boolean values matched to corresponding items in `terms`,
            where `True` indicates that the term is to be treated as a topic,
            and `False` indicates that the term is to be treated as a search term;
            if False (default), all terms are assumed to be "search terms",
            so a same-length list of False values is auto-generated;
            if True, a same-length list of True values is auto-generated
        start_date : str or `datetime.date`, optional
            if None (default), effective value is 2004-01-01 (or 2008-01-01);
            if str, must be in ISO standard format: YYYY-MM-DD;
            Note: day doesn't matter, only year and month
        end_date : str or `datetime.date`, optional
            if None (default), effective value is today's date;
            if str, must be in ISO standard format: YYYY-MM-DD;
            Note: day doesn't matter, only year and month
        category_filter : str, optional
            if None (default), results from 'all categories' are returned
        geo_filter : str, optional
            if None (default), results from 'worldwide' searches are returned
        search_filter : str {'web', 'images', 'news', 'froogle', 'youtube'}, optional
            if None (default), only results from 'web' searches are returned
        """
        query_param = self._process_query_terms(terms, is_topic)
        if search_filter:
            if search_filter not in self.search_filters:
                msg = '`search_filter` {0} not valid; options are {1}'.format(
                    search_filter, self.search_filters)
                raise ValueError(msg)
            else:
                gprop_param = 'gprop={}'.format(search_filter)
        else:
            gprop_param = None
        start_date, end_date = self._process_date_filter(
            start_date, end_date, search_filter)
        if start_date and end_date:
            date_param = '{0} {1}m'.format(
                start_date.strftime('%m/%Y'),
                1 + 12*(end_date.year-start_date.year) + (end_date.month-start_date.month))
            date_param = 'date={}'.format(quote(date_param, safe=''))
        else:
            date_param = None
        if category_filter:
            cat_param = 'cat={}'.format(category_filter)
        else:
            cat_param = None
        if geo_filter:
            geo_param = 'geo={}'.format(geo_filter)
        else:
            geo_param = None

        # default params, not to be changed
        cmpt_param = 'cmpt=q'
        content_param = 'content=1'
        export_param = 'export=1'

        params = [query_param, cat_param, date_param, gprop_param, geo_param,
                  cmpt_param, content_param, export_param]
        params = '&'.join(param for param in params if param)
        query_url = self.base_url + params
        print('Downloading data for:\n{}'.format(query_url))

        self.raw_data = self.connection.download_data(query_url)

    def _process_query_terms(self, terms, is_topic):
        """
        """
        if len(terms) > 5:
            raise ValueError('Google Trends allows 5 or fewer terms at at time')
        if isinstance(is_topic, bool):
            is_topic = [is_topic for _ in range(len(terms))]
        elif len(is_topic) != len(terms):
            msg = 'Each term in `terms` must have a matching True/False in `is_topic`'
            raise ValueError(msg)
        delim = quote(', ')
        query_param = 'q={}'.format(
            delim.join(term if topic is True else quote(term)
                       for term, topic in zip(terms, is_topic)))
        return query_param

    def _process_date_filter(self, start_date, end_date, search_filter=None):
        """
        """
        if not search_filter or search_filter == 'web':
            min_start_date = date(year=2004, month=1, day=1)
        else:
            min_start_date = date(year=2008, month=1, day=1)
        if start_date:
            if not isinstance(start_date, date):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if start_date < min_start_date:
                msg = 'Earliest available Google Trends data is {}'.format(
                    min_start_date)
                raise ValueError(msg)
            if not end_date:
                end_date = date.today()
        if end_date:
            if not isinstance(end_date, date):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            if end_date > date.today():
                msg = 'Latest available Google Trends data is {} (today)'.format(
                    date.today())
                raise ValueError(msg)
            if not start_date:
                start_date = min_start_date
        return start_date, end_date

    def save_csv(self, path, trend_name):
        fileName = path + trend_name + ".csv"
        f = open(fileName, "wb")
        f.write(self.raw_data)
        f.close()

    def get_data(self):
        return self.raw_data
