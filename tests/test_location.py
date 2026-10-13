import pytest
from pipeline.location import location_matches as m, countries_in, is_remote


@pytest.mark.parametrize("loc,query,expected", [
    ("Lausanne, Vaud", "USA", False),          # the original bug
    ("Zurich", "USA", False),
    ("New York, NY", "USA", True),
    ("San Francisco, CA", "us", True),
    ("Springfield, IL", "USA", True),
    ("Remote - US", "USA", True),
    ("Remote - US", "India", False),
    ("Bangalore, Karnataka", "India", True),
    ("UK - London", "UK", True),
    ("London", "United Kingdom", True),
    ("Berlin", "Germany", True),
    ("München", "Germany", True),
    ("Berlin", "ber", True),
    ("Lausanne", "usa", False),
    ("", "USA", False),
    ("Berlin", "", True),
])
def test_location_matches(loc, query, expected):
    assert m(loc, query) == expected


def test_worldwide_remote_respects_checkbox():
    assert m("Remote", "USA", include_remote=True)
    assert not m("Remote", "USA", include_remote=False)


def test_job_type_remote_without_location():
    assert m("", "USA", job_type="remote")
    assert not m("Berlin", "USA", job_type="remote")


def test_remote_query():
    assert m("Remote", "remote")
    assert m("Berlin", "remote", job_type="remote")
    assert not m("Berlin", "remote")


def test_helpers():
    assert countries_in("Lausanne, Vaud") == {"ch"}
    assert is_remote("Remote")