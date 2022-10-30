from dataclasses import dataclass
from unittest.mock import ANY

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from pytrends.request import TrendReq


@dataclass
class ExpectedResult:
    """
    Small class to reduce boilerplate code in the tests that compares a `pd.DataFrame`.
    Instead of compare against a whole `pd.DataFrame` compares it with a given length, head
    and tail.
    The length of head and tail is 3 by default but you can change it.
    """
    length: int
    df_head: pd.DataFrame
    df_tail: pd.DataFrame
    head_tail_length: int = 3

    def assert_equals(self, df_result: pd.DataFrame):
        assert len(df_result) == self.length
        assert_frame_equal(df_result.head(self.head_tail_length), self.df_head)
        assert_frame_equal(df_result.tail(self.head_tail_length), self.df_tail)


def build_interest_over_time_df(records, dates):
    """
    Creates a `pd.DataFrame` with the same shape as a pytrends `interest_over_time` result.
    `records` is a dict of keyword -> results.
    If `records` doesn't include the key 'isPartial' then `[False]` will be used.
    Example:

        In [6]: build_interest_over_time_df(
           ...:     {'kw1': [1, 2, 3], 'kw2': [10, 20, 30]},
           ...:     dates=['2021-01-01', '2021-01-02', '2021-01-03']
           ...: )
        Out[6]:
                    kw1  kw2  isPartial
        date
        2021-01-01    1   10      False
        2021-01-02    2   20      False
        2021-01-03    3   30      False
    """
    records = records.copy()
    if 'isPartial' not in records:
        records['isPartial'] = [False]
    return pd.DataFrame(
        records,
        index=pd.Index(
            data=pd.to_datetime(dates),
            name='date'
        )
    )


@pytest.mark.vcr
def test_initial_data():
    """Should use same values as in the documentation."""
    pytrend = TrendReq()
    result = {
        "hl": pytrend.hl,
        "tz": pytrend.tz,
        "geo": pytrend.geo,
        "cookie_NID": bool(pytrend.cookies["NID"]),
    }
    expected = {"hl": "en-US", "tz": 360, "geo": "", "cookie_NID": True}
    assert result == expected


@pytest.mark.vcr
def test_build_payload():
    """Should return the widgets to get data."""
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=["pizza", "bagel"])
    expected = {
        "hl": "en-US",
        "tz": 360,
        "req": (
            '{"comparisonItem": ['
            '{"keyword": "pizza", "time": "today 5-y", "geo": ""}, '
            '{"keyword": "bagel", "time": "today 5-y", "geo": ""}'
            '], "category": 0, "property": ""}'
        ),
    }
    assert pytrend.token_payload == expected


@pytest.mark.vcr
def test_tokens():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=["pizza", "bagel"], timeframe='2021-01-01 2021-12-31')
    expected = [
        {
            "request": {
                "restriction": {
                    "geo": {},
                    "time": "2021-01-01 2021-12-31",
                    "originalTimeRangeForExploreUrl": "2021-01-01 2021-12-31",
                    "complexKeywordsRestriction": {
                        "keyword": [{"type": "BROAD", "value": "pizza"}]
                    },
                },
                "keywordType": "QUERY",
                "metric": ["TOP", "RISING"],
                "trendinessSettings": {"compareTime": "2020-01-02 2020-12-31"},
                "requestOptions": {"property": "", "backend": "IZG", "category": 0},
                "language": "en",
                "userCountryCode": "ES",
                "userConfig": {"userType": "USER_TYPE_SCRAPER"},
            },
            # We don't care if the help dialog changes.
            "helpDialog": ANY,
            "color": "PALETTE_COLOR_1",
            "keywordName": "pizza",
            # The token will change in every request.
            "token": ANY,
            "id": "RELATED_QUERIES_0",
            "type": "fe_related_searches",
            "title": "Related queries",
            "template": "fe",
            "embedTemplate": "fe_embed",
            "version": "1",
            "isLong": False,
            "isCurated": False,
        },
        {
            "request": {
                "restriction": {
                    "geo": {},
                    "time": "2021-01-01 2021-12-31",
                    "originalTimeRangeForExploreUrl": "2021-01-01 2021-12-31",
                    "complexKeywordsRestriction": {
                        "keyword": [{"type": "BROAD", "value": "bagel"}]
                    },
                },
                "keywordType": "QUERY",
                "metric": ["TOP", "RISING"],
                "trendinessSettings": {"compareTime": "2020-01-02 2020-12-31"},
                "requestOptions": {"property": "", "backend": "IZG", "category": 0},
                "language": "en",
                "userCountryCode": "ES",
                "userConfig": {"userType": "USER_TYPE_SCRAPER"},
            },
            # We don't care if the help dialog changes.
            "helpDialog": ANY,
            "color": "PALETTE_COLOR_2",
            "keywordName": "bagel",
            # The token will change in every request.
            "token": ANY,
            "id": "RELATED_QUERIES_1",
            "type": "fe_related_searches",
            "title": "Related queries",
            "template": "fe",
            "embedTemplate": "fe_embed",
            "version": "1",
            "isLong": False,
            "isCurated": False,
        },
    ]
    assert pytrend.related_queries_widget_list == expected


@pytest.mark.vcr
def test_interest_over_time():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'], timeframe='2021-01-01 2021-12-31')
    df_result = pytrend.interest_over_time()
    expected_result = ExpectedResult(
        length=52,
        df_head=build_interest_over_time_df({
            'pizza': [81, 79, 79],
            'bagel': [2, 2, 2]
        }, dates=['2021-01-03', '2021-01-10', '2021-01-17']),
        df_tail=build_interest_over_time_df({
            'pizza': [83, 83, 100],
            'bagel': [2, 2, 2]
        }, dates=['2021-12-12', '2021-12-19', '2021-12-26'])
    )
    expected_result.assert_equals(df_result)


@pytest.mark.vcr
def test_interest_over_time_images():
    pytrend = TrendReq()
    pytrend.build_payload(
        kw_list=['pizza', 'bagel'],
        gprop='images',
        timeframe='2021-01-01 2021-12-31'
    )
    df_result = pytrend.interest_over_time()
    expected_result = ExpectedResult(
        length=52,
        df_head=build_interest_over_time_df({
            'pizza': [91, 96, 91],
            'bagel': [4, 4, 3]
        }, dates=['2021-01-03', '2021-01-10', '2021-01-17']),
        df_tail=build_interest_over_time_df({
            'pizza': [84, 80, 84],
            'bagel': [3, 3, 3],
        }, dates=['2021-12-12', '2021-12-19', '2021-12-26'])
    )
    expected_result.assert_equals(df_result)


@pytest.mark.vcr
def test_interest_over_time_news():
    pytrend = TrendReq()
    pytrend.build_payload(
        kw_list=['pizza', 'bagel'],
        gprop='news',
        timeframe='2021-01-01 2021-12-31'
    )
    df_result = pytrend.interest_over_time()
    expected_result = ExpectedResult(
        length=52,
        df_head=build_interest_over_time_df({
            'pizza': [53, 60, 65],
            'bagel': [0, 0, 2]
        }, dates=['2021-01-03', '2021-01-10', '2021-01-17']),
        df_tail=build_interest_over_time_df({
            'pizza': [62, 64, 70],
            'bagel': [0, 7, 3]
        }, dates=['2021-12-12', '2021-12-19', '2021-12-26'])
    )
    expected_result.assert_equals(df_result)


@pytest.mark.vcr
def test_interest_over_time_youtube():
    pytrend = TrendReq()
    pytrend.build_payload(
        kw_list=['pizza', 'bagel'],
        gprop='youtube',
        timeframe='2021-01-01 2021-12-31'
    )
    df_result = pytrend.interest_over_time()
    expected_result = ExpectedResult(
        length=52,
        df_head=build_interest_over_time_df({
            'pizza': [93, 92, 85],
            'bagel': [1, 1, 1]
        }, dates=['2021-01-03', '2021-01-10', '2021-01-17']),
        df_tail=build_interest_over_time_df({
            'pizza': [72, 73, 81],
            'bagel': [1, 1, 1]
        }, dates=['2021-12-12', '2021-12-19', '2021-12-26'])
    )
    expected_result.assert_equals(df_result)
