import pandas as pd
import pytest

from shir_connect.database.members import Members

def test_get_demographics(monkeypatch):
    fake_response = pd.DataFrame({'age_group': ['Parrots', 'Penguins'],
                                 'total': [100, 262]})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)
    members = Members()
    demographics = members.get_demographics()
    assert demographics == {'Parrots': 100, 'Penguins': 262, 'All': 362}
