import pandas.api.types as ptypes
import pytest

from pytrends.request import TrendReq
from pytrends.exceptions import TooManyRequestsError


too_many_requests_mark = pytest.mark.xfail(
    reason="Google may return 429 whenever they want",
    raises=TooManyRequestsError
)


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
