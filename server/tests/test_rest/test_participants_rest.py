import pandas as pd

import shir_connect.configuration as conf
from shir_connect.database.participants import Participants
from shir_connect.services.app import app
import shir_connect.services.reports as rep
import shir_connect.services.utils as utils
from .utils import run_url_tests

CLIENT = app.test_client()

participants = Participants()
sql = """
    SELECT id
    FROM {schema}.participant_match
    WHERE member_id IS NULL
    LIMIT 1
""".format(schema=participants.database.schema)
df = pd.read_sql(sql, participants.database.connection)
PARTICIPANT_ID = dict(df.loc[0])['id']

def run_participant_tests(url):
    run_url_tests(url, client=CLIENT, access=[conf.MEMBER_GROUP])

def test_get_participant_service():
    url = '/service/participant/{}'.format(PARTICIPANT_ID)
    run_participant_tests(url)

def test_get_participants_service():
    run_participant_tests('/service/participants')
