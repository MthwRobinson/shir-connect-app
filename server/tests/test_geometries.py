import pytest

from shir_connect.etl.geometries import Geometries

class FakeSearchEngine:
    def __init__(self):
        pass

    def by_zipcode(self, zipcode):
        if zipcode == '12345':
            return FakeResult('Birdtown', 'Conure County', 'VA', zipcode)
        else:
            return FakeResult(None, None, None, None)

class FakeResult:
    def __init__(self, major_city, county, state, zipcode):
        self.major_city = major_city
        self.county = county
        self.state=state
        self.zipcode = zipcode

    def to_dict(self):
        return {'major_city': self.major_city,
                'county': self.county,
                'state': self.state}

class FakeDatabase:
    def __init__(self):
        pass

    def update_column(self, *args, **kwargs):
        pass

def test_load_zip_code():
    geo = Geometries()
    geo.load_zip_code(99504)
    feature = geo.database.get_item('geometries', 99504)
    assert type(feature['geometry']) == dict
    geo.database.delete_item('geometries', 99504)
    feature = geo.database.get_item('geometries', 99504)
    assert feature == None

def test_missing_zip_codes():
    geo = Geometries()
    missing = geo.missing_zip_codes()
    assert type(missing) == list

def test_missing_locations():
    geo = Geometries()
    missing = geo.missing_locations()
    assert type(missing) == list

def test_get_zipcode_data():
    geo = Geometries()
    geo.search = FakeSearchEngine()
    data = geo.get_zipcode_data('12345')
    assert data == {'major_city': 'Birdtown',
                    'county': 'Conure County',
                     'state': 'VA'}
    data = geo.get_zipcode_data('bad zip')
    assert not data

def test_load_locations():
    geo = Geometries()
    geo.database = FakeDatabase()
    geo.search = FakeSearchEngine()
    def fake_missing_locations(*args, **kwargs):
        return ['12345']
    geo.missing_locations = fake_missing_locations
    geo.load_locations()
