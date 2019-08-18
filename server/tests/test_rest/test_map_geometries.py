import shir_connect.configuration as conf
from shir_connect.services.app import app
from shir_connect.database.user_management import UserManagement
import shir_connect.services.utils as utils

CLIENT = app.test_client()

def test_map_authorize():
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)
    url = '/service/map/authorize'

    # User must be authenticated
    response = CLIENT.get(url)
    assert response.status_code == 401

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username=conf.TEST_USER,
        password=conf.TEST_PASSWORD
    ))
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')

    # The user must have access to the map module
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access(conf.TEST_USER, ['map'])

    # Success!
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 200

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert user == None

def test_zip_geometry():
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)
    url = '/service/map/geometry/22102'

    # User must be authenticated
    response = CLIENT.get(url)
    assert response.status_code == 401

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username=conf.TEST_USER,
        password=conf.TEST_PASSWORD
    ))
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')

    # The user must have access to the map module
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access(conf.TEST_USER, ['map'])

    # Success!
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 200
    assert 'id' in response.json
    assert 'type' in response.json
    assert 'source' in response.json
    assert response.json['source']['type'] == 'geojson'
    assert type(response.json['source']['data']) == dict
    assert 'paint' in response.json

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert user == None

def test_zip_codes():
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)
    url = '/service/map/zipcodes'

    # The user must be authenticated
    response = CLIENT.get(url)
    assert response.status_code == 401

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username=conf.TEST_USER,
        password=conf.TEST_PASSWORD
    ))
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')

    # The user must have access to the map
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access(conf.TEST_USER, ['map'])

    # Success!
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 200
    assert type(response.json) == dict

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert user == None

def test_all_geometries():
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)
    url = '/service/map/geometries'

    # The user must be authenticated
    response = CLIENT.get(url)
    assert response.status_code == 401

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username=conf.TEST_USER,
        password=conf.TEST_PASSWORD
    ))
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')

    # The user must have access to the map
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access(conf.TEST_USER, ['map'])

    # Success!
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 200
    for key in response.json:
        layer = response.json[key]
        assert 'id' in layer
        assert 'type' in layer
        assert 'source' in layer
        assert layer['source']['type'] == 'geojson'
        assert type(layer['source']['data']) == dict
        assert 'paint' in layer

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert user == None

def test_default_location():
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)
    url = '/service/map/default'

    # The user must be authenticated
    response = CLIENT.get(url)
    assert response.status_code == 401

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username=conf.TEST_USER,
        password=conf.TEST_PASSWORD
    ))
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')

    # Success!
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 200
    assert type(response.json) == dict

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert user == None

def test_map_event_group_options():
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)
    url = '/service/map/event_options'

    # The user must be authenticated
    response = CLIENT.get(url)
    assert response.status_code == 401

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username=conf.TEST_USER,
        password=conf.TEST_PASSWORD
    ))
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')

    # Success!
    response = CLIENT.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 200
    assert type(response.json) == list

    url = '/service/user/logout'
    response = CLIENT.post(url)
    assert response.status_code == 200

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert user == None
