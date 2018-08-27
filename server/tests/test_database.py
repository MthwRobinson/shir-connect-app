from trs_dashboard.etl.database import Database

def test_initialize():
    database = Database()
    database.initialize()
    assert database.connection.status == 1

def test_get_columns():
    database = Database()
    columns = database.get_columns('events')
    assert len(columns) > 0
