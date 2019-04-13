import pytest

import shir_connect.database.utils as utils

def test_build_age_groups(monkeypatch):
    FAKE_AGE_GROUPS = {'18-23': {'min': 18, 'max': 23}, 
                       '35-50': {'min': 35, 'max': 50}}
    monkeypatch.setattr('shir_connect.configuration.AGE_GROUPS', 
                        FAKE_AGE_GROUPS)
    sql = utils.build_age_groups()
    expected = " CASE WHEN age >= 18 AND age < 23 THEN '18-23'"
    expected += " WHEN age >= 35 AND age < 50 THEN '35-50'"
    expected += " ELSE 'Unknown' END as age_group "
    assert sql.lower().split() == expected.lower().split()
