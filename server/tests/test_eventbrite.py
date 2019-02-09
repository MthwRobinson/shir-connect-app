from shir_connect.etl.eventbrite import Eventbrite

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

def test_event():
    eventbrite = Eventbrite()
    event = eventbrite.get_event(40146904472)
    assert event['id'] == '40146904472'

def test_attendees():
    eventbrite = Eventbrite()
    event = eventbrite.get_attendees(1059379633)
    assert len(event['attendees']) > 0

def test_order():
    eventbrite = Eventbrite()
    order = eventbrite.get_order(705451451)
    assert type(order) == dict

def test_venue():
    eventbrite = Eventbrite()
    venue = eventbrite.get_venue(26449992)
    assert type(venue) == dict
