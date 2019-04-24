from shir_connect.analytics.entity_resolution import NameResolver

class FakeDatabase():
    def __init__(self):
        self.schema = 'fake_schema'

    def run_query(self, query):
        pass

def test_load_members_id():
    name_resolver = NameResolver()
    name_resolver.database = FakeDatabase()
    name_resolver.load_member_ids()

def test_get_fuzzy_matches():
    name_resolver = NameResolver()
    results = name_resolver.get_fuzzy_matches('fake', 'name', 'fake@email.com')
    assert isinstance(results, list)

def test_lookup_name():
    name_resolver = NameResolver()
    nicknames = name_resolver._lookup_name('matt')
    assert 'matthew' in nicknames
    nicknames = name_resolver._lookup_name('matthew')
    assert 'matt' in nicknames
