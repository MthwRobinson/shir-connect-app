from trs_dashboard.etl.data_loader import DataLoader

def test_load_event():
    data_loader = DataLoader()
    data_loader.database.delete_item('test_event_123', 'events')
    event = data_loader.eventbrite.get_event(1059379633)
    event['id'] = 'test_event_123'
    
    data_loader.load_event(event)
    test_event = data_loader.database.get_item('test_event_123', 'events')
    assert test_event['id'] == 'test_event_123'

    data_loader.database.delete_item('test_event_123', 'events')
    test_event = data_loader.database.get_item('test_event_123', 'events')
    assert test_event == None
