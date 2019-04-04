import datetime

import pytest 

import shir_connect.services.reports as rep

def test_get_quarters(monkeypatch):
    fake_date = datetime.datetime(2019,4,2)
    class patched_datetime(datetime.datetime): pass
    monkeypatch.setattr(patched_datetime, "now", lambda: fake_date)
    quarters = rep.get_quarters()
    assert quarters == [(2018, 3), (2018, 4), (2019, 1), (2019, 2)]
