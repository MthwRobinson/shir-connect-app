""" Operations for user authentication endpoints """
import hashlib
import logging

import daiquiri
import pandas as pd

from trs_dashboard.database.database import Database

class UserManagement(object):
    """ Class that handles user centric REST operations """
    def __init__(self):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.database = Database()

    def get_user(self, username):
        """ Fetches a user from the database """
        return self.database.get_item('users', username)

    def add_user(self, username, password):
        """ Adds a new user to the database """
        # Check to see if the user already exists
        user = self.get_user(username)
        if not user:
            return False
        else:
            pw = password.encode('utf-8')
            pw_hash = hashlib.sha512(pw).hexdigest()
            item = {
                'id': username,
                'password': pw_hash
            }
            self.database.load_item(item, 'users')
            return True

