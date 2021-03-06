import pytest

import pandas as pd

from shir_connect.etl.participant_matcher import ParticipantMatcher

class FakeDatabase():
    def __init__(self):
        self.schema = 'fake_schema'
        self.connection = 'fake_connection'

    def load_item(self, *args, **kwargs):
        pass

    def fetch_df(self, *args, **kwargs):
        df = pd.read_sql(*args, **kwargs)
        return df

    def update_column(self, *args, **kwargs):
        pass

    def to_json(self, df):
        return [{'id': 867}, {'id': 5309}]


class FakeNameResolver():
    def __init__(self):
        pass

    def find_best_match(self, first_name, last_name, email, age):
        if first_name == 'Carl':
            return {'first_name': 'Carl', 'last_name': 'Camel',
                    'email': 'two_humps@aol.com', 'id': 1134}
        else:
            return None


class FakeParticipants():
    def __init__(self, *args, **kwargs):
        pass

    def get_participant_events(self, participant_id):
        return [{'event_id': 867}, {'event_id': 5309}]

def test_get_missing_attendees(monkeypatch):
    fake_response = pd.DataFrame({'id': [1, 2, 3], 'event_id': [4, 5, 6]})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)
    participant_matcher = ParticipantMatcher()
    missing_attendees = participant_matcher._get_missing_attendees()
    assert list(missing_attendees['id']) == [1, 2, 3]
    assert list(missing_attendees['event_id']) == [4, 5, 6]

def test_get_avg_event_age(monkeypatch):
    fake_response = pd.DataFrame({'avg_age': [53]})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)
    participant_matcher = ParticipantMatcher()
    avg_age = participant_matcher._get_avg_event_age(123)
    assert avg_age == 53
    avg_age = participant_matcher._get_avg_event_age([123, 456])
    assert avg_age == 53

def test_estimate_participant_age(monkeypatch):
    fake_response = pd.DataFrame({'avg_age': [53]})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)
    participant_matcher = ParticipantMatcher()
    participant_matcher.participants = FakeParticipants()
    est_age = participant_matcher._estimate_participant_age('fake_participant')
    assert est_age == 53

def test_process_attendee(monkeypatch):
    # Mainly testing to make sure this code runs without error
    fake_response = pd.DataFrame({'avg_age': [53]})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)

    participant_matcher = ParticipantMatcher()
    participant_matcher.database = FakeDatabase()
    participant_matcher.name_resolver = FakeNameResolver()

    attendee = {'first_name': 'Carl', 'last_name': 'Camel',
                'email': 'two_humps@aol.com', 'id': 123, 'event_id': 456}
    participant_matcher._process_attendee(attendee)

    attendee = {'first_name': 'Carla', 'last_name': 'Camel',
                'email': 'two_humps@aol.com', 'id': 789, 'event_id': 456}
    participant_matcher._process_attendee(attendee)

def test_participant_match_run():
    # Mainly testing to make sure this code runs without error
    fake_response = pd.DataFrame({'first_name': ['Carl', 'Claramel'],
                                  'last_name': ['Camel', 'Cow'],
                                  'email': ['potatoes@food.net', 'ice_cream@food.net'],
                                  'id': [1, 2],
                                  'event_id': [72, 72]})

    participant_matcher = ParticipantMatcher()
    participant_matcher.database = FakeDatabase()
    participant_matcher.name_resolver = FakeNameResolver()
    participant_matcher._get_missing_attendees = lambda *args, **kwargs: fake_response
    participant_matcher._process_attendee = lambda attendee: attendee
    participant_matcher._estimate_unknown_ages = lambda *args, **kwargs: 'Squawk!!'

    participant_matcher.run(iters=1)

def test_estimate_unknown_ages(monkeypatch):
    fake_response = pd.DataFrame({'id': [867, 5309]})
    monkeypatch.setattr('pandas.read_sql', lambda *args, **kwargs: fake_response)

    participant_matcher = ParticipantMatcher()
    participant_matcher.database = FakeDatabase()
    participant_matcher.name_resolver = FakeNameResolver()
    participant_matcher._estimate_participant_age = lambda *args, **kwargs: 34

    participant_matcher.estimate_unknown_ages()
