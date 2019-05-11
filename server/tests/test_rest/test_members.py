from io import StringIO
import json

import pandas as pd
import pytest

from shir_connect.services.app import app
from shir_connect.database.members import Members
from shir_connect.database.user_management import UserManagement
import shir_connect.services.utils as utils

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
