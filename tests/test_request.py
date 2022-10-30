from dataclasses import dataclass
from unittest.mock import ANY
import re

import pandas as pd
import pytest
import responses
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


@pytest.mark.vcr
def test_interest_over_time_froogle():
    pytrend = TrendReq()
    pytrend.build_payload(
        kw_list=['pizza', 'bagel'],
        gprop='froogle',
        timeframe='2021-01-01 2021-12-31'
    )
    df_result = pytrend.interest_over_time()
    expected_result = ExpectedResult(
        length=52,
        df_head=build_interest_over_time_df({
            'pizza': [87, 80, 87],
            'bagel': [4, 4, 3]
        }, dates=['2021-01-03', '2021-01-10', '2021-01-17']),
        df_tail=build_interest_over_time_df({
            'pizza': [80, 82, 99],
            'bagel': [1, 0, 2]
        }, dates=['2021-12-12', '2021-12-19', '2021-12-26'])
    )
    expected_result.assert_equals(df_result)


@pytest.mark.vcr
def test_interest_over_time_bad_gprop():
    pytrend = TrendReq()
    expected_message = re.compile(r'^gprop must be.+$')
    with pytest.raises(ValueError, match=expected_message):
        pytrend.build_payload(kw_list=['pizza', 'bagel'], gprop=' ')


@pytest.mark.vcr
def test_interest_by_region():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'], timeframe='2021-01-01 2021-12-31')
    df_result = pytrend.interest_by_region()
    # Both head and tail have all 0's in both values, sort the result to test more meaningful values
    df_result = df_result.sort_values(by=['bagel', 'pizza', 'geoName'], ascending=False)
    expected_result = ExpectedResult(
        length=250,
        df_head=pd.DataFrame({
            'pizza': [93, 94, 96],
            'bagel': [7, 6, 4],
        }, index=pd.Index(['Singapore', 'Hong Kong', 'Taiwan'], name='geoName')),
        df_tail=pd.DataFrame({
            'pizza': [0, 0, 0],
            'bagel': [0, 0, 0],
        }, index=pd.Index(['Algeria', 'Albania', 'Afghanistan'], name='geoName'))
    )
    expected_result.assert_equals(df_result)


@pytest.mark.vcr
def test_interest_by_region_city_resolution():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'], timeframe='2021-01-01 2021-12-31')
    df_result = pytrend.interest_by_region(resolution='CITY')
    # Both head and tail have all 0's in both values, sort the result to test more meaningful values
    df_result = df_result.sort_values(by=['bagel', 'pizza', 'geoName'], ascending=False)
    expected_result = ExpectedResult(
        length=200,
        df_head=pd.DataFrame({
            'pizza': [95, 97, 97],
            'bagel': [5, 3, 3],
        }, index=pd.Index(['Grafton', 'Raleigh', 'Philadelphia'], name='geoName')),
        df_tail=pd.DataFrame({
            'pizza': [0, 0, 0],
            'bagel': [0, 0, 0],
        }, index=pd.Index(['Ahmedabad', 'Abu Dhabi', 'Aarhus'], name='geoName'))
    )
    expected_result.assert_equals(df_result)


# FIXME: With more than one term the result is always an empty dict.
# In the web we can get related topics using ['Torvalds', 'Dijkstra'] but not here, something's wrong.
@pytest.mark.vcr
def test_related_topics_result_keys():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza'], timeframe='2021-01-01 2021-12-31')
    df_result = pytrend.related_topics()
    # Since the result dict contains pd.DataFrame's we can't create an expected dict and compare.
    # Fuck you Pandas and your "oops, the truth value of a DataFrame is ambiguous, let's error out".
    assert set(df_result.keys()) == {'pizza'}
    df_result = df_result['pizza']
    assert set(df_result.keys()) == {'top', 'rising'}


@pytest.mark.vcr
def test_related_topics_result_top():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza'], timeframe='2021-01-01 2021-12-31')
    df_result = pytrend.related_topics()['pizza']['top']
    expected_result = ExpectedResult(
        length=22,
        df_head=pd.DataFrame({
            'value': [100, 25, 14],
            'formattedValue': ['100', '25', '14'],
            'hasData': [True, True, True],
            'link': [
                '/trends/explore?q=/m/0663v&date=2021-01-01+2021-12-31',
                '/trends/explore?q=/m/09cfq&date=2021-01-01+2021-12-31',
                '/trends/explore?q=/m/03clwm&date=2021-01-01+2021-12-31',
            ],
            'topic_mid': ['/m/0663v', '/m/09cfq', '/m/03clwm'],
            'topic_title': ['Pizza', 'Pizza Hut', "Domino's Pizza"],
            'topic_type': ['Dish', 'Restaurant company', 'Restaurant company']
        }),
        df_tail=pd.DataFrame({
            'value': [0, 0, 0],
            'formattedValue': ['<1', '<1', '<1'],
            'hasData': [True, True, True],
            'link': [
                '/trends/explore?q=/g/11g6qhxwmd&date=2021-01-01+2021-12-31',
                '/trends/explore?q=/g/11b7c9w1y6&date=2021-01-01+2021-12-31',
                '/trends/explore?q=/m/09nghg&date=2021-01-01+2021-12-31',
            ],
            'topic_mid': ['/g/11g6qhxwmd', '/g/11b7c9w1y6', '/m/09nghg'],
            'topic_title': ['Ooni', "Roman's Pizza", 'Sam Goody'],
            'topic_type': ['Topic', 'Topic', 'Retail company']
        }, index=pd.Index([19, 20, 21]))
    )
    expected_result.assert_equals(df_result)


@pytest.mark.vcr
def test_related_topics_result_rising():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza'], timeframe='2021-01-01 2021-12-31')
    df_result = pytrend.related_topics()['pizza']['rising']
    df_expected = pd.DataFrame({
        'value': [11800, 170, 90, 80],
        'formattedValue': ['Breakout', '+170%', '+90%', '+80%'],
        'link': [
            '/trends/explore?q=/m/09nghg&date=2021-01-01+2021-12-31',
            '/trends/explore?q=/m/0gwh_4&date=2021-01-01+2021-12-31',
            '/trends/explore?q=/g/11g6qhxwmd&date=2021-01-01+2021-12-31',
            '/trends/explore?q=/m/02hvyj&date=2021-01-01+2021-12-31',
        ],
        'topic_mid': ['/m/09nghg', '/m/0gwh_4', '/g/11g6qhxwmd', '/m/02hvyj'],
        'topic_title': ['Sam Goody', 'Detroit-style pizza', 'Ooni', 'Mystic Pizza'],
        'topic_type': ['Retail company', 'Food', 'Topic', '1988 film']
    })
    assert_frame_equal(df_result, df_expected)


@pytest.mark.vcr
def test_related_queries_result_keys():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'], timeframe='2021-01-01 2021-12-31')
    df_result = pytrend.related_queries()
    assert set(df_result.keys()) == {'pizza', 'bagel'}
    df_result_pizza = df_result['pizza']
    assert set(df_result_pizza.keys()) == {'top', 'rising'}
    df_result_bagel = df_result['bagel']
    assert set(df_result_bagel.keys()) == {'top', 'rising'}


@pytest.mark.vcr
def test_related_queries_result_top():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'], timeframe='2021-01-01 2021-12-31')
    df_result = pytrend.related_queries()

    expected_pizza = ExpectedResult(
        length=25,
        df_head=pd.DataFrame({
            'query': ['pizza hut', 'pizza near me', 'pizza pizza near me'],
            'value': [100, 64, 64]
        }),
        df_tail=pd.DataFrame({
            'query': ['cheese pizza', 'little caesars', 'pizza little caesars'],
            'value': [5, 5, 5]
        }, index=pd.Index([22, 23, 24]))
    )
    expected_pizza.assert_equals(df_result['pizza']['top'])

    expected_bagel = ExpectedResult(
        length=25,
        df_head=pd.DataFrame({
            'query': ['the bagel', 'bagel me', 'bagel near me'],
            'value': [100, 99, 93]
        }),
        df_tail=pd.DataFrame({
            'query': ['coffee meets bagel', 'bagel bread', 'what a bagel'],
            'value': [23, 22, 21]
        }, index=pd.Index([22, 23, 24]))
    )
    expected_bagel.assert_equals(df_result['bagel']['top'])


@pytest.mark.vcr
def test_related_queries_result_rising():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'], timeframe='2021-01-01 2021-12-31')
    df_result = pytrend.related_queries()

    expected_pizza = ExpectedResult(
        length=11,
        df_head=pd.DataFrame({
            'query': ['licorice pizza', 'history of pizza', 'stoned pizza'],
            'value': [8850, 400, 300]
        }),
        df_tail=pd.DataFrame({
            'query': ['pizza cosy', 'incredible pizza', 'andys pizza'],
            'value': [50, 50, 50]
        }, index=pd.Index([8, 9, 10]))
    )
    expected_pizza.assert_equals(df_result['pizza']['rising'])

    expected_bagel = ExpectedResult(
        length=19,
        df_head=pd.DataFrame({
            'query': ['rover bagel', 'kettlemans bagel', 'bagel karen'],
            'value': [400, 250, 170]
        }),
        df_tail=pd.DataFrame({
            'query': ['brugger bagel', 'the bagel nook', 'best bagel near me'],
            'value': [50, 40, 40]
        }, index=pd.Index([16, 17, 18]))
    )
    expected_bagel.assert_equals(df_result['bagel']['rising'])


@pytest.mark.vcr
def test_trending_searches():
    pytrend = TrendReq()
    # trending_searches doesn't need to call build_payload.
    df_result = pytrend.trending_searches()
    # NOTE: This expected result needs to be rebuilt from scratch every time the cassette is rewritten.
    # They're time-dependent.
    expected_result = ExpectedResult(
        length=20,
        df_head=pd.DataFrame({0: ['Michigan football', 'Seoul', 'Penn State football']}),
        df_tail=pd.DataFrame(
            {0: ['Myositis', 'Dogecoin', 'Deion Sanders']},
            index=pd.Index([17, 18, 19])
        )
    )
    expected_result.assert_equals(df_result)


@pytest.mark.vcr
def test_realtime_trending_searches():
    pytrend = TrendReq()
    # realtime_trending_searches doesn't need to call build_payload.
    df_result = pytrend.realtime_trending_searches()
    # NOTE: This expected result needs to be rebuilt from scratch every time the cassette is rewritten.
    # They're time-dependent.
    # NOTE: The result returned by this function is a monster.
    # Strings of almost 200 characters, lists of strings, lists of lists of strings...
    # Rebuilding a full 3-head-tail result from scratch is a chore, with a single record for head
    # and tail is more than enough.
    expected_result = ExpectedResult(
        length=131,
        head_tail_length=1,
        df_head=pd.DataFrame({
            'title': [
                ('Michigan Wolverines football, '
                 'Michigan State Spartans football, '
                 'American football, '
                 'Big Ten Conference'),
            ],
            'entityNames': [
                [
                    'Michigan Wolverines football',
                    'Michigan State Spartans football',
                    'American football',
                    'Big Ten Conference'
                ],
            ]
        }),
        df_tail=pd.DataFrame({
            'title': [
                ('Florida Gulf Coast University, '
                 'ASUN Conference, '
                 'Kennesaw State University, '
                 'Cross country running, '
                 'Volleyball, '
                 "Florida Gulf Coast Eagles men's basketball, "
                 'NCAA Division I')
            ], 'entityNames': [
                [
                    'Florida Gulf Coast University',
                    'ASUN Conference',
                    'Kennesaw State University',
                    'Cross country running',
                    'Volleyball',
                    "Florida Gulf Coast Eagles men's basketball",
                    'NCAA Division I'
                ]
            ]
        }, index=pd.Index([130]))
    )
    expected_result.assert_equals(df_result)


@pytest.mark.vcr
def test_top_charts():
    pytrend = TrendReq()
    # top_chars doesn't need to call build_payload.
    df_result = pytrend.top_charts(date=2021)
    df_expected = pd.DataFrame({
        'title': [
            'Australia vs India',
            'India vs England',
            'IPL',
            'NBA',
            'Euro 2021',
            'Copa América',
            'India vs New Zealand',
            'T20 World Cup',
            'Squid Game',
            'DMX'
        ],
        'exploreQuery': ['', '', '', '', '', 'Copa America', '', '', '', '']
    })
    assert_frame_equal(df_result, df_expected)


@pytest.mark.vcr
def test_suggestions():
    pytrend = TrendReq()
    # suggestions doesn't need to call build_payload.
    result = pytrend.suggestions(keyword='pizza')
    expected = [
        {'mid': '/m/0663v', 'title': 'Pizza', 'type': 'Dish'},
        {'mid': '/g/11k19hmrkk', 'title': 'Licorice Pizza', 'type': '2021 film'},
        {'mid': '/m/0dfxdnc', 'title': 'Pizza dough', 'type': 'Food'},
        {'mid': '/g/11hdxfw7c0', 'title': 'history of pizza', 'type': 'Food'},
        {'mid': '/g/11fl7dydwb', 'title': 'Pizza Oven', 'type': 'Topic'},
    ]
    assert result == expected


@responses.activate
def test_request_args_passing():
    responses.add(
        url='https://trends.google.com/?geo=US',
        method='GET',
        match=[responses.matchers.header_matcher({'User-Agent': 'pytrends'})]
    )
    responses.add(
        url='https://trends.google.com/trends/hottrends/visualize/internal/data',
        method='GET',
        match=[responses.matchers.header_matcher({'User-Agent': 'pytrends'})],
        json={
            'united_states': ['term 1', 'term 2']
        }
    )
    requests_args = {'headers': {
        'User-Agent': 'pytrends',
    }}
    pytrend = TrendReq(requests_args=requests_args)
    pytrend.trending_searches()
