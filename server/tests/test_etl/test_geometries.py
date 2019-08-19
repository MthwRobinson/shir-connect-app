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
                'state': self.state,
                'zipcode': self.zipcode}

class FakeDatabase:
    def __init__(self):
        pass

    def update_column(self, *args, **kwargs):
        pass

    def delete_item(self, *args, **kwargs):
        pass

    def load_item(self, *args, **kwargs):
        pass

class FakeResponse:
    def __init__(self):
        self.status_code = 200
        self.text = {'species': 'parrot'}

def test_get_zipcode_data():
    geo = Geometries()
    geo.search = FakeSearchEngine()
    data = geo.get_zipcode_data('12345')
    assert data == {'major_city': 'Birdtown',
                    'county': 'Conure County',
                     'state': 'VA',
                     'zipcode': '12345'}
    data = geo.get_zipcode_data('bad zip')
    assert not data

def test_load_all_zip_codes():
    geo = Geometries()
    geo.database = FakeDatabase()
    geo.get_all_zip_codes = lambda *args, **kwargs: ['22102']
    geo.load_all_zip_codes()

def test_get_all_zip_codes():
    geo = Geometries()
    geo.search = FakeSearchEngine()
    valid_zip_codes = geo.get_all_zip_codes()
    assert valid_zip_codes == ['12345']
