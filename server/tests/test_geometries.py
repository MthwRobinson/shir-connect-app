from trs_dashboard.etl.geometries import Geometries

def test_load_zip_code():
    geo = Geometries()
    geo.load_zip_code(18914)
    feature = geo.database.get_item('geometries', 18914)
    assert type(feature['geometry']) == dict
    geo.database.delete_item('geometries', 18914)
    feature = geo.database.get_item('geometries', 18914)
    assert feature == None

def test_missing_zip_codes():
    geo = Geometries()
    missing = geo.missing_zip_codes()
    assert type(missing) == list
