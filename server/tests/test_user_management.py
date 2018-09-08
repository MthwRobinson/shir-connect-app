from trs_dashboard.services.app import app
from trs_dashboard.services.user_management import UserManagement

CLIENT = app.test_client()

def test_user_register():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    
    response = CLIENT.post('/service/user/register')
    assert response.status_code == 400
    
    response = CLIENT.post('/service/user/register', json=dict(
        username='unittestuser'
    ))
    assert response.status_code == 400

    response = CLIENT.post('/service/user/register', json=dict(
        username='unittestuser',
        password='testpassword'
    ))
    assert response.status_code == 201

    response = CLIENT.post('/service/user/register', json=dict(
        username='unittestuser',
        password='testpassword'
    ))
    assert response.status_code == 409
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None

def test_user_register():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    
    response = CLIENT.post('/service/user/authenticate')
    assert response.status_code == 400
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser'
    ))
    assert response.status_code == 400

    response = CLIENT.post('/service/user/register', json=dict(
        username='unittestuser',
        password='testpassword'
    ))
    assert response.status_code == 201
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testpassword'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='badpassword'
    ))
    assert response.status_code == 401
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None
