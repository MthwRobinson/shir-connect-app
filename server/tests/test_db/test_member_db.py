import pandas as pd
import pytest

from shir_connect.database.members import Members

def test_get_demographics(monkeypatch):
    fake_response = pd.DataFrame({'age_group': ['Parrots', 'Penguins'],
                                 'total': [100, 262]})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)
    members = Members()
    demographics = members.get_demographics()
    assert demographics == [{'age_group': 'All', 'total': 362},
                            {'age_group': 'Penguins', 'total': 262},
                            {'age_group': 'Parrots', 'total': 100}]

def test_get_member_locations(monkeypatch):
    fake_response = pd.DataFrame({'location': ['Bird Town', 'Dog City',
                                               'Fishville'],
                                  'total': [500, 200, 100]})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)
    members = Members()
    locations = members.get_member_locations('city', limit=2)
    assert locations == [{'location': 'All', 'total': 800},
                         {'location': 'Bird Town', 'total': 500},
                         {'location': 'Dog City', 'total': 200},
                         {'location': 'Other', 'total': 100}]
