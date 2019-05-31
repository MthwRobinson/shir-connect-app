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
