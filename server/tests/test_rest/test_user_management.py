import pytest

from shir_connect.services.app import app
from shir_connect.database.user_management import UserManagement
import shir_connect.services.utils as utils
import shir_connect.configuration as conf

CLIENT = app.test_client()

def test_add_user():
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.delete_user('unittestadmin')
    user_management.add_user('unittestadmin', conf.TEST_PASSWORD)

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestadmin',
        password=conf.TEST_PASSWORD))
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')
    csrf = utils._get_cookie_from_response(response, 'csrf_access_token')

    # Only an admin can register a user
    response = CLIENT.post('/service/user?mode=test',
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']})
    assert response.status_code == 403
    user_management.update_role('unittestadmin', 'admin')

    # JSON body is required to register a user
    response = CLIENT.post('/service/user?mode=test', headers={
        'Cookies': 'access_token_cookie=%s'%(jwt),
        'X-CSRF-TOKEN': csrf['csrf_access_token']})
    assert response.status_code == 400

    # Success!
    response = CLIENT.post('/service/user?mode=test',
        json=dict(username=conf.TEST_USER,
                  email='jabber@fakeemail.birds',
                  role='standard',
                  modules=['events','map']),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']})
    assert response.status_code == 201
    user = user_management.get_user(conf.TEST_USER)
    assert 'events' in user['modules']
    assert 'map' in user['modules']
    assert user['role'] == 'standard'
    assert user['email'] == 'jabber@fakeemail.birds'

    # Can't register the same user twice
    response = CLIENT.post('/service/user?mode=test',
        json=dict(username=conf.TEST_USER,
                  email='jabber@fakeemail.birds',
                  password=conf.TEST_PASSWORD),
        headers={'Cookies': 'access_token_cookie=%s'%(jwt),
                 'X-CSRF-TOKEN': csrf['csrf_access_token']})
    assert response.status_code == 400

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert user == None

    user_management.delete_user('unittestadmin')
    user = user_management.get_user('unittestadmin')
    assert user == None

def test_delete_user():
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.delete_user('unittestadmin')
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)
    user_management.add_user('unittestadmin', conf.TEST_PASSWORD)

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestadmin',
        password=conf.TEST_PASSWORD
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

    user = user_management.get_user(conf.TEST_USER)
    assert user == None

    user_management.delete_user('unittestadmin')
    user = user_management.get_user('unittestadmin')

def test_user_authenticate(monkeypatch):
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)

    # Username and password are required to authenticate
    response = CLIENT.post('/service/user/authenticate')
    assert response.status_code == 400

    # Password is required to authenticate
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username=conf.TEST_USER
    ))
    assert response.status_code == 400

    # Password must be correct to authenticate
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username=conf.TEST_USER,
        password='badpassword'
    ))
    assert response.status_code == 401

    # Success !
    monkeypatch.setattr('shir_connect.services.utils.count_bad_login_attempts',
                        lambda *args, **kwargs: 2)
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username=conf.TEST_USER,
        password=conf.TEST_PASSWORD
    ))
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')
    refresh_jwt = utils._get_cookie_from_response(response, 'refresh_token_cookie')
    csrf = utils._get_cookie_from_response(response, 'csrf_access_token')

    # Tests that authenticate is also working with cookies
    response = CLIENT.get('/service/user/authorize', headers={
        'Cookies': 'access_token_cookie=%s'%(jwt),
        'X-CSRF-TOKEN': csrf['csrf_access_token']
    })
    assert response.status_code == 200
    assert response.json['id'] == conf.TEST_USER

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
    assert response.json['id'] == conf.TEST_USER

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert user == None

def test_change_password():
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username=conf.TEST_USER,
        password=conf.TEST_PASSWORD
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
            old_password='1wrongtestPassword!',
            new_password=conf.TEST_PASSWORD + '!1',
            new_password2=conf.TEST_PASSWORD + '!1'
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
            old_password=conf.TEST_PASSWORD,
            new_password=conf.TEST_PASSWORD + '!1',
            new_password2=conf.TEST_PASSWORD + '!2'
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
            old_password=conf.TEST_PASSWORD,
            new_password=conf.TEST_PASSWORD + '!1',
            new_password2=conf.TEST_PASSWORD + '!1'
        ),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 201

    # Make sure password update worked
    authorized = user_management.authenticate_user(
        username=conf.TEST_USER,
        password='updatedtestpassowrd'
    )

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert user == None

def test_authorize():
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username=conf.TEST_USER,
        password=conf.TEST_PASSWORD
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

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert user == None

def test_update_role():
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.delete_user('unittestadmin')
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)
    user_management.add_user('unittestadmin', conf.TEST_PASSWORD)

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestadmin',
        password=conf.TEST_PASSWORD
    ))
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')
    csrf = utils._get_cookie_from_response(response, 'csrf_access_token')

    # User must be an admin to update roles
    response = CLIENT.post('/service/user/update-role',
        json=dict(
            username=conf.TEST_USER,
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
            username=conf.TEST_USER
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
            username=conf.TEST_USER,
            role='admin'
        ),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 201
    unittestuser = user_management.get_user(conf.TEST_USER)
    assert unittestuser['role'] == 'admin'

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert user == None

    user_management.delete_user('unittestadmin')
    user = user_management.get_user('unittestadmin')
    assert user == None

def test_update_email():
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.delete_user('unittestadmin')
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)
    user_management.add_user('unittestadmin', conf.TEST_PASSWORD)

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestadmin',
        password=conf.TEST_PASSWORD))
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')
    csrf = utils._get_cookie_from_response(response, 'csrf_access_token')

    # User must be an admin to update email
    response = CLIENT.post('/service/user/update-email',
        json=dict(
            username=conf.TEST_USER,
            role='admin'
        ),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']})
    assert response.status_code == 403

    user_management.update_role('unittestadmin', 'admin')
    # Username must be in the post body
    response = CLIENT.post('/service/user/update-email',
        json=dict(email='potato@carl.com'),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        })
    assert response.status_code == 400

    # Email must be in the post body
    response = CLIENT.post('/service/user/update-email',
        json=dict(username=conf.TEST_USER),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        })
    assert response.status_code == 400

    # Success!
    response = CLIENT.post('/service/user/update-email',
        json=dict(username=conf.TEST_USER, email='carl@twohump.camel'),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        })
    assert response.status_code == 201
    unittestuser = user_management.get_user(conf.TEST_USER)
    assert unittestuser['email'] == 'carl@twohump.camel'

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert user == None

    user_management.delete_user('unittestadmin')
    user = user_management.get_user('unittestadmin')
    assert user == None

def test_update_access():
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.delete_user('unittestadmin')
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)
    user_management.add_user('unittestadmin', conf.TEST_PASSWORD)

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestadmin',
        password=conf.TEST_PASSWORD
    ))
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')
    csrf = utils._get_cookie_from_response(response, 'csrf_access_token')

    # User must be an admin to update roles
    response = CLIENT.post('/service/user/update-access',
        json=dict(
            username=conf.TEST_USER,
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
            username=conf.TEST_USER
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
            username=conf.TEST_USER,
            modules=['events','map']
        ),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 201
    unittestuser = user_management.get_user(conf.TEST_USER)
    assert 'events' in unittestuser['modules']
    assert 'map' in unittestuser['modules']

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert user == None

    user_management.delete_user('unittestadmin')
    user = user_management.get_user('unittestadmin')
    assert user == None

def test_user_reset_password():
    """For the user reset password end point to work, the e-mail
    in the post body must correspond to the e-mail that is on
    record for the user's account."""
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD,
                             email='jabber@fakeemail.birds')

    # Both the email and the username must appear in the post body
    response = CLIENT.post('/service/user/user-reset-password?mode=test',
        json=dict(username=conf.TEST_USER))
    assert response.status_code == 400

    # The email address in the post body must match the email address
    # list for the user trying to reset their password
    response = CLIENT.post('/service/user/user-reset-password?mode=test',
        json=dict(username=conf.TEST_USER, email='jibber@jabber.net'))
    assert response.status_code == 401

    # Success!
    response = CLIENT.post('/service/user/user-reset-password?mode=test',
        json=dict(username=conf.TEST_USER, email='jabber@fakeemail.birds'))
    assert response.status_code == 201

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert user == None

def test_reset_password():
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.delete_user('unittestadmin')
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)
    user_management.add_user('unittestadmin', conf.TEST_PASSWORD)

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestadmin',
        password=conf.TEST_PASSWORD
    ))
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')
    csrf = utils._get_cookie_from_response(response, 'csrf_access_token')

    # User must be an admin to update roles
    response = CLIENT.post('/service/user/reset-password?mode=test',
        json=dict(username=conf.TEST_USER),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 403

    user_management.update_role('unittestadmin', 'admin')
    # Username must be in the post body
    response = CLIENT.post('/service/user/reset-password?mode=test',
        json=dict(password='testPASSWORD@'),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 400

    # Success!
    response = CLIENT.post('/service/user/reset-password?mode=test',
        json=dict(username=conf.TEST_USER),
        headers={
            'Cookies': 'access_token_cookie=%s'%(jwt),
            'X-CSRF-TOKEN': csrf['csrf_access_token']
        }
    )
    assert response.status_code == 201

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
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
    user_management.add_user('unittestadmin', conf.TEST_PASSWORD)

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestadmin',
        password=conf.TEST_PASSWORD
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
    assert user_management.check_pw_complexity('H3ll@') == False
    assert user_management.check_pw_complexity('hiphophoooray') == False
    assert user_management.check_pw_complexity('Hiphophoooray') == False
    assert user_management.check_pw_complexity('HIPHOPHOORAY') == False
    assert user_management.check_pw_complexity('HIPHOPHooR@Y') == False
    assert user_management.check_pw_complexity('HIPH0PHooRAY') == False
    assert user_management.check_pw_complexity('HIPH0PHooR@Y') == True

def test_pw_complexity_returns_error():
    user_management = UserManagement()
    complex_enough, errors = user_management.check_pw_complexity('parrot', True)
    assert complex_enough == False
    assert len(errors) > 1
