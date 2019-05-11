import pandas as pd

from shir_connect.database.participants import Participants


participants = Participants()
sql = """
    SELECT id
    FROM {schema}.participant_match
    WHERE member_id IS NULL
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
