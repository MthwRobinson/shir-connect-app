import datetime

import pytest 

import shir_connect.services.reports as rep

def test_get_quarters(monkeypatch):
    fake_date = datetime.datetime(2019,4,2)
    class patched_datetime(datetime.datetime): pass
    monkeypatch.setattr(patched_datetime, "now", lambda: fake_date)
    quarters = rep.get_quarters()
    assert quarters == [(2018, 3), (2018, 4), (2019, 1), (2019, 2)]

def test_get_quarter_events():
    class FakeEvents:
        def __init__(self):
            pass
        def event_group_counts(self, start, end):
            return {'All': 5, 'Birds': 3, 'Camels': 2}

    event_manager = FakeEvents()
    quarters = [(2018, 3), (2018, 4), (2019, 1)]
    response = rep.get_quarter_event_counts(quarters, event_manager)
    assert set(response.keys()) == {'2018-Q3', '2018-Q4', '2019-Q1'}
