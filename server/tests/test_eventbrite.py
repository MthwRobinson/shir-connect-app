from trs_dashboard.etl.eventbrite import Eventbrite

def test_token():
    eventbrite = Eventbrite()
    response = eventbrite.get_token_info()
    assert response.status_code == 200

def test_events():
    eventbrite = Eventbrite()
    events = eventbrite.get_events(start='2018-07-01')
    assert type(events['events']) == list
    event = events['events'][0]
    assert event['start']['local'] >= '2018-07-01'
