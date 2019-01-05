""" Utility for uploading member data into the database """
import json
import logging
import os

import daiquiri
import numpy as np
import pandas as pd 

from trs_dashboard.database.database import Database

class MemberLoader(object):
    """
    Uploads members into the member database
    Current supports the following formats:
        1. MM2000
    """
    def __init__(self):
        # Set up logging
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        # Load the column mapping configs
        self.path = os.path.dirname(os.path.realpath(__file__))
        filename = self.path + '/member_columns.json'
        with open(filename, 'r') as f:
            self.column_mapping = json.load(f)

        self.database = Database()

    def load(self, df, source='MM2000', test=False):
        """ Loads the data in to the member database """
        if source==='MM2000':
            items = self.parse_mm2000(df)

        self.database.backup_table('members')
        self.database.truncate_table('members')
        for item in items:
            self.database.load_item(item, 'members')

        good_columns = self.check_columns()
        if good_columns:
            self.database.refresh_view('members_view')
        else:
            self.logger.warning('Column mismatch in upload')
            self.database.revert_table('members')
            return False

        return True

    def parse_mm2000(self, df):
        """ Converts the MM2000 export into a list of rows """
        column_mapping = self.column_mapping['MM2000']
        items = []
        for group in column_mapping:
            column_map = column_mapping[group]['columns']
            source_cols = [x for x in column_map.keys()]
            dest_cols = [column_map[x] for x in column_map]

            if 'id_extension' in column_mapping[group]:
                id_extension = column_mapping[group]['id_extension']
            else:
                id_extension = None

            df_group = df[source_cols].copy()
            df_group = df_group.where((pd.notnull(df_group)), None)
            df_group.columns = dest_cols
            df_group = df_group.dropna(how='all').copy()
            df_group = df_group.reset_index().copy()

            for i in df_group.index:
                item = dict(df_group.loc[i])

                postal = str(item['postal_code'])
                if '-' in postal:
                    postal = postal.split('-')[0]
                if len(postal) != 5:
                    postal = None
                item['postal_code'] = postal

                if id_extension:
                    item['id'] += id_extension

                if item['birth_date']:
                    if item['birth_date'].startswith('0'):
                        item['birth_date'] = None
                if item['membership_date']:
                    if item['membership_date'].startswith('0'):
                        item['membership_date'] = None

                if 'first_name' not in item and item['full_name']:
                    item['first_name'] = item['full_name'].split()[0]
                if 'last_name' not in item  and item['full_name']:
                    item['last_name'] = item['full_name'].split()[0]
                if 'first_name' in item and 'last_name' in item:
                    items.append(item)
        return items

    def check_columns(self):
        """ Checks to make sure the columns are the same in the new table """
        new_columns = self.database.get_columns('members')
        old_columns = self.database.get_columns('members_backup')
        for column in new_columns:
            if column not in old_columns:
                return False
         return True
