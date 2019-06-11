"""Utilities for ETL processes"""
import datetime

def check_age(birth_date, min_age=18):
    """Checks to see if the member is too young
    for us to store their data in the database.
    Returns True if a null value is passed
    for birth_date.

    Parameters
    ----------
    date: string
        the birth date, in YYYY-MM-DD format
    min_age: int

    Returns
    -------
    too_young: boolean
    """
    if birth_date:
        now = datetime.datetime.now()
        max_bday = now - datetime.timedelta(days=365*min_age)
        if str(birth_date)[:10] > str(max_bday)[:10]:
            too_young = True
        else:
            too_young = False
    else:
        too_young = False
    return too_young
