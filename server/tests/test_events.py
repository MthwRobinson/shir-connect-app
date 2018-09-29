import json

from trs_dashboard.services.app import app
from trs_dashboard.services.user_management import UserManagement

CLIENT = app.test_client()

def test_events():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testpassword')
    
    response = CLIENT.get('/service/events?limit=25')
    assert response.status_code == 401
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testpassword'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    response = CLIENT.get('/service/events?limit=25')
    assert response.status_code == 401

    response = CLIENT.get('/service/events?limit=25', headers={
        'Authorization': 'Bearer %s'%(jwt)
    })
    assert response.status_code == 200
    assert type(response.json) == list
    assert len(response.json) == 25
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None
