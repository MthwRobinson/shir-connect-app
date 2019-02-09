from io import StringIO
import json

import pandas as pd

from shir_connect.services.app import app
from shir_connect.services.user_management import UserManagement

CLIENT = app.test_client()

def test_monthly_revenue():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testPassword!')
    url = '/service/trends/monthly-revenue'
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
   
    # JWT needs to be included in the response header
    response = CLIENT.get(url)
    assert response.status_code == 401

    # User must have access to trends
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access('unittestuser', ['trends'])

    # Success!
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 200
    assert type(response.json['results']) == list
    for result in response.json['results']:
        assert 'revenue' in result
        assert 'yr' in result
        assert 'mn' in result
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None

def test_avg_attendance():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testPassword!')
    url = '/service/trends/avg-attendance'
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
   
    # JWT need to be in the header
    response = CLIENT.get(url)
    assert response.status_code == 401

    # User must have access to trends
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access('unittestuser', ['trends'])

    # Success!
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 200
    assert type(response.json['results']) == list
    for result in response.json['results']:
        assert 'day_of_week' in result
        assert 'day_order' in result
        assert 'avg_attendance' in result
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None

def test_year_group_attendees():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testPassword!')
    url = '/service/trends/age-group-attendance'
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
   
    # JWT must be in the response header
    response = CLIENT.get(url)
    assert response.status_code == 401
    
    # User must have access to trends
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access('unittestuser', ['trends'])

    # Success!
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 200
    assert type(response.json) == dict
    for key in response.json:
        assert 'group' in response.json[key]
        assert 'count' in response.json[key]

    # And now let's try grouping by month
    url += '?groupBy=month'
    assert response.status_code == 200
    assert type(response.json) == dict
    for key in response.json:
        assert 'group' in response.json[key]
        assert 'count' in response.json[key]
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None

def test_participation():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testPassword!')
    url = '/service/trends/participation/Young Professional'
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
   
    # JWT must be in the header
    response = CLIENT.get(url)
    assert response.status_code == 401
    
    # User must have access to the trends page 
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access('unittestuser', ['trends'])

    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 200
    assert type(response.json['results']) == list
    for item in response.json['results']:
        assert 'id' in item
        assert 'name' in item
        assert 'total' in item

    url += '?top=event'
    assert response.status_code == 200
    assert type(response.json['results']) == list
    for item in response.json['results']:
        assert 'id' in item
        assert 'name' in item
        assert 'total' in item
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None
