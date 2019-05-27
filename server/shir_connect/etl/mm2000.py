"""Class for handling interaction with the MM2000 CRM.
Include functionality to:
    1. Upload MM2000 membership information
    2. Upload MM2000 resignation information
"""
import logging
import os

import daiquiri
import numpy as np
import pandas as pd
import yaml

from shir_connect.database.database import Database

class MM2000:
    def __init__(self, database=None):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        # Load column mapping configs
        self.path = os.path.dirname(os.path.realpath(__file__))
        filename = self.path + '/../database/member_columns.yml'
        with open(filename, 'r') as f:
            self.column_mapping = yaml.safe_load(f)
        self.database = Database() if not database else database

    ###########################################
    # Methods for handling MM2000 resignations
    ###########################################

    def load_resignations(self, df):
        """Loads MM2000 resignation data into the database."""
        _validate_resignation_data(df)
        # Map the file column names to the databse column names
        df = df.rename(columns=self.column_mapping['MM2000 Resignations'])
        # Drop any rows where the resignation date is null
        df = df.dropna(axis=0, how='any', subset=['resignation_date'])
        for i in df.index:
            member = dict(df.loc[i])
            resignation_date = str(member['resignation_date'])[:10]
            sql = """
                UPDATE {schema}.members
                SET resignation_date = '{resignation_date}'
                WHERE (household_id = '{member_id}'
                       OR id = '{member_id}')
            """.format(schema=self.database.schema,
                       resignation_date=resignation_date,
                       member_id=member['id'])
            self.database.run_query(sql)

            reason = _find_resignation_reason(member['resignation_reason'])
            sql = """
                UPDATE {schema}.members
                SET resignation_reason = '{reason}'
                WHERE (household_id = '{member_id}'
                       OR id = '{member_id}')
            """.format(schema=self.database.schema,
                       reason=reason,
                       member_id=member['id'])
            self.database.run_query(sql)

        self.database.refresh_views()
        

def _validate_resignation_data(df):
    """Checks to make sure the format of the MM2000 resignation
    date is correct. The file needs to have a Member ID columns
    and a Resign Date column."""
    if 'Member ID' not in df.columns:
        raise ValueError('Member ID is missing from the resignation file.')
    if 'Resign Date' not in df.columns:
        raise ValueError('Resign Date is missing from the resignation file.')

def _find_resignation_reason(reason):
    """Converts the resignation reason string to a category.
    TODO: if there is another client that uses MM2000 we may need
    to refactor this"""
    reason = str(reason).lower()
    if 'moving' in reason or 'move' in reason:
        category = 'Moved'
    elif 'too far' in reason:
        category = 'Too Far'
    elif 'come' in reason or 'inactive' in reason:
        category = 'Inactive'
    elif 'deceased' in reason or 'died' in reason:
        category = 'Deceased'
    elif 'mitzvah' in reason:
        category = 'Post Bar/Bat Mitzvah'
    else:
        category = 'Other'
    return category
