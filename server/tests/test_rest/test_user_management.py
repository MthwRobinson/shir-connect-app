from shir_connect.services.app import app
from shir_connect.database.user_management import UserManagement
import shir_connect.services.utils as utils

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
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')
    csrf = utils._get_cookie_from_response(response, 'csrf_access_token')
    
    # Only an admin can register a user
    response = CLIENT.post('/service/user',
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 403
    user_management.update_role('unittestadmin', 'admin')

    # JSON body is required to register a user
    response = CLIENT.post('/service/user', headers={
        'Cookies': 'access_token_cookie=%s'%(jwt),
        'X-CSRF-TOKEN': csrf['csrf_access_token']
    })
    assert response.status_code == 400

    # Success!
    response = CLIENT.post('/service/user', 
        json=dict(
            username='unittestuser', 
            role='standard',
            modules=['events','map']
        ),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
    })
    assert response.status_code == 201
    assert 'password' in response.json
    user = user_management.get_user('unittestuser')
    assert 'events' in user['modules']
    assert 'map' in user['modules']
    assert user['role'] == 'standard'

    # Can't register the same user twice
    response = CLIENT.post('/service/user', 
        json=dict(username='unittestuser', password='testPassword!'),
        headers={
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
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')
    csrf = utils._get_cookie_from_response(response, 'csrf_access_token')
    
    # Only an admin can delete a user
    response = CLIENT.delete('/service/user/unittestuser',
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 403
    user_management.update_role('unittestadmin', 'admin')

    # Success!
    response = CLIENT.delete('/service/user/unittestuser',
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 204
    
    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200
    
    user = user_management.get_user('unittestuser')
    assert user == None
    
    user_management.delete_user('unittestadmin')
    user = user_management.get_user('unittestadmin')

def test_user_authenticate():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testPassword!')
   
    # Username and password are required to authenticate
    response = CLIENT.post('/service/user/authenticate')
    assert response.status_code == 400
    
    # Password is required to authenticate
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser'
    ))
    assert response.status_code == 400

    # Password must be correct to authenticate
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='badpassword'
    ))
    assert response.status_code == 401

    # Success !
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testPassword!'
    ))
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')
    refresh_jwt = utils._get_cookie_from_response(response, 'refresh_token_cookie')
    csrf = utils._get_cookie_from_response(response, 'csrf_access_token')

    # Success!
    response = CLIENT.get('/service/user/authorize', headers={
        'Cookies': 'access_token_cookie=%s'%(jwt),
        'X-CSRF-TOKEN': csrf['csrf_access_token']
    })
    assert response.status_code == 200
    assert response.json['id'] == 'unittestuser'
   
    # Success!
    response = CLIENT.get('/service/user/refresh', headers={
        'Cookies': 'access_token_cookie=%s;refresh_token_cookie=%s'%(jwt, refresh_jwt),
        'X-CSRF-TOKEN': csrf['csrf_access_token']
    })
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'refresh_token_cookie')
    refresh_jwt = utils._get_cookie_from_response(response, 'refresh_token_cookie')
    csrf = utils._get_cookie_from_response(response, 'csrf_access_token')
    
    # Make sure the refreshed token works
    response = CLIENT.get('/service/user/authorize', headers={
        'Cookies': 'access_token_cookie=%s'%(jwt)
    })
    assert response.status_code == 200
    assert response.json['id'] == 'unittestuser'
    
    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

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
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')
    csrf = utils._get_cookie_from_response(response, 'csrf_access_token')
    
    # JSON body is required to update password
    response = CLIENT.post('/service/user/change-password', 
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
    })
    assert response.status_code == 400
    
    # Old password must be correct to change password
    response = CLIENT.post('/service/user/change-password', 
        json=dict(
            old_password='wrongtestPassword!',
            new_password='updatedtestPassword!',
            new_password2='updatedtestPassword!'
        ),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 400
    
    # New passwords must match to update password
    response = CLIENT.post('/service/user/change-password', 
        json=dict(
            old_password='testPassword!',
            new_password='wrongupdatedtestPassword!',
            new_password2='updatedtestPassword!'
        ),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 400
    
    # Success!
    response = CLIENT.post('/service/user/change-password', 
        json=dict(
            old_password='testPassword!',
            new_password='updatedtestPassword!',
            new_password2='updatedtestPassword!'
        ),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 201

    # Make sure password update worked
    authorized = user_management.authenticate_user(
        username='unittestuser',
        password='updatedtestpassowrd'
    )
    
    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200
    
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
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')
    csrf = utils._get_cookie_from_response(response, 'csrf_access_token')
    
    # Success!
    response = CLIENT.get('/service/user/authorize', 
        headers={'Cookies': 'access_token_cookie=%s'%(jwt)}
    )
    assert response.status_code == 200
    assert 'password' not in response.json
    
    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200
    
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
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')
    csrf = utils._get_cookie_from_response(response, 'csrf_access_token')
    
    # User must be an admin to update roles
    response = CLIENT.post('/service/user/update-role', 
        json=dict(
            username='unittestuser',
            role='admin'
        ),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 403

    user_management.update_role('unittestadmin', 'admin')
    # Username must be in the post body
    response = CLIENT.post('/service/user/update-role', 
        json=dict(
            role='admin'
        ),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 400
    
    # Role must be in the post body
    response = CLIENT.post('/service/user/update-role', 
        json=dict(
            username='unittestuser'
        ),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 400
    
    # Success!
    response = CLIENT.post('/service/user/update-role', 
        json=dict(
            username='unittestuser',
            role='admin'
        ),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 201
    unittestuser = user_management.get_user('unittestuser')
    assert unittestuser['role'] == 'admin'
    
    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200
    
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
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')
    csrf = utils._get_cookie_from_response(response, 'csrf_access_token')
    
    # User must be an admin to update roles
    response = CLIENT.post('/service/user/update-access', 
        json=dict(
            username='unittestuser',
            modules=['events','map']
        ),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 403

    user_management.update_role('unittestadmin', 'admin')
    # Username must be in the post body
    response = CLIENT.post('/service/user/update-access', 
        json=dict(
            modules=['events','map']
        ),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 400
    
    # Modules must be in the post body
    response = CLIENT.post('/service/user/update-access', 
        json=dict(
            username='unittestuser'
        ),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 400
    
    # Success!
    response = CLIENT.post('/service/user/update-access', 
        json=dict(
            username='unittestuser',
            modules=['events','map']
        ),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 201
    unittestuser = user_management.get_user('unittestuser')
    assert 'events' in unittestuser['modules']
    assert 'map' in unittestuser['modules']
    
    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200
    
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
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')
    csrf = utils._get_cookie_from_response(response, 'csrf_access_token')
    
    # User must be an admin to update roles
    response = CLIENT.post('/service/user/reset-password', 
        json=dict(username='unittestuser'),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 403

    user_management.update_role('unittestadmin', 'admin')
    # Username must be in the post body
    response = CLIENT.post('/service/user/reset-password', 
        json=dict(password='testPASSWORD@'),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 400
    
    # Success!
    response = CLIENT.post('/service/user/reset-password', 
        json=dict(username='unittestuser'),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 201
    assert 'password' in response.json
    password = response.json['password']
    unittestuser = user_management.get_user('unittestuser')
    assert unittestuser['password'] == user_management.hash_pw(password)
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None
    
    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200
    
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
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')
    csrf = utils._get_cookie_from_response(response, 'csrf_access_token')
    
    # User must be an admin to update roles
    response = CLIENT.get('/service/users/list', 
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 403

    user_management.update_role('unittestadmin', 'admin')
    # Success!
    response = CLIENT.get('/service/users/list', 
        headers={'Cookies': 'access_token_cookie=%s'%(jwt)}
    )
    assert response.status_code == 200
    users = response.json
    for user in users:
        assert 'id' in user
        assert 'role' in user
        assert 'modules' in user
        assert 'password' not in user

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200
    
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
