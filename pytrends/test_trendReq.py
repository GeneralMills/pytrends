from unittest import TestCase
import pandas.api.types as ptypes

from pytrends.request import TrendReq


class TestTrendReq(TestCase):

    def test__get_data(self):
        """Should use same values as in the documentation"""
        pytrend = TrendReq()
        self.assertEqual(pytrend.hl, 'en-US')
        self.assertEqual(pytrend.tz, 360)
        self.assertEqual(pytrend.geo, '')
        self.assertTrue(pytrend.cookies['NID'])

    def test_build_payload(self):
        """Should return the widgets to get data"""
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'])
        self.assertIsNotNone(pytrend.token_payload)

    def test__tokens(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'])
        self.assertIsNotNone(pytrend.related_queries_widget_list)

    def test_interest_over_time(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'])
        self.assertIsNotNone(pytrend.interest_over_time())

    def test_interest_over_time_images(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'], gprop='images')
        self.assertIsNotNone(pytrend.interest_over_time())

    def test_interest_over_time_news(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'], gprop='news')
        self.assertIsNotNone(pytrend.interest_over_time())

    def test_interest_over_time_youtube(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'], gprop='youtube')
        self.assertIsNotNone(pytrend.interest_over_time())

    def test_interest_over_time_froogle(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'], gprop='froogle')
        self.assertIsNotNone(pytrend.interest_over_time())

    def test_interest_over_time_bad_gprop(self):
        pytrend = TrendReq()
        with self.assertRaises(ValueError):
            pytrend.build_payload(kw_list=['pizza', 'bagel'], gprop=' ')

    def test_interest_by_region(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'])
        self.assertIsNotNone(pytrend.interest_by_region())

    def test_related_topics(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'])
        self.assertIsNotNone(pytrend.related_topics())

    def test_related_queries(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'])
        self.assertIsNotNone(pytrend.related_queries())

    def test_trending_searches(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'])
        self.assertIsNotNone(pytrend.trending_searches())

    def test_realtime_trending_searches(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'])
        self.assertIsNotNone(pytrend.realtime_trending_searches(pn='IN'))

    def test_top_charts(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'])
        self.assertIsNotNone(pytrend.top_charts(date=2019))

    def test_suggestions(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'])
        self.assertIsNotNone(pytrend.suggestions(keyword='pizza'))

    def test_ispartial_dtype(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'])
        df = pytrend.interest_over_time()
        assert ptypes.is_bool_dtype(df.isPartial)

    def test_ispartial_dtype_timeframe_all(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'],
                              timeframe='all')
        df = pytrend.interest_over_time()
        assert ptypes.is_bool_dtype(df.isPartial)
