from trs_dashboard.services.app import app
from trs_dashboard.services.user_management import UserManagement

CLIENT = app.test_client()

def test_add_user():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.delete_user('unittestadmin')
    user_management.add_user('unittestadmin', 'testPassword!')
   
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestadmin',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    # Authorization header  is required to register a user
    response = CLIENT.post('/service/user')
    assert response.status_code == 401
    
    # Only an admin can register a user
    response = CLIENT.post('/service/user',
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 403
    user_management.update_role('unittestadmin', 'admin')

    # JSON body is required to register a user
    response = CLIENT.post('/service/user',
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 400
    
    # Username and password is required to register a user
    response = CLIENT.post('/service/user', 
        json=dict(username='unittestuser'),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 400

    # Success!
    response = CLIENT.post('/service/user', 
        json=dict(
            username='unittestuser', 
            password='testPassword!',
            role='standard',
            modules=['events','map']
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 201
    user = user_management.get_user('unittestuser')
    assert 'events' in user['modules']
    assert 'map' in user['modules']
    assert user['role'] == 'standard'

    # Can't register the same user twice
    response = CLIENT.post('/service/user', 
        json=dict(username='unittestuser', password='testPassword!'),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 400

    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None
    
    user_management.delete_user('unittestadmin')
    user = user_management.get_user('unittestadmin')
    assert user == None

def test_delete_user():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.delete_user('unittestadmin')
    user_management.add_user('unittestuser', 'testPassword!')
    user_management.add_user('unittestadmin', 'testPassword!')
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestadmin',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    # Authorization header  is required to delete a user
    response = CLIENT.delete('/service/user/unittestuser')
    assert response.status_code == 401
    
    # Only an admin can delete a user
    response = CLIENT.delete('/service/user/unittestuser',
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 403
    user_management.update_role('unittestadmin', 'admin')

    # Success!
    response = CLIENT.delete('/service/user/unittestuser',
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 204
    
    user = user_management.get_user('unittestuser')
    assert user == None
    
    user_management.delete_user('unittestadmin')
    user = user_management.get_user('unittestadmin')

def test_user_authenticate():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testPassword!')
    
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
        password='testPassword!'
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
    user_management.add_user('unittestuser', 'testPassword!')
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testPassword!'
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
            old_password='wrongtestPassword!',
            new_password='updatedtestPassword!',
            new_password2='updatedtestPassword!'
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 400
    
    # New passwords must match to update password
    response = CLIENT.post('/service/user/change-password', 
        json=dict(
            old_password='testPassword!',
            new_password='wrongupdatedtestPassword!',
            new_password2='updatedtestPassword!'
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 400
    
    # Success!
    response = CLIENT.post('/service/user/change-password', 
        json=dict(
            old_password='testPassword!',
            new_password='updatedtestPassword!',
            new_password2='updatedtestPassword!'
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
    user_management.add_user('unittestuser', 'testPassword!')
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testPassword!'
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

def test_update_role():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.delete_user('unittestadmin')
    user_management.add_user('unittestuser', 'testPassword!')
    user_management.add_user('unittestadmin', 'testPassword!')
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestadmin',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    # Authorization header required to change password
    response = CLIENT.post('/service/user/update-role')
    assert response.status_code == 401
    
    # User must be an admin to update roles
    response = CLIENT.post('/service/user/update-role', 
        json=dict(
            username='unittestuser',
            role='admin'
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 403

    user_management.update_role('unittestadmin', 'admin')
    # Username must be in the post body
    response = CLIENT.post('/service/user/update-role', 
        json=dict(
            role='admin'
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 400
    
    # Role must be in the post body
    response = CLIENT.post('/service/user/update-role', 
        json=dict(
            username='unittestuser'
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 400
    
    # Success!
    response = CLIENT.post('/service/user/update-role', 
        json=dict(
            username='unittestuser',
            role='admin'
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 201
    unittestuser = user_management.get_user('unittestuser')
    assert unittestuser['role'] == 'admin'
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None
    
    user_management.delete_user('unittestadmin')
    user = user_management.get_user('unittestadmin')
    assert user == None

def test_update_access():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.delete_user('unittestadmin')
    user_management.add_user('unittestuser', 'testPassword!')
    user_management.add_user('unittestadmin', 'testPassword!')
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestadmin',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    # Authorization header required to change password
    response = CLIENT.post('/service/user/update-access')
    assert response.status_code == 401
    
    # User must be an admin to update roles
    response = CLIENT.post('/service/user/update-access', 
        json=dict(
            username='unittestuser',
            modules=['events','map']
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 403

    user_management.update_role('unittestadmin', 'admin')
    # Username must be in the post body
    response = CLIENT.post('/service/user/update-access', 
        json=dict(
            modules=['events','map']
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 400
    
    # Modules must be in the post body
    response = CLIENT.post('/service/user/update-access', 
        json=dict(
            username='unittestuser'
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 400
    
    # Success!
    response = CLIENT.post('/service/user/update-access', 
        json=dict(
            username='unittestuser',
            modules=['events','map']
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 201
    unittestuser = user_management.get_user('unittestuser')
    assert 'events' in unittestuser['modules']
    assert 'map' in unittestuser['modules']
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None
    
    user_management.delete_user('unittestadmin')
    user = user_management.get_user('unittestadmin')
    assert user == None

def test_reset_password():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.delete_user('unittestadmin')
    user_management.add_user('unittestuser', 'testPassword!')
    user_management.add_user('unittestadmin', 'testPassword!')
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestadmin',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    # Authorization header required to change password
    response = CLIENT.post('/service/user/reset-password')
    assert response.status_code == 401
    
    # User must be an admin to update roles
    response = CLIENT.post('/service/user/reset-password', 
        json=dict(
            username='unittestuser',
            password='testPASSWORD@',
            password2='testPASSWORD@'
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 403

    user_management.update_role('unittestadmin', 'admin')
    # Username must be in the post body
    response = CLIENT.post('/service/user/reset-password', 
        json=dict(
            password='testPASSWORD@',
            password2='testPASSWORD@'
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 400
    
    # Password must be in the post body
    response = CLIENT.post('/service/user/reset-password', 
        json=dict(
            username='unittestuser',
            password2='testPASSWORD@'
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 400
    
    # Password2 must be in the post body
    response = CLIENT.post('/service/user/reset-password', 
        json=dict(
            username='unittestuser',
            password='testPASSWORD@'
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 400
    
    # Passwords must match
    response = CLIENT.post('/service/user/reset-password', 
        json=dict(
            username='unittestuser',
            password='testPASSWORD@',
            password2='testPASSWORD!'
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 400
    
    # Success!
    response = CLIENT.post('/service/user/reset-password', 
        json=dict(
            username='unittestuser',
            password='testPASSWORD@',
            password2='testPASSWORD@'
        ),
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 201
    unittestuser = user_management.get_user('unittestuser')
    assert unittestuser['password'] == user_management.hash_pw('testPASSWORD@')
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None
    
    user_management.delete_user('unittestadmin')
    user = user_management.get_user('unittestadmin')
    assert user == None

def test_list_users():
    user_management = UserManagement()
    user_management.delete_user('unittestadmin')
    user_management.add_user('unittestadmin', 'testPassword!')
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestadmin',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    # Authorization header required to change password
    response = CLIENT.get('/service/users/list')
    assert response.status_code == 401
    
    # User must be an admin to update roles
    response = CLIENT.get('/service/users/list', 
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 403

    user_management.update_role('unittestadmin', 'admin')
    # Success!
    response = CLIENT.get('/service/users/list', 
        headers={'Authorization': 'Bearer %s'%(jwt)}
    )
    assert response.status_code == 200
    users = response.json
    for user in users:
        assert 'id' in user
        assert 'role' in user
        assert 'modules' in user
        assert 'password' not in user
    
    user_management.delete_user('unittestadmin')
    user = user_management.get_user('unittestadmin')
    assert user == None

def test_pw_complexity():
    user_management = UserManagement()
    assert user_management.check_pw_complexity('Hell@') == False
    assert user_management.check_pw_complexity('hiphophoooray') == False
    assert user_management.check_pw_complexity('Hiphophoooray') == False
    assert user_management.check_pw_complexity('HIPHOPHOORAY') == False
    assert user_management.check_pw_complexity('HIPHOPHooR@Y') == True
