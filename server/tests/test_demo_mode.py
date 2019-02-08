from trs_dashboard.services.demo_mode import demo_mode

@demo_mode(['first_name','last_name',{'friends': ['name']}], demo_mode=True)
def kangaroo():
    response = {
        'first_name': 'Matt',
        'last_name': 'Robinson',
        'occupation':'Penguin',
        'friends': [
            {'name': 'Nathan', 'occupation': 'Dinosaur'},
            {'name': 'Eric', 'occupation': 'Guy on a buffalo'}
        ]
    }
    return response

def test_demo_mode():
    response = kangaroo()
    assert response['first_name'] != 'Matt'
    assert response['last_name'] != 'Robinson'
    assert response['occupation'] == 'Penguin'
    assert response['friends'][0]['name'] != 'Nathan'
    assert response['friends'][0]['occupation'] == 'Dinosaur'
    assert response['friends'][1]['name'] != 'Eric'
    assert response['friends'][1]['occupation'] == 'Guy on a buffalo'
