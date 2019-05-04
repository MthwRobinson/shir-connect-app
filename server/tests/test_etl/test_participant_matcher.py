import pytest

import pandas as pd

from shir_connect.etl.participant_matcher import ParticipantMatcher

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
