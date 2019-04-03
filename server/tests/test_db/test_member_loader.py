import os

import pandas as pd

from shir_connect.database.member_loader import MemberLoader

PATH = os.path.dirname(os.path.realpath(__file__))

def test_mm2000():
    filename = os.path.join(PATH, '..', 'data/mm2000_upload_test.csv')
    df = pd.read_csv(filename, encoding='latin-1')
    member_loader = MemberLoader()
    items = member_loader.parse_mm2000(df)
    for item in items:
        assert 'id' in item
        assert 'first_name' in item
        assert 'last_name' in item
