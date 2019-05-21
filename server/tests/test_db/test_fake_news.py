import pandas as pd
import pytest

from shir_connect.database.fake_news import FakeNews

@pytest.fixture
def fake_news():
    def read_table(name):
        if name in ['participants', 'attendees', 'members', 'orders']:
            return pd.DataFrame({'id': [0,1,2,3,4,5],
                                 'first_name': ['Jabber', 'Chester',
                                                'Missy', 'Cody', 
                                                'Jabber', 'Shenzy'],
                                 'last_name': ['Robinson', 'Shindhelm',
                                               'Robinson', 'Barky',
                                               'Robinson', 'Squawky']})
        elif name == 'venues':
            return pd.DataFrame({'id': [0,1,2,3],
                                 'name': ['Squawk', 'Bark', 'Moo', 'Quack']})
        elif name == 'events':
            return pd.DataFrame({'id': [0,1,2,3],
                                 'name': ['Rodef 2100: Squawk', 'Bark', 
                                          'WOTRS: hooray', 'Quack'],
                                 'description': ['Lots of flappy birds!',
                                                 'Lots of barky dogs!',
                                                 'Lots friendly camels!',
                                                 'Lots of hungry ducks!']})

    fake_news = FakeNews()
    fake_news.database.read_table = lambda x: read_table(x)
    fake_news.database.update_column = lambda *args, **kwargs: 'Squawk!'
    fake_news.database.refresh_views = lambda *args, **kwargs: 'Bark!'
    return fake_news

class FakeDatabase:
    def __init__(self):
        self.schema = 'fake_schema'
        self.connection = 'fake_connection'

    def update_column(self, *args, **kwargs):
        pass

def test_fake_names(monkeypatch):
    fake_response = pd.DataFrame({'id': ['camel1', 'camel2']})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)
    fake_news = FakeNews()
    fake_news.database = FakeDatabase()
    updated = fake_news.fake_names()

def test_fake_venues(fake_news):
    updated = fake_news.fake_venues()
    assert set(updated) == {0,1,2,3}

def test_fake_events(fake_news):
    updated = fake_news.fake_events()
    assert set(updated) == {0,1,2,3}

def test_fake_data(fake_news):
    fake_news.build_fake_data()
