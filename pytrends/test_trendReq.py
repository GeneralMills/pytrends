import pandas.api.types as ptypes
import pytest

from pytrends.request import TrendReq
from pytrends.exceptions import TooManyRequestsError


too_many_requests_mark = pytest.mark.xfail(
    reason="Google may return 429 whenever they want",
    raises=TooManyRequestsError
)


@too_many_requests_mark
def test_get_data():
    """Should use same values as in the documentation"""
    pytrend = TrendReq()
    assert pytrend.hl == 'en-US'
    assert pytrend.tz == 360
    assert pytrend.geo == ''
    assert bool(pytrend.cookies['NID']) is True


@too_many_requests_mark
def test_build_payload():
    """Should return the widgets to get data"""
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'])
    assert pytrend.token_payload is not None


@too_many_requests_mark
def test_tokens():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'])
    assert pytrend.related_queries_widget_list is not None


@too_many_requests_mark
def test_interest_over_time():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'])
    result = pytrend.interest_over_time()
    assert result is not None


@too_many_requests_mark
def test_interest_over_time_images():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'], gprop='images')
    result = pytrend.interest_over_time()
    assert result is not None


@too_many_requests_mark
def test_interest_over_time_news():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'], gprop='news')
    result = pytrend.interest_over_time()
    assert result is not None


@too_many_requests_mark
def test_interest_over_time_youtube():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'], gprop='youtube')
    result = pytrend.interest_over_time()
    assert result is not None


@too_many_requests_mark
def test_interest_over_time_froogle():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'], gprop='froogle')
    result = pytrend.interest_over_time()
    assert result is not None


@too_many_requests_mark
def test_interest_over_time_bad_gprop():
    pytrend = TrendReq()
    with pytest.raises(ValueError):
        pytrend.build_payload(kw_list=['pizza', 'bagel'], gprop=' ')


@too_many_requests_mark
def test_interest_by_region():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'])
    result = pytrend.interest_by_region()
    assert result is not None


@too_many_requests_mark
def test_interest_by_region_city_resolution():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'])
    result = pytrend.interest_by_region(resolution='CITY')
    assert result is not None


@too_many_requests_mark
def test_related_topics():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'])
    result = pytrend.related_topics()
    assert result is not None


@too_many_requests_mark
def test_related_queries():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'])
    result = pytrend.related_queries()
    assert result is not None


@too_many_requests_mark
def test_trending_searches():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'])
    result = pytrend.trending_searches()
    assert result is not None


@too_many_requests_mark
def test_realtime_trending_searches():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'])
    result = pytrend.realtime_trending_searches(pn='IN')
    assert result is not None


@too_many_requests_mark
def test_request_args_passing_suggestions():
    requests_args = {'headers': {
        'User-Agent': 'pytrends',
    }}
    pytrend = TrendReq(requests_args=requests_args)
    pytrend.build_payload(kw_list=['bananas'])
    result = pytrend.suggestions('bananas')
    assert result is not None


@too_many_requests_mark
def test_request_args_passing_trending_searches():
    requests_args = {'headers': {
        'User-Agent': 'pytrends',
    }}
    pytrend = TrendReq(requests_args=requests_args)
    pytrend.build_payload(kw_list=['bananas'])
    result = pytrend.trending_searches()
    assert result is not None


@too_many_requests_mark
def test_top_charts():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'])
    result = pytrend.top_charts(date=2019)
    assert result is not None


@too_many_requests_mark
def test_suggestions():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'])
    result = pytrend.suggestions(keyword='pizza')
    assert result is not None


@too_many_requests_mark
def test_ispartial_dtype():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'])
    df = pytrend.interest_over_time()
    assert ptypes.is_bool_dtype(df.isPartial)


@too_many_requests_mark
def test_ispartial_dtype_timeframe_all():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['pizza', 'bagel'], timeframe='all')
    df = pytrend.interest_over_time()
    assert ptypes.is_bool_dtype(df.isPartial)
