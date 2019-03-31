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
    fake_news._get_person_tables()
    return fake_news

def test_find_name(fake_news):
    df = pd.DataFrame({'first_name': ['Jabber', 'Jabber',
                                      'Chester', 'Squawkers'],
                       'last_name': ['Robinson', 'Robinson',
                                     'Shindhelm', 'Robinson']})
    subset = fake_news._find_name('Jabber', 'Robinson', df)
    assert len(subset) == 2

def test_get_person_tables(fake_news):
    tables = ['participants', 'attendees', 'members', 'orders']
    for table in tables:
        df = getattr(fake_news, table)
        assert isinstance(df, pd.core.frame.DataFrame)
        assert len(df) == 6

def test_swap_attendees(fake_news):
    updated = fake_news._swap_people(first_name='Jabber', 
                                        last_name='Robinson',
                                        fake_first_name='Big',
                                        fake_last_name='Beak',
                                        fake_email='bird@flapping.net',
                                        table='attendees')
    assert updated == [0,4]

def test_swap_orders(fake_news):
    updated = fake_news._swap_people(first_name='Jabber', 
                                        last_name='Robinson',
                                        fake_first_name='Big',
                                        fake_last_name='Beak',
                                        fake_email='bird@flapping.net',
                                        table='orders')
    assert updated == [0,4]

def test_swap_members(fake_news):
    updated = fake_news._swap_people(first_name='Jabber', 
                                        last_name='Robinson',
                                        fake_first_name='Big',
                                        fake_last_name='Beak',
                                        fake_email='bird@flapping.net',
                                        table='members')
    assert updated == [0,4]

def test_fake_names(fake_news):
    updated = fake_news.fake_names()
    for key in updated:
        assert set(updated[key]) == {0,1,2,3,4,5}

def test_fake_venues(fake_news):
    updated = fake_news.fake_venues()
    assert set(updated) == {0,1,2,3}

def test_fake_events(fake_news):
    updated = fake_news.fake_events()
    assert set(updated) == {0,1,2,3}

def test_fake_data(fake_news):
    fake_news.build_fake_data()
