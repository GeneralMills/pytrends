from unittest.mock import ANY

import pytest

from pytrends.request import TrendReq


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
