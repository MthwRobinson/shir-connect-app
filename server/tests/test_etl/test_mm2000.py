import os

import pandas as pd
import pytest

import shir_connect.etl.mm2000 as m

PATH = os.path.dirname(os.path.realpath(__file__))

class FakeDatabase:
    def __init__(self):
        self.schema = 'fake_schema'

    def get_columns(self, table):
        return ['parrots', 'dogs']

    def backup_table(self, table):
        pass

    def truncate_table(self, table):
        pass

    def load_item(self, *args):
        pass

    def update_column(self, *args, **kwargs):
        pass

    def refresh_view(self, view):
        pass

    def refresh_views(self, *args, **kwargs):
        pass

    def revert_table(self, table):
        pass

    def run_query(self, *args, **kwargs):
        pass

class OtherFakeDB(FakeDatabase):
    def get_columns(self, table):
        if table == 'members':
            return ['koalas']
        else:
            return ['parrots', 'dogs']

def test_error_raises_with_bad_resign_columns():
    mm2000 = m.MM2000(database=FakeDatabase())

    df = pd.DataFrame({'Camel ID': [1,2],
                       'Resign Date': ['2018-01-01', '2019-01-01'],
                       'Resignation Reason': ['Too many bears', 'Not enough birds']})
    with pytest.raises(ValueError):
        mm2000.load_resignations(df)
    
    df = pd.DataFrame({'Member ID': [1,2],
                       'Caravan Date': ['2018-01-01', '2019-01-01'],
                       'Resignation Reason': ['Too many bears', 'Not enough birds']})
    with pytest.raises(ValueError):
        mm2000.load_resignations(df)

def test_resignations_load():
    mm2000 = m.MM2000(database=FakeDatabase())
    
    df = pd.DataFrame({'Member ID': [867, 6309],
                       'Resign Date': ['2018-01-01', '2019-01-01'],
                       'Resignation Reason': ['Too many bears', 'Not enough birds'],
                       'Comment1': ['Not enough camels', 'Too many lizards!'],
                       'Comment2': ['Rejoined', 'Angry bird!']})
    mm2000.load_resignations(df)

def test_resignation_reason():
    category = m._find_resignation_reason("I moved")
    assert category == 'Moved'

    category = m._find_resignation_reason("Shul is too far")
    assert category == 'Too Far'
    
    category = m._find_resignation_reason("Don't ever come")
    assert category == 'Inactive'

    category = m._find_resignation_reason("Deceased")
    assert category == 'Deceased'

    category = m._find_resignation_reason("Bar mitzvah over")
    assert category == 'Post Bar/Bat Mitzvah'

    category = m._find_resignation_reason("Something else")
    assert category == 'Other'

def test_mm2000():
    filename = os.path.join(PATH, '..', 'data/mm2000_upload_test.csv')
    df = pd.read_csv(filename, encoding='latin-1')
    mm2000 = m.MM2000()
    items = mm2000.parse_mm2000(df)
    for item in items:
        assert 'id' in item
        assert 'first_name' in item
        assert 'last_name' in item

def test_check_columns():
    mm2000 = m.MM2000()
    mm2000.database = FakeDatabase()
    assert mm2000.check_columns() is True

    mm2000.database = OtherFakeDB()
    assert mm2000.check_columns() is False

def test_add_postal_code():
    item = {'postal_code': '55000-131'}
    assert m._parse_postal_code(item) == {'postal_code': '55000'}
    item = {'postal_code': '222-13'}
    assert m._parse_postal_code(item) == {'postal_code': None}

def test_parse_mm2000_date():
    item = {'birth_date': '0000-01-01'}
    assert m._parse_mm2000_date(item, 'birth_date') == {'birth_date': None}
    
    item = {'birth_date': '1999-01-01'}
    assert m._parse_mm2000_date(item, 'birth_date') == {'birth_date': '1999-01-01'}

def test_parse_mm2000_active():
    item = {'member_type': None}
    assert m._check_mm2000_active(item) == {'member_type': None,
                                           'active_member': False}
 
    item = {'member_type': 'MEMFAM'}
    assert m._check_mm2000_active(item) == {'member_type': 'MEMFAM',
                                           'active_member': True}
 
    item = {'member_type': 'Bird'}
    assert m._check_mm2000_active(item) == {'member_type': 'Bird',
                                           'active_member': False}
    
    item = {'member_type': 'STAFF'}
    assert m._check_mm2000_active(item) == {'member_type': 'STAFF',
                                           'active_member': True}

def test_mm2000_load():
    mm2000 = m.MM2000(database=FakeDatabase())
    mm2000.parse_mm2000 = lambda *args, **kwargs: ['item1', 'item2']
    
    mm2000.check_columns = lambda *args, **kwargs: True
    df = pd.DataFrame({'MemberID': [1,2], 'Name': ['Carl', 'Carla']})
    load_status = mm2000.load(df)
    assert load_status == True

    mm2000.check_columns = lambda *args, **kwargs: False
    df = pd.DataFrame({'MemberID': [1,2], 'Name': ['Carl', 'Carla']})
    load_status = mm2000.load(df)
    assert load_status == False
