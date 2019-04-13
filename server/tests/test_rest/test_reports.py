import datetime

import pytest 

import shir_connect.configuration as conf
from shir_connect.services.app import app
import shir_connect.services.reports as rep
from shir_connect.database.user_management import UserManagement
import shir_connect.services.utils as utils

CLIENT = app.test_client()

def run_url_tests(url):
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)

    # User must be authenticated
    response = CLIENT.get(url)
    assert response.status_code == 401

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username=conf.TEST_USER,
        password=conf.TEST_PASSWORD
    ))
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')

    # The user must have access to the reports module
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access(conf.TEST_USER, ['report'])
    
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 200

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert not user

def test_report_event_count():
    run_url_tests('/service/report/events/count')

def test_member_demographics():
    run_url_tests('/service/report/members/demographics')

def test_new_member_demographics():
    run_url_tests('/service/report/members/demographics?only=new_members')

def test_member_locations():
    run_url_tests('/service/report/members/locations')

def test_new_members_cont():
    run_url_tests('/service/report/members/new/count')

def test_member_locations():
    run_url_tests('/service/report/members/new?limit=30')

def test_households_by_year():
    run_url_tests('/service/report/members/households/count?years=5')

def test_households_by_type():
    run_url_tests('/service/report/members/households/type')

def test_get_quarters(monkeypatch):
    fake_date = datetime.datetime(2019,4,2)
    class patched_datetime(datetime.datetime): pass
    monkeypatch.setattr(patched_datetime, "now", lambda: fake_date)
    quarters = rep.get_quarters()
    assert quarters == [(2018, 3), (2018, 4), (2019, 1), (2019, 2)]

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

    members = FakeMembers()
    quarters = [(2018, 3), (2018, 4), (2019, 1)]
    response = rep.get_quarterly_new_members(quarters, members)
    assert set(response.keys()) == {'2018-Q3', '2018-Q4', '2019-Q1'}
