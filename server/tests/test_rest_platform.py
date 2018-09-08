from trs_dashboard.services.app import app

CLIENT = app.test_client()

def test_rest_platform():
    response = CLIENT.get('/service/test')
    assert response.json['status'] == 'success'
