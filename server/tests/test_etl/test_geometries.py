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

def test_get_zipcode_data():
    geo = Geometries()
    geo.search = FakeSearchEngine()
    data = geo.get_zipcode_data('12345')
    assert data == {'major_city': 'Birdtown',
                    'county': 'Conure County',
                     'state': 'VA'}
    data = geo.get_zipcode_data('bad zip')
    assert not data
