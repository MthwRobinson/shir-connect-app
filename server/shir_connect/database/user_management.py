""" Class for managing users in the database. """
import datetime
import hashlib
import logging
import random
import string

import daiquiri
import numpy as np

import shir_connect.configuration as conf
from shir_connect.database.database import Database
from shir_connect.email import Email

SPECIAL_CHARACTERS = '!@#$%&'
PW_CHARACTERS = string.ascii_letters + string.digits + SPECIAL_CHARACTERS

class UserManagement:
    """Class that handles user centric REST operations """
    def __init__(self, database=None):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.database = database if database else Database()

        self.access_groups = conf.ACCESS_GROUPS
        self.user_roles = conf.USER_ROLES

    def get_user(self, username):
        """Fetches a user from the database """
        return self.database.get_item('users', username)

    def authenticate_user(self, username, password):
        """Checks the password of the user
        Returns True if the user is authorized."""
        user = self.get_user(username)
        if not user:
            return False

        pw_hash = self.hash_pw(password)
        return user['password'] == pw_hash

    def add_user(self, username, password, email=None, role='standard',
                 modules=[], send=False):
        """Adds a new user to the system. The pw_update_ts for the account
        is set to the time that the password was updated with this function.

        Parameters
        ----------
        username: str, the username for the new user
        password: str, the password to the new user. must meet password
            complexity requirements
        email: str, the email for the user. primarily used for password resets
        role: str, the role of the new user. 'standard' or 'admin'
        modules: list, the list of modules the uer should have access to
        temporary_password: boolean, True if the password is temporary. users
            who log in with a temporary password should be redirected to
            the change password screen

        Returns
        -------
        True if the password update was successful, False otherwise
        """
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
                    'email': email,
                    'role': role,
                    'modules': modules,
                    'temporary_password': True,
                    'pw_update_ts': datetime.datetime.utcnow()}
            self.database.load_item(item, 'users')

            # Send an email with temporary credentials to the user
            # The homepage will redirect the user to the change password
            # screen until they have changed their temporary credentials
            content = """
            <html>
                <h3>New User Account</h3>
                <p>Hi {username}, </p>
                <p>Your user account at
                <b>https://{subdomain}.shirconnect.com</b> is now active.
                Your temporary credentials are as follows. To ensure the
                security of your account, please update your password
                immediately after logging in to your account.
                </p>
                <p>Thanks,</p>
                <p>Shir Connect Development Team
                <hr/>
                User: <b>{username}</b><br/>
                Temporary Password: <b>{password}</b><br/>
            </html>
            """.format(username=username, subdomain=conf.SUBDOMAIN,
                    password=password)
            if send:
                smtp = Email()
                smtp.send_email(to_address=email,
                                subject="Shir Connect User Account",
                                content=content,
                                text_format='html')
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
            self.update_password(username, new_password, temporary=True)
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

    def update_password(self, username, password, temporary=False):
        """Updates the password for a user.

        Parameters
        ----------
        username: string, the name of the user
        password: string, the updated password for the user. The password
            is hashed before being started in the database
        temporary: boolean, if True, the password is stored as a temporary
            password. The user will be redirected to the change password
            screen if their password is listed as temporary in the database
        """
        complex_enough = self.check_pw_complexity(password)
        if not complex_enough:
            return False

        # Check to see if the user exists
        user = self.get_user(username)
        if user:
            pw_hash = self.hash_pw(password)
            pw_value = "'%s'"%(pw_hash)
            # Change the password for the user in the database
            self.database.update_column(
                table='users',
                item_id=username,
                column='password',
                value=pw_value)
            # Change the update time for the password in the database
            self.database.update_column(
                table='users',
                item_id=username,
                column='pw_update_ts',
                value="'{}'".format(datetime.datetime.utcnow()))
            # Update the temporary_password column to indicate whether
            # the password is a temporary or permanent password
            self.database.update_column(
                table='users',
                item_id=username,
                column='temporary_password',
                value=temporary)
            return True
        else:
            return False

    def update_role(self, username, role):
        """ Updates the role for the user.
        The two types of users are admin and standard."""
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

    def update_email(self, username, email):
        """Updates the users email in the database."""
        self.database.update_column(table='users',
                                    item_id=username,
                                    column='email',
                                    value="'{}'".format(email))

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

    def check_pw_complexity(self, password, display_error=False):
        """Checks to ensure a password is sufficiently complex.

        Parameters
        ----------
        password: str
            the password whose complexity needs to be checked
        display_error: bool
            if true, displays a message indicating why the password is not
            complex enough

        Returns
        -------
        complex_enough, errors: (bool, list)
        """
        complex_enough = True
        errors = []
        if len(password) < 10:
            complex_enough = False
            errors.append("Password needs to have more than 10 characters.")
        if password.isalnum():
            complex_enough = False
            errors.append("Password must include numbers and special characters.")
        if password.islower():
            complex_enough = False
            errors.append("Password cannot be all lower case.")
        if password.isupper():
            complex_enough = False
            errors.append("Password cannot be all upper case.")
        if contains_digit(password) == False:
            complex_enough = False
            errors.append("Password must include at least one number.")
        if valid_characters(password) == False:
            complex_enough = False
            error = "Password may only contain numbers, letters "
            error += "and the following special characters: {}."
            errors.append(error.format(SPECIAL_CHARACTERS))
        if password != password.strip():
            complex_enough = False
            errors.append("Password cannot contain white space.")
        if display_error:
            return complex_enough, errors
        else:
            return complex_enough

    def generate_password(self, length=20):
        """Generates a complex random password that serves as a temporary
        password for new users or users who reset their pasword."""
        password = ''.join(random.choice(PW_CHARACTERS) for i in range(length))
        complex_enough = self.check_pw_complexity(password)
        if not complex_enough:
            password = self.generate_password(length=length)
        return password

def contains_digit(pw):
    """Checks to see if a password contains number."""
    return max([x.isdigit() for x in pw])

def valid_characters(pw):
    """Checkes to ensure the password only contains valid characters."""
    return max([x in PW_CHARACTERS for x in pw])
