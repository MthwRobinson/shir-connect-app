import shir_connect.configuration as conf
from shir_connect.database.user_management import UserManagement
import shir_connect.services.utils as utils

def run_url_tests(url, client, access=[]):
    user_management = UserManagement()
    user_management.delete_user(conf.TEST_USER)
    user_management.add_user(conf.TEST_USER, conf.TEST_PASSWORD)

    # User must be authenticated
    response = client.get(url)
    assert response.status_code == 401

    response = client.post('/service/user/authenticate', json=dict(
        username=conf.TEST_USER,
        password=conf.TEST_PASSWORD
    ))
    assert response.status_code == 200
    jwt = utils._get_cookie_from_response(response, 'access_token_cookie')

    # The user must have access to the correct modules
    response = client.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 403
    user_management.update_access(conf.TEST_USER, access)
    
    response = client.get(url, headers={'Cookies': 'access_token_cookie=%s'%(jwt)})
    assert response.status_code == 200

    url = '/service/user/logout'
    response = client.post(url)
    assert response.status_code == 200

    user_management.delete_user(conf.TEST_USER)
    user = user_management.get_user(conf.TEST_USER)
    assert not user
