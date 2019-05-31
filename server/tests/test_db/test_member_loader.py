import os

import pandas as pd
import pytest

from shir_connect.database.member_loader import MemberLoader
import shir_connect.database.member_loader as ml

PATH = os.path.dirname(os.path.realpath(__file__))

class FakeLoader:
    def __init__(self):
        pass

    def load(self, df):
        return True

    def load_resignations(self, df):
        return True

class OtherFakeLoader:
    def __init__(self):
        pass

    def load(self, df):
        raise ValueError

    def load_resignations(self, df):
        raise ValueError

def test_load():
    filename = os.path.join(PATH, '..', 'data/mm2000_upload_test.csv')
    df = pd.read_csv(filename, encoding='latin-1')

    member_loader = MemberLoader()
    member_loader.mm2000 = FakeLoader()
    loaded = member_loader.load(df, source='MM2000')
    assert loaded is True

    member_loader.mm2000 = OtherFakeLoader()
    with pytest.warns(None):
        loaded = member_loader.load(df, source='MM2000')
    assert loaded is False


def test_load_resignations():
    member_loader = MemberLoader()


    member_loader.mm2000 = FakeLoader()
    df = pd.DataFrame({'Camels': [1, 2],
                       'Resign Date': ['2018-01-01', '2019-01-01'],
                       'Resignation Reason': ['Not enough camels', 'Too many snakes']})
    good_upload = member_loader.load_resignations(df)
    assert good_upload == True

    member_loader.mm2000 = OtherFakeLoader()
    df = pd.DataFrame({'Member ID': [1, 2],
                       'Resign Date': ['2018-01-01', '2019-01-01'],
                       'Resignation Reason': ['Not enough camels', 'Too many snakes']})
    good_upload = member_loader.load_resignations(df)
    assert good_upload == False
