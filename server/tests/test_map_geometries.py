from trs_dashboard.services.app import app
from trs_dashboard.services.user_management import UserManagement

CLIENT = app.test_client()

def test_zip_geometry():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testpassword')
    url = '/service/map/geometry/22102'
    
    response = CLIENT.get(url)
    assert response.status_code == 401
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testpassword'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    response = CLIENT.get(url)
    assert response.status_code == 401

    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 200
    assert 'id' in response.json
    assert 'type' in response.json
    assert 'source' in response.json
    assert response.json['source']['type'] == 'geojson'
    assert type(response.json['source']['data']) == dict
    assert 'paint' in response.json
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None

def test_zip_codes():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testpassword')
    url = '/service/map/zipcodes'
    
    response = CLIENT.get(url)
    assert response.status_code == 401
    
    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testpassword'
    ))
    assert response.status_code == 200
    assert type(response.json['jwt']) == str
    jwt = response.json['jwt']
    
    response = CLIENT.get(url)
    assert response.status_code == 401

    response = CLIENT.get(url, headers={'Authorization': 'Bearer %s'%(jwt)})
    assert response.status_code == 200
    assert type(response.json) == list
    
    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None
