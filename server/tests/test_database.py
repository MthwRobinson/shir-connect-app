from trs_dashboard.database.database import Database

def test_initialize():
    database = Database()
    database.initialize()
    assert database.connection.status == 1

def test_get_columns():
    database = Database()
    columns = database.get_columns('events')
    assert len(columns) > 0

def test_refresh_views():
    database = Database()
    database.refresh_views(test=True)

def test_read_table():
    database = Database()
    df = database.read_table('event_aggregates', limit=10)
    assert len(df) == 10

def test_load_items():
    database = Database()
    database.delete_item('members', 'testid1')
    database.delete_item('members', 'testid2')

    columns = database.get_columns('members')
    item1 = {x: None for x in columns}
    item1['id'] = 'testid1'
    item2 = {x: None for x in columns}
    item2['id'] = 'testid2'
    items = [item1, item2]

    database.load_items(items, 'members')
    item1_ = database.get_item('members', 'testid1')
    assert item1_['id'] == 'testid1'
    item2_ = database.get_item('members', 'testid2')
    assert item2_['id'] == 'testid2'

    database.delete_item('members', 'testid1')
    item1_ = database.get_item('members', 'testid1')
    assert item1_ == None
    database.delete_item('members', 'testid2')
    item2_ = database.get_item('members', 'testid2')
    assert item2_ == None
