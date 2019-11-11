""" Generates fake data to support testing and demos to new clients.

Fake data is generated for the following tables and columns:
    - Table: participant_match
        Columns:
            - fake_first_name
            - fake_last_name
            - fake_nickname
    - Table: events
        Columns:
            - name
            - description
    - Table: venues
        Columns:
            - name
"""
import datetime
import logging
import random

import daiquiri
from faker import Faker
import pandas as pd
import numpy as np

import shir_connect.configuration as conf
from shir_connect.database.database import Database

class FakeNews:
    """A class for generating and uploading fake Shir Connect data."""
    def __init__(self, database=None):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)
        self.database = Database() if not database else database
        self.faker = Faker()
        self.postal_codes = None

    def build_fake_data(self):
        """ Generates fake data for the database. """
        self.fake_names()
        self.fake_events()
        self.fake_venues()
        self.database.refresh_views()

    def fake_events(self):
        """Generates fake events for the events table."""
        event_ids = self._get_events()
        prefixes = [x for x in conf.EVENT_GROUPS]
        prefixes.append(None)

        for i, event_id in enumerate(event_ids):
            if i%1000 == 0:
                msg = 'Generated fake names for {} events.'.format(i)
                self.logger.info(msg)

            fake_name = self._random_name(max_size=5)
            fake_name = fake_name.replace("'",'')
            np.random.shuffle(prefixes)
            prefix = prefixes[0]
            if prefix:
                fake_name = prefix + ': ' + fake_name
            fake_descr = self._random_paragraph(max_size=15)

            self.database.update_column(table='events',
                                        item_id=event_id,
                                        column='fake_name',
                                        value="'{}'".format(fake_name))
            self.database.update_column(table='events',
                                        item_id=event_id,
                                        column='fake_description',
                                        value="'{}'".format(fake_descr))

    def fake_venues(self):
        """Generates fake venues for the venues table."""
        venue_ids = self._get_venues()
        for i, venue_id in enumerate(venue_ids):
            if i%1000 == 0:
                msg = 'Generated fake names for {} venues.'.format(i)
                self.logger.info(msg)

            fake_name = self._random_name(max_size=2)
            self.database.update_column(table='venues',
                                        item_id=venue_id,
                                        column='fake_name',
                                        value="'{}'".format(fake_name))

    def fake_names(self):
        """Generates fake names for the attendees, members, and orders table. """
        participant_ids = self._get_participants()
        for i, participant_id in enumerate(participant_ids):
            if i%1000 == 0:
                msg = 'Generated fake names for {} participants.'.format(i)
                self.logger.info(msg)

            fake_first_name = "'{}'".format(self.faker.first_name())
            fake_last_name = "'{}'".format(self.faker.last_name())
            fake_email = "'{}'".format(self.faker.email())

            self.database.update_column(table='participant_match',
                                        item_id=participant_id,
                                        column='fake_first_name',
                                        value=fake_first_name)
            self.database.update_column(table='participant_match',
                                        item_id=participant_id,
                                        column='fake_nickname',
                                        value=fake_first_name)
            self.database.update_column(table='participant_match',
                                        item_id=participant_id,
                                        column='fake_last_name',
                                        value=fake_last_name)
            self.database.update_column(table='participant_match',
                                        item_id=participant_id,
                                        column='fake_email',
                                        value=fake_email)

    def fake_birthday(self, min_age=18, max_age=85):
        """Generates a fake birthday that can be used in the demo version.

        Parameters
        ----------
        min_age : int
            the minimum age of the random birthday
        max_age : int
            the maximum age of the random birthday

        Returns
        -------
        birthday : datetime.datetime
        """
        start_date = "-{}y".format(max_age)
        end_date = "-{}y".format(min_age)
        birthday = self.faker.date_between(start_date=start_date, end_date=end_date)
        return birthday

    def fake_membership_date(self, max_age=30):
        """Generates a fake membership date for the database

        Parameters
        ----------
        max_age : int
            the maximum age of the random birthday

        Returns
        -------
        birthday : datetime.datetime
        """
        start_date = "-{}y".format(max_age)
        membership_date = self.faker.date_between(start_date=start_date, end_date="today")
        return membership_date#

    def fake_members(self, num_members):
        """Generates fake members and loads them into the databse

        Parameters
        ----------
        num_members : int
            the number of fake members to create

        Returns
        -------
        Loads the fake members into the demo database
        """
        for i in range(num_members):
            member = self._fake_member(i)
            self.database.load_item(member, 'members')

    def _fake_member(self, identifier):
        """Generates a fake member with all of the attributes required in the
        member table"""
        member = {}
        member['id'] = identifier
        member['household_id'] = identifier
        member['member_family'] = 'Y'

        # Generate a male or female name with 50% probability
        female = np.random.random() < .5
        if female:
            first_name = self.faker.first_name_female()
            gender = 'F'
        else:
            first_name = self.faker.first_name_male()
            gender = 'M'
        member['first_name'] = first_name
        member['nickname'] = first_name
        member['last_name'] = self.faker.last_name()
        member['gender'] = gender
        member['email'] = self.faker.email()
        member['postal_code'] = self._postal_code()

        member['birth_date'] = self.fake_birthday()
        membership_date = self.fake_membership_date()
        member['membership_date'] = membership_date

        # Make the member Jewish with 90% probability
        jewish = np.random.random() < .9
        religion = 'Jewish' if jewish else 'Not Jewish'
        member['member_religion'] = religion

        member['resignation_date'] = self._resignation_date(membership_date)
        reasons = ['Too far', 'Finished bar mitzvah', 'Moved', 'Lost interest']
        if member['resignation_date']:
            resignation_reason = np.random.choice(reasons)
        else:
            resignation_reason = None
        member['resignation_reason'] = resignation_reason
        active = np.random.random() < .9
        member['active_member'] = active and not member['resignation_date']

        membership_types = ['MEMFAM', 'MEMIND', 'STAFF']
        member['member_type'] = np.random.choice(membership_types, p=[.75, .2, .05])

        return member

    def _resignation_date(self, membership_date, prob=.1):
        """Generates a fake resignation date with probability prob."""
        # Make the member resign with 10% probability
        resigned = np.random.random() < .1
        resignation_date = None
        if resigned:
            today = datetime.datetime.now()
            mem_dt = datetime.datetime.combine(membership_date,
                                               datetime.datetime.min.time())
            max_age = int(np.floor((today - mem_dt).days / 365))
            if max_age > 0:
                resignation_date = self.fake_membership_date(max_age)
        return resignation_date

    def _get_participants(self):
        """Pulls a list of participants who need fake names."""
        sql = """
            SELECT id
            FROM {schema}.participant_match
            WHERE fake_first_name IS NULL
            OR fake_last_name IS NULL
            OR fake_nickname IS NULL
        """.format(schema=self.database.schema)
        df = pd.read_sql(sql, self.database.connection)
        participant_ids = list(df['id'].unique())
        return participant_ids

    def _postal_code(self):
        """Generates a fake postal code, weighted by numerical.
        distance from the default postal_code."""
        if not isinstance(self.postal_codes, pd.DataFrame):
            default = conf.DEFAULT_LOCATION['postal_code']
            postal_codes = self.database.read_table('geometries', ['id'])
            postal_codes['weights'] = (postal_codes['id'].astype(int) - default)**2
            postal_codes.sort_values('weights', ascending=True, inplace=True)
            postal_codes.reset_index(drop=True, inplace=True)
            postal_codes = postal_codes[:100]
            postal_codes['weights'] = (postal_codes['weights'].max() -
                                       postal_codes['weights'])
            postal_codes['weights'] = (postal_codes['weights'] /
                                       postal_codes['weights'].sum())
            self.postal_codes = postal_codes
        return np.random.choice(self.postal_codes['id'],
                                p=self.postal_codes['weights'])

    def _get_events(self):
        """Pulls a list of events that need fake names."""
        sql = """
            SELECT id
            FROM {schema}.events
            WHERE fake_name IS NULL
        """.format(schema=self.database.schema)
        df = pd.read_sql(sql, self.database.connection)
        event_ids = list(df['id'].unique())
        return event_ids

    def _get_venues(self):
        """Pulls a list of events that need fake names."""
        sql = """
            SELECT id
            FROM {schema}.venues
            WHERE fake_name IS NULL
        """.format(schema=self.database.schema)
        df = pd.read_sql(sql, self.database.connection)
        venue_ids = list(df['id'].unique())
        return venue_ids

    def _random_name(self, max_size=2):
        """Generates a random name for events and venues."""
        phrase = self.faker.catch_phrase().split()
        short_phrase = ' '.join(phrase[:max_size])
        letters = list(short_phrase)
        random.shuffle(letters)
        name = ''.join(letters)
        return name.title()

    def _random_paragraph(self, max_size=15):
        """Generates a random sentence for event descriptions."""
        sentences = self.faker.sentences(max_size)
        scrambled_sentences = []
        for sentence in sentences:
            sentence_list = list(sentence)
            random.shuffle(sentence_list)
            scrambled_sentence = ''.join(sentence_list).replace('.','')
            scrambled_sentences.append(scrambled_sentence.capitalize())
        paragraph = '. '.join(scrambled_sentences)
        return paragraph
