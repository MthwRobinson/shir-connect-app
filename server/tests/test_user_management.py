from trs_dashboard.services.app import app
from trs_dashboard.services.user_management import UserManagement

CLIENT = app.test_client()

def test_user_register():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.delete_user('unittestadmin')
    user_management.add_user('unittestadmin', 'testpassword')
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestadmin',
        password='testpassword'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']

    response = CLIENT.post('/service/user/register',
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 400
    
    response = CLIENT.post('/service/user/register', 
        json=dict(username='unittestuser'),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 400

    response = CLIENT.post('/service/user/register', 
        json=dict(username='unittestuser', password='testpassword'),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 201

    response = CLIENT.post('/service/user/register', 
        json=dict(username='unittestuser', password='testpassword'),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 409
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None
    
    user_management.delete_user('unittestadmin')
    user = user_management.get_user('unittestadmin')
    assert user == None

def test_user_authenticate():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testpassword')
    
    response = CLIENT.post('/service/user/authenticate')
    assert response.status_code == 400
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser'
    ))
    assert response.status_code == 400

    response = CLIENT.get('/service/test')
    assert response.status_code == 401
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testpassword'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']

    response = CLIENT.get('/service/test', headers={
        'Authorization': 'Bearer %s'%(jwt)
    })
    assert response.status_code == 200
    assert 'unittestuser' in response.json['message']
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='badpassword'
    ))
    assert response.status_code == 401
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None
