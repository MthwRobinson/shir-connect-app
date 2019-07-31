from io import StringIO
import json

import pandas as pd

from shir_connect.services.app import app
from shir_connect.database.user_management import UserManagement
import shir_connect.services.utils as utils
import shir_connect.configuration as conf

CLIENT = app.test_client()

def test_event():
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)

    # User must be authenticated
    url = '/service/event/7757038511'
    response = CLIENT.get(url)
    assert response.status_code == 401

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username=conf.TEST_USER,
        password=conf.TEST_PASSWORD
    ))
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')

    # User must have access to events
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access(conf.TEST_USER, ['events'])

    # Success
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 200
    assert type(response.json) == dict

    # Check to make sure the aggregates are present
    assert 'average_age' in response.json
    assert 'member_count' in response.json
    assert 'non_member_count' in response.json
    assert 'first_event_count' in response.json
    assert 'age_groups' in response.json
    for group in response.json['age_groups']:
        count = response.json['age_groups'][group]
        assert type(count) == int

    # Check to make sure the attendees are present
    for attendee in response.json['attendees']:
        'member_id' in attendee
        'first_name' in attendee
        'last_name' in attendee
        'name' in attendee
        'age' in attendee
        'is_member' in attendee

    url = '/service/event/8675309'
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 404
    assert type(response.json) == dict

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert user == None

def test_events():
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

    # User must be authenticated
    response = CLIENT.get('/service/events?limit=25')
    assert response.status_code == 401

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username=conf.TEST_USER,
        password=conf.TEST_PASSWORD
    ))
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')

    url = '/service/events?limit=25&page=2'
    url += '&sort=start_datetime&order=desc'
    url += '&q=a&start_datetime=1900-01-01'
    url += '&end_datetime=2100-01-01'
    user_management.update_access(conf.TEST_USER, ['events'])

    # Success!
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 200
    assert type(response.json['results']) == list
    assert len(response.json['results']) == 25
    assert 'count' in response.json
    assert 'pages' in response.json

    # Make sure input validation is working
    url = '/service/events?limit=30&page=2'
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 422

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert user == None

def test_event_locations():
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username=conf.TEST_USER,
        password=conf.TEST_PASSWORD
    ))
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')

    # User must have access to events
    url = '/service/events/locations'
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access(conf.TEST_USER, ['map'])

    # Success!
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 200
    assert type(response.json['results']) == list
    for result in response.json['results']:
        assert type(result['type']) == str
        assert type(result['geometry']['type']) == str
        assert type(result['geometry']['coordinates'][0]) == float
        assert type(result['geometry']['coordinates'][1]) == float
        assert type(result['properties']['title']) == str
        assert type(result['properties']['icon']) == str
        assert type(result['properties']['description']) == str

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert user == None

def test_event_cities():
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)

    # User must be authenticated
    response = CLIENT.get('/service/events?limit=25')
    assert response.status_code == 401

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username=conf.TEST_USER,
        password=conf.TEST_PASSWORD
    ))
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')

    # User must have access to events
    url = '/service/events/cities'
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access(conf.TEST_USER, ['map'])

    # Success!
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 200
    assert type(response.json['results']) == dict
    for city in response.json['results']['cities']:
        assert type(response.json['results']['cities'][city]) == list
    for city in response.json['results']['counts']:
        assert type(response.json['results']['counts'][city]) == str
    assert type(response.json['count']) == str

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert user == None

def test_export_event_aggregates():
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)

    # User must be authenticated
    url = '/service/events/export?q=trsty'
    response = CLIENT.get(url)
    assert response.status_code == 401

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username=conf.TEST_USER,
        password=conf.TEST_PASSWORD
    ))
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')

    # User must have access to events
    url = '/service/events/export?q=trsty'
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access(conf.TEST_USER, ['events'])

    # Success!
    url = '/service/events/export?q=trsty'
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 200

    csv = StringIO(response.data.decode('utf-8'))
    df = pd.read_csv(csv)
    assert len(df) > 0

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert user == None
