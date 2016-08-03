from __future__ import absolute_import, print_function, unicode_literals

from datetime import date, datetime
import io
import json

import arrow

from .compat import quote, string_type
from .connect import GoogleConnection
from .parse import parse_data

# TODO: specify granularity for timeseries data (daily, weekly, monthly)
# automatically handle searching over multiple time sub-periods and scaling
# periods to match each other over the full time period

class GoogleTrends(object):
    """
    Class to fetch and save data from Google Trends.
    """
    def __init__(self, username, password, wait=3.0):
        """
        Parameters
        ----------
        username : str
        password : str
        wait : int or float, optional
            number of seconds (on average) to wait between queries;
            minimum recommended value is 1 -- don't provoke Google with rapid-fire requests
        """
        self.search_filters = {'web', 'images', 'news', 'froogle', 'youtube'}
        self.base_url = 'http://www.google.com/trends/trendsReport?&'
        self.connection = GoogleConnection(username, password, wait=wait)

    def query(self, terms, is_topic=False,
              start_date=None, end_date=None, granularity='auto',
              category_filter=None, geo_filter=None, search_filter=None,
              language=None):
        """
        Query Google Trends for `terms`, optionally filtering by date,
        category, geography, and search type.

        Parameters
        ----------
        terms : str or list of str
            single search term or list of search terms for which to get trends data
            may be either raw "search terms" or (Freebase) "topics"
        is_topic : bool or list of bool, optional
            a list of boolean values matched to corresponding items in `terms`,
            where `True` indicates that the term is to be treated as a topic,
            and `False` indicates that the term is to be treated as a search term;
            if False (default), all terms are assumed to be "search terms",
            so a same-length list of False values is auto-generated;
            if True, a same-length list of True values is auto-generated
        start_date : str, `datetime.datetime`, or `datetime.date`, optional
            if None (default), effective value is 2004-01-01 (or 2008-01-01);
            if str, must be in ISO standard format: YYYY-MM-DD;
            Note: day doesn't matter, only year and month
        end_date : str, `datetime.datetime`, or `datetime.date`, optional
            if None (default), effective value is today's date;
            if str, must be in ISO standard format: YYYY-MM-DD;
            Note: day doesn't matter, only year and month
        granularity : str {'auto', 'daily'}, optional
            if 'auto' (default), Google Trends will automatically determine the
            granularity of search volume over time (see Notes below);
            if 'daily', a series of 3-month queries are concatenated together,
            and search volume values between 3-month spans are scaled to match
            based on shared values for overlapping months
        category_filter : str, optional
            if None (default), results from 'all categories' are returned;
            otherwise, manually extract valid values from the web GUI's URLs
        geo_filter : str, optional
            if None (default), results from 'worldwide' searches are returned
            otherwise, manually extract valid values from the web GUI's URLs
        search_filter : str {'web', 'images', 'news', 'froogle', 'youtube'}, optional
            if None (default), only results from 'web' searches are returned
        language : str, optional
            if None (default), data headers are in English ('en');
            otherwise, specify the desired 2-letter language code; see
            https://sites.google.com/site/tomihasa/google-language-codes
            for a list of available google web interface language codes

        Notes
        -----
        Google Trends data over time can come in daily, weekly, or monthly frequencies.
        To get daily data, queries must be over a timespan of 3 months or less.
        Otherwise, weekly data is usually returned, unless the query is low popularity,
        in which case monthly data is returned. Lastly, if multiple terms are queried
        and some don't return enough data, the csv will automatically exclude them.
        """
        # set optional params
        query_param = self._process_query_terms(terms, is_topic)
        gprop_param = self._process_search_filter(search_filter)
        cat_param = 'cat={}'.format(category_filter) if category_filter else None
        geo_param = 'geo={}'.format(geo_filter) if geo_filter else None
        hl_param = 'hl={}'.format(language) if language else None

        # set default params
        cmpt_param = 'cmpt=q'
        content_param = 'content=1'
        export_param = 'export=1'

        # get processed start and end dates for query
        # which depend on search filter and granularity arguments
        start_date, end_date = self._process_date_filter(
            start_date, end_date, search_filter, granularity)

        # handle complicated case where multiple calls need to be made
        # then concatenated and re-normalized
        if granularity == 'daily':
            queries = []
            while start_date < end_date:
                n_months = min(int((end_date - start_date).days / 30), 3)
                date_param = 'date={}'.format(quote(
                    '{0} {1}m'.format(start_date.format('MM/YYYY'), n_months), safe=''))
                print(start_date.format('MM/YYYY'), n_months)
                params = [query_param, cat_param, date_param, gprop_param, geo_param,
                          hl_param, cmpt_param, content_param, export_param]
                params = '&'.join(param for param in params if param)
                query_url = self.base_url + params
                self.raw_data = self.connection.download_data(query_url)

                # save queries, access corresponding data in connection's cache
                # the cache does double-duty here: this is more memory-efficient
                # than saving *two* copies, one in connection the other here
                queries.append(query_url)
                # 3-month timespans are queried, but the start date is only
                # increased by 2 months; this ensures overlap, for re-normalization
                start_date = start_date.replace(months=+2)

            # TODO: implement code to concatenate results across 3-month spans
            # and re-scale them to match based on overlapping month's values

            return

        # otherwise, a single call is needed, with or without date param
        elif start_date and end_date:
            n_months = (1 + 12*(end_date.year - start_date.year)
                        + (end_date.month - start_date.month))
            date_param = 'date={}'.format(quote(
                '{0} {1}m'.format(start_date.format('MM/YYYY'), n_months), safe=''))
        else:
            date_param = None

        params = [query_param, cat_param, date_param, gprop_param, geo_param,
                  hl_param, cmpt_param, content_param, export_param]
        params = '&'.join(param for param in params if param)
        query_url = self.base_url + params
        self.raw_data = self.connection.download_data(query_url)

    def _process_query_terms(self, terms, is_topic):
        if isinstance(terms, string_type):
            terms = [terms]
        elif len(terms) > 5:
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

    def _process_search_filter(self, search_filter):
        if search_filter:
            if search_filter not in self.search_filters:
                msg = '`search_filter` {0} not valid; options are {1}'.format(
                    search_filter, self.search_filters)
                raise ValueError(msg)
            else:
                gprop_param = 'gprop={}'.format(search_filter)
        else:
            gprop_param = None
        return gprop_param

    def _process_date_filter(self, start_date, end_date,
                             search_filter, granularity):
        if granularity not in {'daily', 'auto'}:
            msg = "Invalid `granularity` parameter; must be 'daily' or 'auto'"
            raise ValueError(msg)
        if not search_filter or search_filter == 'web':
            min_start_date = arrow.get('2004-01-01')
        else:
            min_start_date = arrow.get('2008-01-01')
        max_end_date = arrow.now()
        # handle special case: "daily" granularity for full (unspecified) time span
        if granularity == 'daily' and not start_date and not end_date:
            return min_start_date, max_end_date
        if start_date:
            start_date = arrow.get(start_date).replace(day=1)
            if start_date < min_start_date:
                msg = 'Earliest available Google Trends data is for {}'.format(
                    min_start_date)
                raise ValueError(msg)
            if not end_date:
                end_date = max_end_date
        if end_date:
            end_date = arrow.get(end_date).replace(day=1)
            if end_date > max_end_date:
                msg = 'Last available Google Trends data is for {} (today)'.format(
                    max_end_date)
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
