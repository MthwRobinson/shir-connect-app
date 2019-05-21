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

from shir_connect.database.database import Database

class FakeNews:
    """A class for generating and uploading fake Shir Connect data."""
    def __init__(self):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)
        self.database = Database()
        self.faker = Faker()

    def build_fake_data(self):
        """ Generates fake data for the database. """
        self.fake_names()
        self.fake_events()
        self.fake_venues()
        self.database.refresh_views()

    def fake_events(self):
        """Generates fake events for the events table."""
        events = self.database.read_table('events')
        updated = []
        for i in events.index:
            event = dict(events.loc[i])
            if not event['name']:
                continue
            if ':' in event['name']:
                prefix = event['name'].split(':')[0] + ':'
                fake_name = ' '.join([prefix, self._random_name(max_size=5)])
            else:
                fake_name = self._random_name(max_size=5)
            fake_name = fake_name.replace("'",'')
            fake_descr = self._random_paragraph(max_size=15)
            msg = 'Changing event name {} to {}'.format(event['name'],
                                                        fake_name)
            self.logger.info(msg)
            subset = events[events['name']==event['name']]
            for j in subset.index:
                event_ = dict(subset.loc[j])
                self.database.update_column(table='events',
                                            item_id=event_['id'],
                                            column='name',
                                            value="'{}'".format(fake_name))
                self.database.update_column(table='events',
                                            item_id=event_['id'],
                                            column='description',
                                            value="'{}'".format(fake_descr))
                updated.append(j)
        return updated

    def fake_venues(self):
        """Generates fake venues for the venues table."""
        venues = self.database.read_table('venues')
        updated = []
        for i in venues.index:
            venue = dict(venues.loc[i])
            if not venue['name']:
                continue
            fake_name = self._random_name(max_size=2)
            msg = 'Changing venue name {} to {}'.format(venue['name'],
                                                        fake_name)
            self.logger.info(msg)
            subset = venues[venues['name']==venue['name']]
            for j in subset.index:
                venue_ = dict(subset.loc[j])
                self.database.update_column(table='venues',
                                            item_id=venue_['id'],
                                            column='name',
                                            value="'{}'".format(fake_name))
                updated.append(j)
        return updated

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
        """Pulls person information from the database."""
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
