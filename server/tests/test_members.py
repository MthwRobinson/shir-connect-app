from io import StringIO
import json

import pandas as pd

from shir_connect.services.app import app
from shir_connect.services.members import Members
from shir_connect.services.user_management import UserManagement

CLIENT = app.test_client()

def test_member_authorize():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testPassword!')
    url = '/service/member/authorize'
    
    # The user must be authenticated
    response = CLIENT.get(url)
    assert response.status_code == 401
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    # The user must have access to members
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access('unittestuser',['members'])
    
    # Success!
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 200
    assert 'role' in response.json
    assert 'password' not in response.json
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None

def test_members():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testPassword!')

    # Must be authenticated to use the service
    response = CLIENT.get('/service/members?limit=25')
    assert response.status_code == 401
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    # The JWT must be in the header of the request
    url = '/service/members?limit=25&page=2'
    url += '&sort=last_event_date&order=desc'
    url += '&q=smuckler'
    response = CLIENT.get(url)
    assert response.status_code == 401
    
    # The user must have access to members
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access('unittestuser',['members'])

    # Success!
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
    user_management.add_user('unittestuser', 'testPassword!')
    url = '/service/member'
    
    # The user must be authenticated
    response = CLIENT.get(url)
    assert response.status_code == 401
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    # The user must have access to members
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access('unittestuser',['members'])

    # The parametes must include first name and last name
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 404
    
    # The parametes must include first name and last name
    url += '?firstName=danielle'
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 404
    
    # Success!
    url += '&lastName=agress'
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 200
    assert 'first_name' in response.json
    assert 'last_name' in response.json
    assert 'age' in response.json
    assert 'membership_date' in response.json
    assert 'is_member' in response.json
    assert 'events' in response.json
    assert type(response.json['events']) == list
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None

def test_member_upload():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testPassword!')
    url = '/service/members/upload'
    
    # The user must be authenticated
    response = CLIENT.post(url)
    assert response.status_code == 401
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    # The user must have access to members
    response = CLIENT.post(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 403
    user_management.update_role('unittestuser', 'admin')
    
    # Uh oh! Bad file
    response = CLIENT.post(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 400

    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None
