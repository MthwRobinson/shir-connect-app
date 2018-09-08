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

    def authenticate_user(self, username, password):
        """
        Checks the password of the user
        Returns True if the user is authorized
        """
        user = self.get_user(username)
        if not user:
            return False

        pw = password.encode('utf-8')
        pw_hash = hashlib.sha512(pw).hexdigest()
        if user['password'] == pw_hash:
            return True
        else:
            return False

    def add_user(self, username, password):
        """ Adds a new user to the database """
        # Check to see if the user already exists
        user = self.get_user(username)
        if user:
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

    def delete_user(self, username):
        """ Deletes a user from the database """
        self.database.delete_item('users', username)

