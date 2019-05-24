import pandas as pd

from shir_connect.database.participants import Participants

participants = Participants()
sql = """
    SELECT a.id
    FROM {schema}.participant_match a
    INNER JOIN {schema}.attendee_to_participant b
    ON a.id = b.participant_id
    WHERE member_id IS NOT NULL
    LIMIT 1
""".format(schema=participants.database.schema)
df = pd.read_sql(sql, participants.database.connection)
PARTICIPANT_ID = dict(df.loc[0])['id']

def test_get_participant():
    participants = Participants()
    participant = participants.get_participant(PARTICIPANT_ID)
    assert isinstance(participant, dict)
    assert participant['participant_id'] == PARTICIPANT_ID

    participant = participants.get_participant('not-a-real-id')
    assert participant is None

def test_get_participant_events():
    participants = Participants()
    events = participants.get_participant_events(PARTICIPANT_ID)
    assert isinstance(events, list)
    assert len(events) > 0

def test_get_participants():
    participant_db = Participants()
    participants = participant_db.get_participants(limit=25)
    assert isinstance(participants, dict)
    assert len(participants['results']) == 25
