from io import StringIO
import json

import pandas as pd

from trs_dashboard.services.app import app
from trs_dashboard.services.user_management import UserManagement

CLIENT = app.test_client()

def test_event():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testPassword!')

    # User must be authenticated
    url = '/service/event/7757038511'
    response = CLIENT.get(url)
    assert response.status_code == 401
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    # JWT must be present in the header
    response = CLIENT.get(url)
    assert response.status_code == 401
    
    # User must have access to events
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access('unittestuser', ['events'])

    # Success
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
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
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 404
    assert type(response.json) == dict
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None

def test_events():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testPassword!')
    
    # User must be authenticated
    response = CLIENT.get('/service/events?limit=25')
    assert response.status_code == 401
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    # JWT must be in the header
    url = '/service/events?limit=25&page=2'
    url += '&sort=start_datetime&order=desc'
    url += '&q=trsty'
    response = CLIENT.get(url)
    assert response.status_code == 401
    
    # User must have access to events
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access('unittestuser', ['events'])

    # Success!
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 200
    assert type(response.json['results']) == list
    assert len(response.json['results']) == 25
    assert 'count' in response.json
    assert 'pages' in response.json
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None

def test_event_locations():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testPassword!')
    
    # User must be authenticated
    response = CLIENT.get('/service/events?limit=25')
    assert response.status_code == 401
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    # Request must have a header
    url = '/service/events/locations'
    response = CLIENT.get(url)
    assert response.status_code == 401
    
    # User must have access to events
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access('unittestuser', ['map'])

    # Success!
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
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
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None

def test_event_cities():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testPassword!')
    
    # User must be authenticated
    response = CLIENT.get('/service/events?limit=25')
    assert response.status_code == 401
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    # Request must have JWT in the header
    url = '/service/events/cities'
    response = CLIENT.get(url)
    assert response.status_code == 401
    
    # User must have access to events
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access('unittestuser', ['map'])

    # Success!
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 200
    assert type(response.json['results']) == dict
    for city in response.json['results']['cities']:
        assert type(response.json['results']['cities'][city]) == list
    for city in response.json['results']['counts']:
        assert type(response.json['results']['counts'][city]) == str
    assert type(response.json['count']) == str
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None

def test_export_event_aggregates():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testPassword!')
    
    # User must be authenticated
    url = '/service/events/export?q=trsty'
    response = CLIENT.get(url)
    assert response.status_code == 401

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testPassword!'
    ))
    assert response.status_code == 200
    jwt = response.json['jwt']

    # User must have access to events
    url = '/service/events/export?q=trsty'
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access('unittestuser', ['events'])

    # Success!
    url = '/service/events/export?q=trsty'
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 200

    csv = StringIO(response.data.decode('utf-8'))
    df = pd.read_csv(csv)
    assert len(df) > 0

    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None
