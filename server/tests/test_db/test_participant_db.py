import pandas as pd

from shir_connect.database.participants import Participants

def test_get_participant():
    participants = Participants()
    sql = """
        SELECT id
        FROM {schema}.participant_match
        LIMIT 1
    """.format(schema=participants.database.schema)
    df = pd.read_sql(sql, participants.database.connection)
    participant_id = dict(df.loc[0])['id']

    participant = participants.get_participant(participant_id)
    assert isinstance(participant, dict)
