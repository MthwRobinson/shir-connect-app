import pandas as pd
import pytest

from shir_connect.database.fake_news import FakeNews

@pytest.fixture
def fake_news():
    def read_table(name):
        if name in ['participants', 'attendees', 'members', 'orders']:
            return pd.DataFrame({'first_name': ['Jabber', 'Chester',
                                                'Missy', 'Cody', 
                                                'Jabber', 'Shenzy'],
                                 'last_name': ['Robinson', 'Shindhelm',
                                               'Robinson', 'Barky',
                                               'Robinson', 'Squawky']})

    fake_news = FakeNews()
    fake_news.database.read_table = lambda x: read_table(x)
    fake_news.database.update_column = lambda *args, **kwargs: 'Squawk!'
    return fake_news

def test_find_name(fake_news):
    df = pd.DataFrame({'first_name': ['Jabber', 'Jabber',
                                      'Chester', 'Squawkers'],
                       'last_name': ['Robinson', 'Robinson',
                                     'Shindhelm', 'Robinson']})
    subset = fake_news._find_name('Jabber', 'Robinson', df)
    assert len(subset) == 2

def test_get_person_tables(fake_news):
    fake_news._get_person_tables()
    tables = ['participants', 'attendees', 'members', 'order']
    for table in tables:
        df = getattr(fake_news, table)
        assert isinstance(df, pd.core.frame.DataFrame)
        assert len(df) == 6
