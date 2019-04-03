from io import StringIO
import json

import pandas as pd
import pytest

from shir_connect.services.app import app
from shir_connect.database.members import Members
from shir_connect.services.user_management import UserManagement
import shir_connect.services.utils as utils

CLIENT = app.test_client()

@pytest.fixture
def test_participant():
    members = Members()
    sql = """
        SELECT first_name, last_name
        FROM {schema}.participants
        WHERE first_name IS NOT NULL
        AND last_name IS NOT NULL
        ORDER BY first_name DESC, last_name DESC
        LIMIT 1
    """.format(schema=members.database.schema)
    df = pd.read_sql(sql, members.database.connection)
    test_participant = dict(df.loc[0])
    return test_participant

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
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')
    
    # The user must have access to members
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access('unittestuser',['members'])
    
    # Success!
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 200
    assert 'role' in response.json
    assert 'password' not in response.json

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200
    
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
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')
    
    url = '/service/members?limit=25&page=2'
    url += '&sort=last_event_date&order=desc'
    url += '&q=smuckler&min_age=4&max_age=100'
    
    # The user must have access to members
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access('unittestuser',['members'])

    # Success!
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 200
    assert type(response.json['results']) == list
    assert 'count' in response.json
    assert 'pages' in response.json
    
    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None

def test_member(test_participant):
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
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')
    
    # The user must have access to members
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access('unittestuser',['members'])

    # The parametes must include first name and last name
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 404
    
    # The parametes must include first name and last name
    url += '?firstName=' + test_participant['first_name']
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 404
    
    # Success!
    url += '&lastName=' + test_participant['last_name']
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 200
    assert 'first_name' in response.json
    assert 'last_name' in response.json
    assert 'age' in response.json
    assert 'membership_date' in response.json
    assert 'is_member' in response.json
    assert 'events' in response.json
    assert type(response.json['events']) == list
    
    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200
    
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
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')
    csrf = utils._get_cookie_from_response(response, 'csrf_access_token')

    # The user must have access to members
    response = CLIENT.post(url, headers={
        'Cookies': 'access_token_cookie=%s'%(jwt),
        'X-CSRF-TOKEN': csrf['csrf_access_token']
    })
    assert response.status_code == 403
    user_management.update_role('unittestuser', 'admin')
    
    # Uh oh! Bad file
    response = CLIENT.post(url, headers={
        'Cookies': 'access_token_cookie=%s'%(jwt),
        'X-CSRF-TOKEN': csrf['csrf_access_token']
    })
    assert response.status_code == 400
    
    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None
