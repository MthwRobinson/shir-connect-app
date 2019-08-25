""" Class for managing users in the database. """
import hashlib
import logging
import random
import string

import daiquiri
import numpy as np

import shir_connect.configuration as conf
from shir_connect.database.database import Database
from shir_connect.email import Email

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
        """Checks the password of the user.
        Returns True if the user is authorized
        """
        user = self.get_user(username)
        if not user:
            return False

        pw_hash = self.hash_pw(password)
        return user['password'] == pw_hash

    def add_user(self, username, password,
                 role='standard', modules=[]):
        """Adds a new user to the database"""
        complex_enough = self.check_pw_complexity(password)
        if not complex_enough:
            return False

        # Check to see if the user already exists
        user = self.get_user(username)
        if user:
            return False
        else:
            pw_hash = self.hash_pw(password)
            item = {'id': username,
                    'password': pw_hash,
                    'role': role,
                    'modules': modules}
            self.database.load_item(item, 'users')
            return True

    def delete_user(self, username):
        """Deletes a user from the database"""
        self.database.delete_item('users', username)

    def reset_password(self, username, email, send=True):
        """Creates a new password for the user and then emails
        a temporary password to the user. Only succeeds if the user
        knows the email address associated with the account."""
        user = self.get_user(username)
        if user['email'] != email:
            return False
        else:
            new_password = self.generate_password()
            self.update_password(username, new_password)
            content = """
            <html>
                <h3>Password Reset</h3>
                <p>Hi {username}, </p>
                <p>We have a received a request to reset the password on your
                   account at <b>https://{subdomain}.shirconnect.com</b>.
                   Your temporary credentials are as follows. To ensure the
                   security of your account, please update your password
                   immediately after logging in to your account. If you
                   did not request a password update, contact your site
                   administrator immediately.
                </p>
                <p>Thanks,</p>
                <p>Shir Connect Development Team
                <hr/>
                User: <b>{username}</b><br/>
                Temporary Password: <b>{password}</b><br/>
            </html>
            """.format(username=username, subdomain=conf.SUBDOMAIN,
                       password=new_password)
            if send:
                smtp = Email()
                smtp.send_email(to_address=email,
                                subject="Shir Connect Password Reset",
                                content=content,
                                text_format='html')
            return True

    def hash_pw(self, password):
        """Hashes a password"""
        pw = password.encode('utf-8')
        pw_hash = hashlib.sha512(pw).hexdigest()
        return pw_hash

    def update_password(self, username, password):
        """Updates the password for a user."""
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
                value=pw_value)
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
                value=value)
            return True

    def update_access(self, username, modules):
        """Updates the modules thate are available for the user.
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
        """Lists all of the active users."""
        df = self.database.read_table('users', sort='id', order='asc')
        users = []
        for i in df.index:
            user = dict(df.loc[i])
            del user['password']
            del user['temporary_password']
            users.append(user)
        return users

    def check_pw_complexity(self, password):
        """Checks to ensure a password is sufficiently complex"""
        if len(password) < 10:
            return False
        elif password.isalnum():
            return False
        elif password.islower():
            return False
        elif password.isupper():
            return False
        elif contains_digit(password) == False:
            return False
        else:
            return True

    def generate_password(self, length=20):
        """Generates a complex random password that serves as a temporary
        password for new users or users who reset their pasword."""
        options = string.ascii_letters + string.digits + '!@#$%&'
        password = ''.join(random.choice(options) for i in range(length))
        complex_enough = self.check_pw_complexity(password)
        if not complex_enough:
            password = self.generate_password(length=length)
        return password

def contains_digit(pw):
    """Checks to see if a password contains number."""
    return max([x.isdigit() for x in pw])
