from trs_dashboard.etl.data_loader import DataLoader

def test_load_event():
    data_loader = DataLoader()
    data_loader.database.delete_item('events', 'test_event')
    event = data_loader.eventbrite.get_event(1059379633)
    event['id'] = 'test_event'
    
    data_loader.load_event(event)
    test_event = data_loader.database.get_item('events', 'test_event')
    assert test_event['id'] == 'test_event'

    data_loader.database.delete_item('events', 'test_event')
    test_event = data_loader.database.get_item('events', 'test_event')
    assert test_event == None

def test_load_attendee():
    data_loader = DataLoader()
    data_loader.database.delete_item('attendees', 'test_attendee')
    attendees = data_loader.eventbrite.get_attendees(1059379633)
    attendee = attendees['attendees'][0]
    attendee['id'] = 'test_attendee'

    data_loader.load_attendee(attendee)
    test_attendee = data_loader.database.get_item('attendees', 'test_attendee')
    assert test_attendee['id'] == 'test_attendee'
    
    data_loader.database.delete_item('attendees', 'test_attendee')
    test_attendee = data_loader.database.get_item('attendees', 'test_attendee')
    assert test_attendee == None

def test_load_order():
    data_loader = DataLoader()
    data_loader.database.delete_item('orders', 'test_order')
    order = data_loader.eventbrite.get_order(23271451)
    order['id'] = 'test_order'

    data_loader.load_order(order)
    test_order = data_loader.database.get_item('orders', 'test_order')
    assert test_order['id'] == 'test_order'

    data_loader.database.delete_item('orders', 'test_order')
    test_order = data_loader.database.get_item('orders', 'test_order')
    assert test_order == None
