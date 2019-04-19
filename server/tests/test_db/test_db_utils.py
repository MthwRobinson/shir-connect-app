import pytest

import shir_connect.database.utils as utils

def test_build_age_groups(monkeypatch):
    FAKE_AGE_GROUPS = {'18-23': {'min': 18, 'max': 23}, 
                       '35-50': {'min': 35, 'max': 50}}
    monkeypatch.setattr('shir_connect.configuration.AGE_GROUPS', 
                        FAKE_AGE_GROUPS)
    sql = utils.build_age_groups()
    assert "'18-23'" in sql
    assert "'35-50'" in sql
    assert "'Unknown'" in sql

def test_sort_results():
    results = [{'parrot': 'Conure'}, {'parrot': 'All'},
               {'parrot': 'Other'}, {'parrot': 'Macaw'}]

    ordered_results = utils.sort_results(results, 'parrot')
    assert ordered_results == [{'parrot': 'All'}, {'parrot': 'Conure'},
                               {'parrot': 'Macaw'}, {'parrot': 'Other'}]
    
    ordered_results = utils.sort_results(results, 'parrot', reverse=True)
    assert ordered_results == [{'parrot': 'All'}, {'parrot': 'Macaw'},
                               {'parrot': 'Conure'}, {'parrot': 'Other'}]
