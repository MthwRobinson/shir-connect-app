from trs_dashboard.etl.eventbrite import Eventbrite

def test_token():
    eventbrite = Eventbrite()
    response = eventbrite.get_token_info()
    assert response.status_code == 200
