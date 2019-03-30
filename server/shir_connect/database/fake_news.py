""" Generates fake data to support testing and demos to new clients. 

Fake data is generated for the following tables and columns:
    - Table: attendees
        Columns:
            - email
            - first_name
            - last_name
            - name
    - Table: events
        Columns:
            - name
            - description
    - Table: members
        Columns:
            - first_name
            - last_name
            - nickname
            - email
    - Table: orders
        Columns:
            - email
            - first_name
            - last_name
            - name
    - Table: venues
        Columns:
            - name
"""
from faker import Faker

from shir_connect.database.database import Database

class FakeNews:
    """A class for generating and uploading fake Shir Connect data."""
    def __init__(self):
        self.database = Database()
        self.faker = Faker()

    def fake_names(self):
        """Generates fake names for the attendees, members, and orders table. """

        for i in participants.index:
            participant = dict(participants.loc[i])
            first_name = participant['first_name']
            last_name = participant['last_name']
            fake_first_name = self.faker.first_name()
            fake_last_name = self.faker.last_name()
            fake_email = self.faker.email()

    def _get_person_tables(self):
        """Pulls person information from the database.""" 
        self.participants = self.database.read_table('participants')
        self.attendees = self.database.read_table('attendees')
        self.members = self.database.read_table('members')
        self.order = self.database.read_table('orders')

    def _swap_attendees(self, first_name, last_name, fake_first_name,
                        fake_last_name, fake_email):
        """Swaps out real date for fake data in the attendees table."""
        pass

    def _find_name(self, first_name, last_name, table):
        """Finds the rows in the table that match the name."""
        return table[(table['first_name']==first_name)&
                     (table['last_name']==last_name)]
