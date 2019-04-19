""" Class for managing users in the database. """
import hashlib
import logging
import random

import daiquiri
import numpy as np
import xkcdpass.xkcd_password as xkcd

import shir_connect.configuration as conf
from shir_connect.database.database import Database

class UserManagement:
    """ Class that handles user centric REST operations """
    def __init__(self, database=None):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.database = database if database else Database()

        self.access_groups = conf.ACCESS_GROUPS
        self.user_roles = conf.USER_ROLES

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

        pw_hash = self.hash_pw(password)
        return user['password'] == pw_hash

    def add_user(self, username, password,
                 role='standard', modules=[]):
        """ Adds a new user to the database """
        complex_enough = self.check_pw_complexity(password)
        if not complex_enough:
            return False

        # Check to see if the user already exists
        user = self.get_user(username)
        if user:
            return False
        else:
            pw_hash = self.hash_pw(password)
            item = {
                'id': username,
                'password': pw_hash,
                'role': role,
                'modules': modules
            }
            self.database.load_item(item, 'users')
            return True

    def delete_user(self, username):
        """ Deletes a user from the database """
        self.database.delete_item('users', username)

    def hash_pw(self, password):
        """ Hashes a password """
        pw = password.encode('utf-8')
        pw_hash = hashlib.sha512(pw).hexdigest()
        return pw_hash

    def update_password(self, username, password):
        """ Updates the password for a user. """
        complex_enough = self.check_pw_complexity(password)
        if not complex_enough:
            return False

        # Check to see if the user exists
        user = self.get_user(username)
        if user:
            pw_hash = self.hash_pw(password)
            pw_value = "'%s'"%(pw_hash)
            self.database.update_column(
                table='users',
                item_id=username,
                column='password',
                value=pw_value
            )
            return True
        else:
            return False

    def update_role(self, username, role):
        """
        Updates the role for the user.
        The two types of users are admin and standard
        """
        if role not in self.user_roles:
            return False
        else:
            value = "'%s'"%(role)
            self.database.update_column(
                table='users',
                item_id=username,
                column='role',
                value=value
            )
            return True

    def update_access(self, username, modules):
        """
        Updates the modules thate are available for the user.
        The available types are events, members, trends and map
        """
        mods = [x for x in modules if x in self.access_groups]
        value = "'{" + ','.join(['"%s"'%(x) for x in mods]) + "}'"
        self.database.update_column(
            table='users',
            item_id=username,
            column='modules',
            value=value
        )

    def list_users(self):
        """ Lists all of the active users """
        df = self.database.read_table('users', sort='id', order='asc')
        users = []
        for i in df.index:
            user = dict(df.loc[i])
            del user['password']
            users.append(user)
        return users

    def check_pw_complexity(self, password):
        """ Checks to ensure a password is sufficiently complex """
        if len(password) < 10:
            return False
        elif password.isalnum():
            return False
        elif password.islower():
            return False
        elif password.isupper():
            return False
        else:
            return True

    def generate_password(self):
        """ Creates an XKCD style password """
        # Choose four random english words and three random integers
        wordfile = xkcd.locate_wordfile()
        wordlist = xkcd.generate_wordlist(
            wordfile=wordfile,
            min_length=4,
            max_length=8
        )
        words = xkcd.generate_xkcdpassword(wordlist, numwords=4).split()
        numbers = np.random.randint(low=0, high=9, size=3)

        # Generate the password
        password = ''
        for i, word in enumerate(words):
            password += word.title()
            if i < 3:
                password += str(numbers[i])
        password += random.choice('!@#$%&')
        return password
