""" Utility for uploading member data into the database """
import logging
import os

import daiquiri

from shir_connect.etl.sources.mm2000 import MM2000
from shir_connect.database.database import Database

class MemberLoader:
    """
    Uploads members into the member database
    Current supports the following formats:
        1. MM2000
    """
    def __init__(self, database=None):
        # Set up logging
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.mm2000 = MM2000()

    def load(self, df, source='MM2000'):
        """ Loads the data in to the member database """
        if source=='MM2000':
            try:
                load_status = self.mm2000.load(df)
            except ValueError:
                load_status = False

        return load_status

    def load_resignations(self, df, source='MM2000'):
        """Loads resignation data into the database."""
        if source=='MM2000':
            try:
                self.mm2000.load_resignations(df)
                return True
            except ValueError:
                return False
