from io import StringIO

import pandas as pd

from trs_dashboard.services.app import app
from trs_dashboard.services.user_management import UserManagement

CLIENT = app.test_client()

def test_export_event_aggregates():
    user_management = UserManagement()
    user_management.delete_user('unittestuser')
    user_management.add_user('unittestuser', 'testpassword')

    response = CLIENT.post('/service/user/authenticate', json=dict(
        username='unittestuser',
        password='testpassword'
    ))
    assert response.status_code == 200
    jwt = response.json['jwt']

    response = CLIENT.get('/service/export/event_aggregates', headers={
        'Authorization': 'Bearer %s'%(jwt)
    })
    assert response.status_code == 200

    csv = StringIO(response.data.decode('utf-8'))
    df = pd.read_csv(csv)
    assert len(df) > 0

    user_management.delete_user('unittestuser')
    user = user_management.get_user('unittestuser')
    assert user == None
