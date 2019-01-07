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
    
    # Authorization header  is required to register a user
    response = CLIENT.post('/service/user/register')
    assert response.status_code == 401

    # JSON body is required to register a user
    response = CLIENT.post('/service/user/register',
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 400
    
    # Username and password is required to register a user
    response = CLIENT.post('/service/user/register', 
        json=dict(username='unittestuser'),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 400

    # Success!
    response = CLIENT.post('/service/user/register', 
        json=dict(
            username='unittestuser', 
            password='testpassword',
            role='standard',
            modules=[]
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 201

    # Can't register the same user twice
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

    response = CLIENT.get('/service/user/authorize')
    assert response.status_code == 401
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testpassword'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']

    response = CLIENT.get('/service/user/authorize', headers={
        'Authorization': 'Bearer %s'%(jwt)
    })
    assert response.status_code == 200
    assert response.json['id'] == 'unittestuser'
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='badpassword'
    ))
    assert response.status_code == 401
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None
    
def test_change_password():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testpassword')
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testpassword'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']

    # Authorization header required to change password
    response = CLIENT.post('/service/user/change-password')
    assert response.status_code == 401
    
    # JSON body is required to update password
    response = CLIENT.post('/service/user/change-password', 
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 400
    
    # Old password must be correct to change password
    response = CLIENT.post('/service/user/change-password', 
        json=dict(
            old_password='wrongtestpassword',
            new_password='updatedtestpassword',
            new_password2='updatedtestpassword'
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 400
    
    # New passwords must match to update password
    response = CLIENT.post('/service/user/change-password', 
        json=dict(
            old_password='testpassword',
            new_password='wrongupdatedtestpassword',
            new_password2='updatedtestpassword'
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 400
    
    # Success!
    response = CLIENT.post('/service/user/change-password', 
        json=dict(
            old_password='testpassword',
            new_password='updatedtestpassword',
            new_password2='updatedtestpassword'
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 201

    # Make sure password update worked
    authorized = user_management.authenticate_user(
        username='unittestuser',
        password='updatedtestpassowrd'
    )
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None

def test_authorize():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testpassword')
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testpassword'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']

    # Authorization header required to change password
    response = CLIENT.get('/service/user/authorize')
    assert response.status_code == 401
    
    # Success!
    response = CLIENT.get('/service/user/authorize', 
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 200
    assert 'password' not in response.json
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None
