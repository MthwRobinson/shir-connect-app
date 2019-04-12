import os

import pandas as pd

from shir_connect.database.member_loader import MemberLoader

PATH = os.path.dirname(os.path.realpath(__file__))

class FakeDatabase:
    def __init__(self):
        pass

    def get_columns(self, table):
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
    class OtherFakeDB(FakeDatabase):
        def get_columns(self, table):
            if table == 'members':
                return ['koalas']
            else:
                return ['parrots', 'dogs']

    member_loader = MemberLoader()
    member_loader.database = FakeDatabase()
    assert member_loader.check_columns() is True

    member_loader.database = OtherFakeDB()
    assert member_loader.check_columns() is False
