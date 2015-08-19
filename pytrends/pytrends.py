from __future__ import absolute_import, print_function, unicode_literals

from datetime import date, datetime
import io
import json

from .compat import quote
from .connect import GoogleConnection
from .parse import parse_data


class GoogleTrends(object):
    """
    Class to fetch and save data from Google Trends.
    """
    def __init__(self, username, password):
        self.search_filters = {'web', 'images', 'news', 'froogle', 'youtube'}
        self.base_url = 'http://www.google.com/trends/trendsReport?&'
        self.connection = GoogleConnection(username, password)

    def query(self, terms, is_topic=False,
              start_date=None, end_date=None,
              category_filter=None, geo_filter=None, search_filter=None):
        """
        Query Google Trends for `terms`, optionally filtering by date,
        category, geography, and search type.

        Parameters
        ----------
        terms : list of str
            list of search terms for which to get google trends data;
            may be either raw "search terms" or (Freebase-based) "topics"
        is_topic : bool or list of bool, optional
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
        print('\nDownloading data for:\n{}'.format(query_url))

        self.raw_data = self.connection.download_data(query_url)

    def _process_query_terms(self, terms, is_topic):
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

    def save_data(self, fname):
        """
        Save data to disk at `fname`, which includes the full /path/to/file.
        Allowed extensions are .csv and .json; if the latter, raw Google Trends
        data (which comes in CSV form) will be parsed into JSON
        """
        if fname.endswith('.csv'):
            with io.open(fname, mode='w', encoding='utf-8') as f:
                f.write(self.raw_data)
        elif fname.endswith('.json'):
            with io.open(fname, mode='w', encoding='utf-8') as f:
                json.dump(self.parsed_data, f,
                          ensure_ascii=False, sort_keys=True, indent=4,
                          default=self._date_handler_for_json)
        else:
            raise Exception('Data can only be saved as .csv or .json')

    def _date_handler_for_json(self, obj):
        # Python 2's `date.isoformat()` returns str, not _unicode_
        # but json module apparently requires unicode. WUT.
        # so I don't think this works for Python 2.
        return obj.isoformat() if hasattr(obj, 'isoformat') else obj

    def get_data(self, parsed=False):
        if parsed is False:
            return self.raw_data
        else:
            return self.parsed_data

    @property
    def parsed_data(self):
        return parse_data(self.raw_data)
