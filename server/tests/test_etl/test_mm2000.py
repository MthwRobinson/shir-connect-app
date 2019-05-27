import pandas as pd
import pytest

import shir_connect.etl.mm2000 as m

class FakeDatabase:
    def __init__(self):
        self.schema = 'fake_schema'

    def update_column(self, *args, **kwargs):
        pass

    def refresh_views(self, *args, **kwargs):
        pass

    def run_query(self, *args, **kwargs):
        pass

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
                       'Resignation Reason': ['Too many bears', 'Not enough birds']})
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
