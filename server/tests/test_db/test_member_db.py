import pandas as pd
import pytest

from shir_connect.database.members import Members, _clean_location_name

def test_get_demographics(monkeypatch):
    fake_response = pd.DataFrame({'age_group': ['Parrots', 'Penguins'],
                                 'total': [100, 262]})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)
    members = Members()
    demographics = members.get_demographics(new_members=True)
    assert demographics == [{'age_group': 'All', 'total': 362},
                            {'age_group': 'Parrots', 'total': 100},
                            {'age_group': 'Penguins', 'total': 262}]

def test_get_member_locations(monkeypatch):
    fake_response = pd.DataFrame({'location': ['Bird Town', 'Dog City',
                                               'Fishville'],
                                  'total': [500, 200, 100]})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)
    members = Members()

    locations = members.get_member_locations('city', limit=2)
    assert locations == [{'location': 'All', 'total': 800},
                         {'location': 'Bird Town', 'total': 500},
                         {'location': 'Dog', 'total': 200},
                         {'location': 'Other', 'total': 100}]

    locations = members.get_member_locations('city', limit=3,
                                             start='2018-01-01',
                                             end='2019-01-01')
    assert locations == [{'location': 'All', 'total': 800},
                         {'location': 'Bird Town', 'total': 500},
                         {'location': 'Dog', 'total': 200},
                         {'location': 'Fishville', 'total': 100}]

def test_get_households_by_year(monkeypatch):
    fake_response = pd.DataFrame({'total': [5000]})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)
    members = Members()
    demographics = members.get_resignations_by_year(2014, 2017)
    assert demographics == [{'year': '2014', 'count': '5000'},
                            {'year': '2015', 'count': '5000'},
                            {'year': '2016', 'count': '5000'},
                            {'year': '2017', 'count': '5000'}]

def test_get_households_by_year(monkeypatch):
    fake_response = pd.DataFrame({'total': [5000]})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)
    members = Members()
    demographics = members.get_households_by_year(2014, 2017)
    assert demographics == [{'year': '2014', 'count': '5000'},
                            {'year': '2015', 'count': '5000'},
                            {'year': '2016', 'count': '5000'},
                            {'year': '2017', 'count': '5000'}]

def test_get_households_types(monkeypatch):
    fake_response = pd.DataFrame({'member_type': ['Family', 'Individual'],
                                  'total': [200, 300]})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)
    members = Members()
    demographics = members.get_household_types()
    assert demographics == [{'member_type': 'All', 'total': 500},
                            {'member_type': 'Family', 'total': 200},
                            {'member_type': 'Individual', 'total': 300}]

def test_count_new_households(monkeypatch):
    fake_response = pd.DataFrame({'count': [200]})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)
    members = Members()
    count = members.count_new_households('2018-01-01', '2019-01-01')
    assert count == 200

def test_count_new_resignations(monkeypatch):
    fake_response = pd.DataFrame({'count': [200]})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)
    members = Members()
    count = members.count_new_resignations('2018-01-01', '2019-01-01')
    assert count == 200

def test_count_new_members(monkeypatch):
    fake_response = pd.DataFrame({'count': [200]})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)
    members = Members()
    count = members.count_new_members('2018-01-01', '2019-01-01')
    assert count == 200

def test_clean_location_name():
    assert _clean_location_name('Moo City') == 'Moo'
    assert _clean_location_name('Growl County') == 'Growl'
    assert _clean_location_name('District Of Columbia') == 'DC'


def test_upload_file(monkeypatch):
    fake_response = pd.DataFrame({'count': [200]})
    monkeypatch.setattr('pandas.read_csv', lambda *args, **kwargs: True)
    monkeypatch.setattr('pandas.read_excel', lambda *args, **kwargs: True)

    class FakeFile:
        def __init__(self, filename):
            self.filename = filename

    class FakeRequest:
        def __init__(self, extension):
            self.files = {'file': FakeFile('camels_rock' + extension)}

    class FakeMemberLoader:
        def __init__(self):
            pass

        def load(self, df):
            return True

        def load_resignations(self, df):
            return True

    members = Members()
    members.member_loader = FakeMemberLoader()

    good_upload = members.upload_file(FakeRequest('.csv'), 'members')
    assert good_upload == True
    
    good_upload = members.upload_file(FakeRequest('.xlsx'), 'resignations')
    assert good_upload == True
    
    good_upload = members.upload_file(FakeRequest('.xls'), 'resignations')
    assert good_upload == True
    
    good_upload = members.upload_file(FakeRequest('.txt'), 'resignations')
    assert good_upload == False

    good_upload = members.upload_file(FakeRequest('.csv'), 'penguins')
    assert good_upload == False
