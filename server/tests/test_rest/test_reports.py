import datetime

import pytest 

from shir_connect.services.app import app
import shir_connect.services.reports as rep
import shir_connect.services.utils as utils
from .utils import run_url_tests

CLIENT = app.test_client()

def run_report_tests(url):
    run_url_tests(url, client=CLIENT, access=['report'])

def test_report_event_count():
    run_report_tests('/service/report/events/count')

def test_member_demographics():
    run_report_tests('/service/report/members/demographics')

def test_new_member_demographics():
    run_report_tests('/service/report/members/demographics?only=new_members')

def test_member_locations():
    run_report_tests('/service/report/members/locations')

def test_new_members_cont():
    run_report_tests('/service/report/members/new/count')

def test_member_locations():
    run_report_tests('/service/report/members/new?limit=30')

def test_households_by_year():
    run_report_tests('/service/report/members/households/count?years=5')

def test_resignations_by_year():
    run_report_tests('/service/report/members/households/count?tally=resignations')

def test_households_by_type():
    run_report_tests('/service/report/members/households/type')

def test_resignations_by_type():
    run_report_tests('/service/report/members/resignations/type')

def test_get_quarters(monkeypatch):
    fake_date = datetime.datetime(2019,4,2)
    class patched_datetime(datetime.datetime): pass
    monkeypatch.setattr(patched_datetime, "now", lambda: fake_date)
    quarters = rep.get_quarters()
    assert quarters == [(2018, 4), (2019, 1), (2019, 2), (2019, 3)]

def test_get_quarterly_events():
    class FakeEvents:
        def __init__(self):
            pass
        def event_group_counts(self, start, end):
            return {'All': 5, 'Birds': 3, 'Camels': 2}

    event_manager = FakeEvents()
    quarters = [(2018, 3), (2018, 4), (2019, 1)]
    response = rep.get_quarterly_event_counts(quarters, event_manager)
    assert set(response.keys()) == {'2018-Q3', '2018-Q4', '2019-Q1'}

def test_get_quarterly_new_members():
    class FakeMembers:
        def __init__(self):
            pass

        def count_new_members(self, start, end):
            return 100
        
        def count_new_households(self, start, end):
            return 100

    members = FakeMembers()
    quarters = [(2018, 3), (2018, 4), (2019, 1)]
    response = rep.get_quarterly_new_members(quarters, members)
    assert set(response.keys()) == {'2018-Q3', '2018-Q4', '2019-Q1'}

def test_common_locations():
    response = {'all_members': [{'location': 'All', 'total': 175},
                                {'location': 'Bird Town', 'total': 50},
                                {'location': 'Barkville', 'total': 25},
                                {'location': 'Portland', 'total': 50},
                                {'location': 'Fishville', 'total': 25},
                                {'location': 'Other', 'total': 25}],
                'new_members': [{'location': 'All', 'total': 150},
                                {'location': 'Bird Town', 'total': 50},
                                {'location': 'Barkland', 'total': 25},
                                {'location': 'Fishville', 'total': 25},
                                {'location': 'Chicago', 'total': 25},
                                {'location': 'Other', 'total': 25}],
                'other_members': [{'location': 'All', 'total': 150},
                                {'location': 'Bird Town', 'total': 50},
                                {'location': 'Barkland', 'total': 25},
                                {'location': 'Fishville', 'total': 25},
                                {'location': 'Portland', 'total': 25},
                                {'location': 'Other', 'total': 25}]}
    common_locations = rep._find_common_locations(response)
    assert common_locations == {'Bird Town', 'Fishville'}

def test_build_locations_pct():
    response = {'all_members': [{'location': 'All', 'total': 175},
                                {'location': 'Bird Town', 'total': 50},
                                {'location': 'Barkville', 'total': 25},
                                {'location': 'Portland', 'total': 50},
                                {'location': 'Fishville', 'total': 25},
                                {'location': 'Other', 'total': 25}],
                'new_members': [{'location': 'All', 'total': 150},
                                {'location': 'Bird Town', 'total': 50},
                                {'location': 'Barkland', 'total': 25},
                                {'location': 'Fishville', 'total': 25},
                                {'location': 'Chicago', 'total': 25},
                                {'location': 'Other', 'total': 25}],
                'other_members': [{'location': 'All', 'total': 150},
                                {'location': 'Bird Town', 'total': 50},
                                {'location': 'Barkland', 'total': 25},
                                {'location': 'Fishville', 'total': 25},
                                {'location': 'Portland', 'total': 25},
                                {'location': 'Other', 'total': 25}]}
    
    percentages = rep.build_locations_pct(response)
    for key in percentages:
        assert set(percentages[key].keys()) == {'Bird Town', 'Fishville',
                                                'Other'}

        total = rep._get_list_key(response[key], 'location', 'All')['total']
        for k in percentages[key]:
            if k != 'Other':
                count = rep._get_list_key(response[key], 'location', k)['total']
                assert percentages[key][k] == count/total
        total_pct = sum([percentages[key][k] for k in percentages[key]])
        assert total_pct < 1.0000000001
        assert total_pct > 0.9999999999
