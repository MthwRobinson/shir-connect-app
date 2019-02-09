from shir_connect.services.app import app
from shir_connect.services.user_management import UserManagement

CLIENT = app.test_client()

def test_map_authorize():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testPassword!')
    url = '/service/map/authorize'
    
    # User must be authenticated
    response = CLIENT.get(url)
    assert response.status_code == 401
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    # The JWT must be present in the header
    response = CLIENT.get(url)
    assert response.status_code == 401
    
    # The user must have access to the map module
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access('unittestuser', ['map'])

    # Success!
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 200
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None

def test_zip_geometry():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testPassword!')
    url = '/service/map/geometry/22102'

    # User must be authenticated
    response = CLIENT.get(url)
    assert response.status_code == 401
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    # The JWT must be present in the header
    response = CLIENT.get(url)
    assert response.status_code == 401
    
    # The user must have access to the map module
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access('unittestuser', ['map'])

    # Success!
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 200
    assert 'id' in response.json
    assert 'type' in response.json
    assert 'source' in response.json
    assert response.json['source']['type'] == 'geojson'
    assert type(response.json['source']['data']) == dict
    assert 'paint' in response.json
    assert 'description' in response.json['source']['data']['features'][0]['properties']
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None

def test_zip_codes():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testPassword!')
    url = '/service/map/zipcodes'
    
    # The user must be authenticated
    response = CLIENT.get(url)
    assert response.status_code == 401
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    # The JWT must be present in the header
    response = CLIENT.get(url)
    assert response.status_code == 401
    
    # The user must have access to the mpa
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access('unittestuser', ['map'])

    # Success!
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 200
    assert type(response.json) == list
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None

def test_all_geometries():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testPassword!')
    url = '/service/map/geometries'
    
    # The user must be authenticated
    response = CLIENT.get(url)
    assert response.status_code == 401
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testPassword!'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    # The JWT must be present in the header
    response = CLIENT.get(url)
    assert response.status_code == 401

    # The user must have access to the map
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access('unittestuser', ['map'])

    # Success!
    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 200
    for key in response.json:
        layer = response.json[key]
        assert 'id' in layer
        assert 'type' in layer
        assert 'source' in layer
        assert layer['source']['type'] == 'geojson'
        assert type(layer['source']['data']) == dict
        assert 'paint' in layer
        assert 'description' in layer['source']['data']['features'][0]['properties']
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None
