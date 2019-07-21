import datetime

from shir_connect.etl.eventbrite import Eventbrite, EventbriteLoader

def test_eventbrite_token():
    eventbrite = Eventbrite()
    response = eventbrite.get_token_info()
    assert response.status_code == 200

def test_eventbrite_events():
    eventbrite = Eventbrite()
    events = eventbrite.get_events(1358538665, start='2018-07-01')
    assert type(events['events']) == list
    event = events['events'][0]
    assert event['start']['local'] >= '2018-07-01'

def test_eventbrite_event():
    eventbrite = Eventbrite()
    event = eventbrite.get_event(40146904472)
    assert event['id'] == '40146904472'

def test_eventbrite_attendees():
    eventbrite = Eventbrite()
    event = eventbrite.get_attendees(1059379633)
    assert len(event['attendees']) > 0

def test_eventbrite_order():
    eventbrite = Eventbrite()
    order = eventbrite.get_order(705451451)
    assert type(order) == dict

def test_eventbrite_venue():
    eventbrite = Eventbrite()
    venue = eventbrite.get_venue(26449992)
    assert type(venue) == dict

######################################
# Tests for the Eventbrite dataloader
######################################

def test_eventbrite_data_loader():
    eventbrite_loader = EventbriteLoader()
    eventbrite_loader.run(test=True)

def test_eventbrite_load_event():
    eventbrite_loader = EventbriteLoader()
    eventbrite_loader.database.delete_item('events', 'test_event')
    event = eventbrite_loader.eventbrite.get_event(1059379633)
    event['id'] = 'test_event'

    eventbrite_loader.load_event(event)
    test_event = eventbrite_loader.database.get_item('events', 'test_event')
    assert test_event['id'] == 'test_event'
    last_event_date = eventbrite_loader.database.last_event_date()
    assert isinstance(last_event_date, datetime.datetime)

    eventbrite_loader.database.delete_item('events', 'test_event')
    test_event = eventbrite_loader.database.get_item('events', 'test_event')
    assert test_event == None

def test_eventbrite_load_attendee():
    eventbrite_loader = EventbriteLoader()
    eventbrite_loader.database.delete_item('attendees', 'test_attendee')
    attendees = eventbrite_loader.eventbrite.get_attendees(1059379633)
    attendee = attendees['attendees'][0]
    attendee['id'] = 'test_attendee'

    eventbrite_loader.load_attendee(attendee)
    test_attendee = eventbrite_loader.database.get_item('attendees', 'test_attendee')
    assert test_attendee['id'] == 'test_attendee'

    eventbrite_loader.database.delete_item('attendees', 'test_attendee')
    test_attendee = eventbrite_loader.database.get_item('attendees', 'test_attendee')
    assert test_attendee == None

def test_eventbrite_load_order():
    eventbrite_loader = EventbriteLoader()
    eventbrite_loader.database.delete_item('orders', 'test_order')
    order = eventbrite_loader.eventbrite.get_order(23271451)
    order['id'] = 'test_order'

    eventbrite_loader.load_order(order)
    test_order = eventbrite_loader.database.get_item('orders', 'test_order')
    assert test_order['id'] == 'test_order'

    eventbrite_loader.database.delete_item('orders', 'test_order')
    test_order = eventbrite_loader.database.get_item('orders', 'test_order')
    assert test_order == None
