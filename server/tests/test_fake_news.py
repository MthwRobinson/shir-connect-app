import pandas as pd
import pytest

from shir_connect.database.fake_news import FakeNews

@pytest.fixture
def fake_news():
    fake_news = FakeNews()
    fake_news.database.update_column = lambda *args, **kwargs: 'Squawk!'
    return fake_news

def test_find_name(fake_news):
    df = pd.DataFrame({'first_name': ['Jabber', 'Jabber',
                                      'Chester', 'Squawkers'],
                       'last_name': ['Robinson', 'Robinson',
                                     'Shindhelm', 'Robinson']})
    subset = fake_news._find_name('Jabber', 'Robinson', df)
    assert len(subset) == 2
