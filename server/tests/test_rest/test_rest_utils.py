import datetime

import shir_connect.services.utils as utils
from shir_connect.services.app import app

CLIENT = app.test_client()

@utils.demo_mode(['first_name','last_name',{'friends': ['name']}], demo=True)
def kangaroo():
    response = {
        'first_name': 'Matt',
        'last_name': 'Robinson',
        'occupation':'Penguin',
        'friends': [
            {'name': 'Nathan', 'occupation': 'Dinosaur'},
            {'name': 'Eric', 'occupation': 'Guy on a buffalo'}
        ]
    }
    return response

class FakeDatabase:
    def __init__(self):
        pass

    def get_item(self, table, item):
        if item == 'Jabber':
            modules =  ['events', 'members']
        else:
            modules = ['events']
        return {'modules': modules}

    def load_item(self, item, table):
        pass

class FakeRequest:
    def __init__(self):
        self.base_url = 'https://parrot.shirconnect.com'
        self.endpoint = 'parrots.squawk'
        self.host = 'parrot.shirconnect'
        self.host_url = 'https://parrot.shirconnect'
        self.query_string = b"?q=parrot"
        self.referrer = 'https://parrot.shirconnect.com'
        self.remote_addr = 'localhost'
        self.scheme = 'https'
        self.url = 'https://parrot.shirconnect.com/parrots'
        self.url_root = 'parrots'
        self.user_agent = 'parrot browser'

        self.environment = FakeRequestEnviron()

class FakeRequestEnviron:
    def __init__(self):
        pass

    def get(self, key, default):
        if key == 'HTTP_X_FORWARDED_FOR':
            return '1.2.3.4'
        else:
            return default

def test_demo_mode():
    response = kangaroo()
    assert response['first_name'] != 'Matt'
    assert response['last_name'] != 'Robinson'
    assert response['occupation'] == 'Penguin'
    assert response['friends'][0]['name'] != 'Nathan'
    assert response['friends'][0]['occupation'] == 'Dinosaur'
    assert response['friends'][1]['name'] != 'Eric'
    assert response['friends'][1]['occupation'] == 'Guy on a buffalo'

def test_validate_inputs():
    url = '/service/test/test'
    response = CLIENT.get(url)
    assert response.status_code == 422

    url = '/service/test/101'
    response = CLIENT.get(url)
    assert response.status_code == 422

    url = '/service/test/100'
    response = CLIENT.get(url)
    assert response.status_code == 200

    response = CLIENT.get(url + '?limit=25')
    assert response.status_code == 200
    response = CLIENT.get(url + '?limit=26')
    assert response.status_code == 422
    response = CLIENT.get(url + '?limit=carl')
    assert response.status_code == 422

    response = CLIENT.get(url + '?page=25')
    assert response.status_code == 200
    response = CLIENT.get(url + '?page=carl')
    assert response.status_code == 422

    response = CLIENT.get(url + '?order=desc')
    assert response.status_code == 200
    response = CLIENT.get(url + '?order=asc')
    assert response.status_code == 200
    response = CLIENT.get(url + '?order=carl')
    assert response.status_code == 422

    response = CLIENT.get(url + '?sort=blah')
    assert response.status_code == 200
    sort = 'carl!!' * 5
    response = CLIENT.get(url + '?sort=' + sort)
    assert response.status_code == 422

    response = CLIENT.get(url + '?q=blah')
    assert response.status_code == 200
    q = 'carl!!' * 10
    response = CLIENT.get(url + '?q=' + q)
    assert response.status_code == 422

    response = CLIENT.get(url + '?name=carl')
    assert response.status_code == 200
    response = CLIENT.get(url + '?name=carlaaaaa')
    assert response.status_code == 422

    response = CLIENT.get(url + '?count=carl')
    assert response.status_code == 422
    response = CLIENT.get(url + '?count=22')
    assert response.status_code == 422
    response = CLIENT.get(url + '?name=20')
    assert response.status_code == 200

def test_validate_int():
    value = 9
    valid = utils.validate_int(value, max_value=8)
    assert not valid
    valid = utils.validate_int(value, max_value=10)
    assert valid
    valid = utils.validate_int(value)
    assert valid

    value = 'koala'
    valid = utils.validate_int(value)
    assert not valid

def test_validate_date():
    value = '2018-01-01'
    assert utils.validate_date(value)

    value = 'big bad bird!'
    assert not utils.validate_date(value)

    value ='2018-01-01-conure'
    assert not utils.validate_date(value)

    value ='2018-01-0177'
    assert not utils.validate_date(value)

def test_check_access():
    fake_database = FakeDatabase()
    assert utils.check_access('Jabber', 'members', fake_database) == True
    assert utils.check_access('Chester', 'members', fake_database) == False

def test_log_request():
    fake_database = FakeDatabase()
    fake_request = FakeRequest()

    utils.log_request(fake_request, 'jabber', False, fake_database)

def test_count_bad_login_attempts():
    reset = datetime.datetime.now() - datetime.timedelta(days=20)
    count = utils.count_bad_login_attempts('Matt', 'dev', str(reset))
    assert isinstance(count, int)
