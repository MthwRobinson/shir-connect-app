import pandas as pd
import pytest

from shir_connect.etl.mm2000 import MM2000

class FakeDatabase:
    def __init__(self):
        pass

    def update_column(self, *args, **kwargs):
        pass

    def refresh_views(self, *args, **kwargs):
        pass

    def run_query(self, *args, **kwargs):
        pass

def test_error_raises_with_bad_resign_columns():
    mm2000 = MM2000(database=FakeDatabase())

    df = pd.DataFrame({'Camel ID': [1,2],
                       'Resign Date': ['2018-01-01', '2019-01-01']})
    with pytest.raises(ValueError):
        mm2000.load_resignations(df)
    
    df = pd.DataFrame({'Member ID': [1,2],
                       'Caravan Date': ['2018-01-01', '2019-01-01']})
    with pytest.raises(ValueError):
        mm2000.load_resignations(df)

def test_resignations_load():
    mm2000 = MM2000(database=FakeDatabase())
    
    df = pd.DataFrame({'Member ID': [867, 6309],
                       'Resign Date': ['2018-01-01', '2019-01-01']})
    mm2000.load_resignations(df)
