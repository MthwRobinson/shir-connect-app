import shir_connect.analytics.entity_resolution as er

class FakeDatabase():
    def __init__(self):
        self.schema = 'fake_schema'

    def run_query(self, query):
        pass

def test_load_members_id():
    name_resolver = er.NameResolver()
    name_resolver.database = FakeDatabase()
    name_resolver.load_member_ids()

def test_get_fuzzy_matches():
    name_resolver = er.NameResolver()
    results = name_resolver.get_fuzzy_matches('fake', 'name', 'fake@email.com')
    assert isinstance(results, list)

def test_lookup_name():
    name_resolver = er.NameResolver()
    nicknames = name_resolver._lookup_name('matt')
    assert 'matthew' in nicknames
    nicknames = name_resolver._lookup_name('matthew')
    assert 'matt' in nicknames

def test_string_similarity():
    similarity_1 = er.string_similarity('matt', 'matt')
    similarity_2 = er.string_similarity('matthew', 'matt')
    similarity_3 = er.string_similarity('matt', 'ryan')
    assert similarity_1 > similarity_2
    assert similarity_2 > similarity_3

def test_age_similarity():
    similarity_1 = er.age_similarity(50, 50)
    assert similarity_1 == 1
    similarity_2 = er.age_similarity(50, 35)
    similarity_3 = er.age_similarity(40, 50)
    assert similarity_3 > similarity_2
    similarity_4 = er.age_similarity(100, 20)
    assert similarity_4 == 0

def test_name_similarity():
    similarity_1 = er.name_similarity('Matt', 'Matthew', 'Matt')
    assert similarity_1 == 1
    similarity_2 = er.name_similarity('Matt', 'Matthew')
    assert similarity_1 > similarity_2
