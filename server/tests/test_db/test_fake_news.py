import pandas as pd
import pytest

from shir_connect.database.fake_news import FakeNews

class FakeDatabase:
    def __init__(self):
        self.schema = 'fake_schema'
        self.connection = 'fake_connection'

    def update_column(self, *args, **kwargs):
        pass

    def refresh_views(self, *args, **kwargs):
        pass

def test_fake_names(monkeypatch):
    fake_response = pd.DataFrame({'id': ['camel1', 'camel2']})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)
    fake_news = FakeNews()
    fake_news.database = FakeDatabase()
    updated = fake_news.fake_names()

def test_fake_venues(monkeypatch):
    fake_response = pd.DataFrame({'id': ['camel1', 'camel2']})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)
    fake_news = FakeNews()
    fake_news.database = FakeDatabase()
    fake_news.fake_venues()

def test_fake_events(monkeypatch):
    fake_response = pd.DataFrame({'id': ['camel1', 'camel2']})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)
    fake_news = FakeNews()
    fake_news.database = FakeDatabase()
    fake_news.fake_events()

def test_fake_data(monkeypatch):
    fake_response = pd.DataFrame({'id': ['camel1', 'camel2']})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)
    fake_news = FakeNews()
    fake_news.database = FakeDatabase()
    fake_news.build_fake_data()
