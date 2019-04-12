import os

import pandas as pd
import pytest

from shir_connect.database.member_loader import MemberLoader
import shir_connect.database.member_loader as ml

PATH = os.path.dirname(os.path.realpath(__file__))

class FakeDatabase:
    def __init__(self):
        pass

    def get_columns(self, table):
        return ['parrots', 'dogs']

    def backup_table(self, table):
        pass

    def truncate_table(self, table):
        pass

    def load_item(self, *args):
        pass

    def refresh_view(self, view):
        pass

    def revert_table(self, table):
        pass

class OtherFakeDB(FakeDatabase):
    def get_columns(self, table):
        if table == 'members':
            return ['koalas']
        else:
            return ['parrots', 'dogs']

def test_mm2000():
    filename = os.path.join(PATH, '..', 'data/mm2000_upload_test.csv')
    df = pd.read_csv(filename, encoding='latin-1')
    member_loader = MemberLoader()
    items = member_loader.parse_mm2000(df)
    for item in items:
        assert 'id' in item
        assert 'first_name' in item
        assert 'last_name' in item

def test_check_columns():
    member_loader = MemberLoader()
    member_loader.database = FakeDatabase()
    assert member_loader.check_columns() is True

    member_loader.database = OtherFakeDB()
    assert member_loader.check_columns() is False

def test_load():
    filename = os.path.join(PATH, '..', 'data/mm2000_upload_test.csv')
    df = pd.read_csv(filename, encoding='latin-1')

    member_loader = MemberLoader()
    member_loader.database = FakeDatabase()
    loaded = member_loader.load(df, source='MM2000')
    assert loaded is True

    member_loader.database = OtherFakeDB()
    with pytest.warns(None):
        loaded = member_loader.load(df, source='MM2000')
    assert loaded is False

def test_add_postal_code():
    item = {'postal_code': '55000-131'}
    assert ml._parse_postal_code(item) == {'postal_code': '55000'}
    item = {'postal_code': '222-13'}
    assert ml._parse_postal_code(item) == {'postal_code': None}

def test_parse_mm2000_date():
    item = {'birth_date': '0000-01-01'}
    assert ml._parse_mm2000_date(item, 'birth_date') == {'birth_date': None}
    
    item = {'birth_date': '1999-01-01'}
    assert ml._parse_mm2000_date(item, 'birth_date') == {'birth_date': '1999-01-01'}

def test_parse_mm2000_active():
    item = {'member_type': None}
    assert ml._check_mm2000_active(item) == {'member_type': None,
                                           'active_member': False}
 
    item = {'member_type': 'MEMFAM'}
    assert ml._check_mm2000_active(item) == {'member_type': 'MEMFAM',
                                           'active_member': True}
 
    item = {'member_type': 'Bird'}
    assert ml._check_mm2000_active(item) == {'member_type': 'Bird', 
                                           'active_member': False}
