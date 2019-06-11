import datetime

import shir_connect.etl.utils as utils

def test_check_age():
    old_enough = datetime.datetime.now() - datetime.timedelta(days=365*20)
    too_young = utils.check_age(old_enough)
    assert too_young == False
    
    not_old_enough = datetime.datetime.now() - datetime.timedelta(days=365*12)
    too_young = utils.check_age(not_old_enough)
    assert too_young == True

    assert utils.check_age(None) == False
