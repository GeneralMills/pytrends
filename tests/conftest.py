import pytest
from responses import RequestsMock


@pytest.fixture
def mocked_responses():
    requests_mock = RequestsMock(
        assert_all_requests_are_fired=True
    )
    with requests_mock as mocked_responses:
        yield mocked_responses
