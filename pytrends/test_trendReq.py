from unittest import TestCase

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

    def test_interest_by_country_world(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'])
        self.assertIsNotNone(pytrend.interest_by_region())

    def test_interest_by_badregion(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'])
        with self.assertRaises(ValueError):
            pytrend.interest_by_region(resolution='BADREGION')

    def test_interest_by_dma(self):
        # DMA is only available for US and US states (subregions).
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'])
        with self.assertRaises(ValueError):
            pytrend.interest_by_region(resolution='DMA')

    def test_interest_by_subregion(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'])
        self.assertIsNotNone(pytrend.interest_by_region(resolution='REGION'))

    def test_interest_by_city(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'])
        self.assertIsNotNone(pytrend.interest_by_region(resolution='CITY'))

    def test_interest_by_country_us(self):
        # Interest by country (default resolution) only works for world.
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'], geo='US')
        with self.assertRaises(ValueError):
            pytrend.interest_by_region()

    def test_interest_by_dma_us(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'], geo='US')
        self.assertIsNotNone(pytrend.interest_by_region(resolution='DMA'))

    def test_interest_by_subregion_us(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'], geo='US')
        self.assertIsNotNone(pytrend.interest_by_region(resolution='REGION'))

    def test_interest_by_city_us(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'], geo='US')
        self.assertIsNotNone(pytrend.interest_by_region(resolution='CITY'))

    def test_interest_by_country_ca(self):
        # Interest by country (default resolution) only works for world.
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'], geo='CA')
        with self.assertRaises(ValueError):
            pytrend.interest_by_region()

    def test_interest_by_subregion_ca(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'], geo='CA')
        self.assertIsNotNone(pytrend.interest_by_region(resolution='REGION'))

    def test_interest_by_dma_ca(self):
        # DMA is only available for US and US states (subregions).
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'], geo='CA')
        with self.assertRaises(ValueError):
            pytrend.interest_by_region(resolution='DMA')

    def test_interest_by_city_ca(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'], geo='CA')
        self.assertIsNotNone(pytrend.interest_by_region(resolution='CITY'))
        
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

    def test_top_charts(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'])
        self.assertIsNotNone(pytrend.top_charts(date=2019))

    def test_suggestions(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=['pizza', 'bagel'])
        self.assertIsNotNone(pytrend.suggestions(keyword='pizza'))
