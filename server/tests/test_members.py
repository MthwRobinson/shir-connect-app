from io import StringIO
import json

import pandas as pd

from trs_dashboard.services.app import app
from trs_dashboard.services.members import Members
from trs_dashboard.services.user_management import UserManagement

CLIENT = app.test_client()

def test_members():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testpassword')
    
    response = CLIENT.get('/service/members?limit=25')
    assert response.status_code == 401
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testpassword'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    url = '/service/members?limit=25&page=2'
    url += '&sort=membership_date&order=desc'
    url += '&q=smuckler'
    response = CLIENT.get(url)
    assert response.status_code == 401

    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 200
    assert type(response.json['results']) == list
    assert 'count' in response.json
    assert 'pages' in response.json
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None

def test_member():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testpassword')
    url = '/service/member'
    
    response = CLIENT.get(url)
    assert response.status_code == 401
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testpassword'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 404
    
    url += '?firstName=danielle'
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 404
    
    url += '&lastName=agress'
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 200
    assert 'first_name' in response.json
    assert 'last_name' in response.json
    assert 'age' in response.json
    assert 'membership_date' in response.json
    assert 'is_member' in response.json
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None

def test_dummy_members():
    members = Members()
    df = members.create_dummy_members(limit=20)
    assert len(df) <= 20
