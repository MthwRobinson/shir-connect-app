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
import logging
import random

import daiquiri
from faker import Faker

from shir_connect.database.database import Database

class FakeNews:
    """A class for generating and uploading fake Shir Connect data."""
    def __init__(self):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)
        self.database = Database()
        self.faker = Faker()

    def fake_venues(self):
        """ Generates fake venues for the venues table."""
        venues = self.database.read_table('venues')
        updated = []
        for i in venues.index:
            venue = dict(venues.loc[i])
            fake_name = self._random_name(max_size=2)
            msg = 'Changing venue name {} to {}'.format(venue['name'],
                                                        fake_name)
            self.logger.info(msg)
            subset = venues[venues['name']==venue['name']]
            for i in subset.index:
                venue_ = dict(subset.loc[i])
                self.database.update_column(table='venues',
                                            item_id=venue_['id'],
                                            column='name',
                                            value="'{}'".format(fake_name))
                updated.append(i)
        return updated

    def fake_names(self):
        """Generates fake names for the attendees, members, and orders table. """
        self._get_person_tables()
        people_tables = ['attendees', 'members', 'orders']
        updated = {k: [] for k in people_tables}
        for i in self.participants.index:
            participant = dict(self.participants.loc[i])
            first_name = participant['first_name']
            last_name = participant['last_name']
            fake_first_name = self.faker.first_name()
            fake_last_name = self.faker.last_name()
            fake_email = self.faker.email()
            msg = 'Changing name {} {} to {} {}'.format(first_name, last_name,
                                                        fake_first_name,
                                                        fake_last_name)
            self.logger.info(msg)    
            for table in people_tables:
                new_updates = self._swap_people(first_name=first_name, 
                                                last_name=last_name,
                                                fake_first_name=fake_first_name,
                                                fake_last_name=fake_last_name,
                                                fake_email=fake_email,
                                                table=table)
                for update in new_updates:
                    updated[table].append(update)
        return updated

    def _get_person_tables(self):
        """Pulls person information from the database.""" 
        self.participants = self.database.read_table('participants')
        self.attendees = self.database.read_table('attendees')
        self.members = self.database.read_table('members')
        self.orders = self.database.read_table('orders')

    def _swap_people(self, first_name, last_name, fake_first_name,
                        fake_last_name, fake_email, table):
        """Swaps out real date for fake data in the people tables."""
        # Need to clean the inputs because apostrophes trips up the
        # update statement in postgres
        first_name = first_name.replace("'",'')
        last_name = last_name.replace("'",'')
        fake_first_name = fake_first_name.replace("'",'')
        fake_last_name = fake_last_name.replace("'",'')
        fake_email = fake_email.replace("'",'')

        df = getattr(self, table)
        subset = self._find_name(first_name, last_name, df)
        for i in subset.index:
            person = dict(subset.loc[i])
            full_name = ' '.join([first_name, last_name])
            self.database.update_column(table=table,
                                        item_id=person['id'],
                                        column='first_name',
                                        value="'{}'".format(fake_first_name))
            self.database.update_column(table=table,
                                        item_id=person['id'],
                                        column='last_name',
                                        value="'{}'".format(fake_last_name))
            self.database.update_column(table=table,
                                        item_id=person['id'],
                                        column='email',
                                        value="'{}'".format(fake_email))
            if table in ['attendees', 'orders']:
                self.database.update_column(table=table,
                                            item_id=person['id'],
                                            column='name',
                                            value="'{}'".format(full_name))
            elif table == 'members':
                self.database.update_column(table='members',
                                            item_id=person['id'],
                                            column='nickname',
                                            value="'{}'".format(first_name))
        
        return list(subset.index)
    
    def _find_name(self, first_name, last_name, table):
        """Finds the rows in the table that match the name."""
        return table[(table['first_name']==first_name)&
                     (table['last_name']==last_name)]

    def _random_name(self, max_size):
        """Generates a random name for events and venues. """
        phrase = self.faker.catch_phrase().split()
        short_phrase = ' '.join(phrase[:max_size])
        letters = list(short_phrase)
        random.shuffle(letters)
        name = ''.join(letters)
        return name.title()
