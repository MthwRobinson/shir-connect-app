import pytest

from shir_connect.database.events import Events

class FakeDatabase:
    def __init__(self):
        pass

    def count_rows(self, *args, **kwargs):
        query = kwargs.get('query')
        if not query:
            return 50210
        elif query[1] == 'Conures':
            return 22
        elif query[1] == 'African Greys':
            return 17
        else:
            return 8675309

def test_count_events():
    events = Events()
    events.database = FakeDatabase()
    assert events.count_events(start="'2017-01-01'", 
                               end="'2018-01-01'") == 50210
    assert events.count_events(start="'2017-01-01'", 
                               end="'2018-01-01'",
                               query='parrot') == 8675309 

def test_event_group_counts(monkeypatch):
    monkeypatch.setattr('shir_connect.configuration.EVENT_GROUPS',
                        ['Conures', 'African Greys'])
    events = Events()
    events.database = FakeDatabase()
    counts = events.event_group_counts("'2017-01-01'", "'2018-01-01'")
    assert counts['All'] == 50210
    assert counts['Conures'] == 22
    assert counts['African Greys'] == 17
