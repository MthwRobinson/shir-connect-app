from trs_dashboard.database.database import Database

def test_initialize():
    database = Database()
    database.initialize()
    assert database.connection.status == 1
