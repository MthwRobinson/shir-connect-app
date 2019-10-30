import json
import pytest

from .utils import fake_request, FakeResponse
from shir_connect.etl.sources.lgl import LittleGreenLight

def test_lgl_get(monkeypatch):
    monkeypatch.setattr('requests.get',
                        lambda *args, **kwargs: lgl_request(*args, **kwargs))

    lgl = LittleGreenLight()
    response = lgl.get('/test')
    body = json.loads(response.text)
    assert body['test'] == 'success'
    assert response.status_code == 200

def test_lgl_traverse_results(monkeypatch):
    monkeypatch.setattr('requests.get',
                        lambda *args, **kwargs: lgl_request(*args, **kwargs))

    lgl = LittleGreenLight()
    items = lgl._traverse_results('/traverse?offset=0')
    assert items == ['carl', 'carla', 'sheep', 'sleepy_sheep']

def test_get_lgl_constituents(monkeypatch):
    monkeypatch.setattr('requests.get',
                        lambda *args, **kwargs: lgl_request(*args, **kwargs))

    lgl = LittleGreenLight()

    constituents = lgl.get_constituents(traverse=True)
    assert [x['id'] for x in constituents] == [100, 101]

    constituents = lgl.get_constituents(traverse=False)
    assert [x['id'] for x in constituents] == [100, 101]

def test_get_lgl_addresses(monkeypatch):
    monkeypatch.setattr('requests.get',
                        lambda *args, **kwargs: lgl_request(*args, **kwargs))

    lgl = LittleGreenLight()

    constituents = lgl.get_addresses(constituent_id=123)
    assert [x['postal_code'] for x in constituents] == ['60603']

    constituents = lgl.get_addresses(constituent_id=123, traverse=False)
    assert [x['postal_code'] for x in constituents] == ['60603']

def test_get_lgl_email_addresses(monkeypatch):
    monkeypatch.setattr('requests.get',
                        lambda *args, **kwargs: lgl_request(*args, **kwargs))

    lgl = LittleGreenLight()

    constituents = lgl.get_email_addresses(constituent_id=123)
    assert [x['address'] for x in constituents] == ['carl@camels.com',
					            'jabber@parrots.com']

    constituents = lgl.get_email_addresses(constituent_id=123, traverse=False)
    assert [x['address'] for x in constituents] == ['carl@camels.com',
					    	    'jabber@parrots.com']


def lgl_request(url, headers=None):
    """Mocks reponses based on the documentation found at
    https://api.littlegreenlight.com/api-docs/static.html"""
    base_url = 'https://api.littlegreenlight.com/api/v1'
    if url.startswith(base_url + '/test'):
        return fake_request(text="""{"test": "success"}""",
                            status_code=200,
                            auth_method='header',
                            headers=headers)
    if url == base_url + '/traverse?offset=0':
        return fake_request(text=FIRST_TRAVERSE,
                            status_code=200,
                            auth_method='header',
                            headers=headers)
    if url == base_url + '/traverse?offset=2':
        return fake_request(text=SECOND_TRAVERSE,
                            status_code=200,
                            auth_method='header',
                            headers=headers)
    if url == base_url + '/traverse?offset=4':
        return fake_request(text=THIRD_TRAVERSE,
                            status_code=200,
                            auth_method='header',
                            headers=headers)
    if '/street_addresses' in url:
        return fake_request(text=STREET_ADDRESSES,
                            status_code=200,
                            auth_method='header',
                            headers=headers)
    if '/email_addresses' in url:
        return fake_request(text=EMAIL_ADDRESSES,
                            status_code=200,
                            auth_method='header',
                            headers=headers)
    if url.startswith(base_url + '/constituents'):
        return fake_request(text=CONSTITUENTS,
                            status_code=200,
                            auth_method='header',
                            headers=headers)

#########################################################
# Example API responses derived from
# https://api.littlegreenlight.com/api-docs/static.html
##########################################################

FIRST_TRAVERSE = """
{
  "next_link": "https://api.littlegreenlight.com/api/v1/traverse?offset=2",
  "items": ["carl", "carla"]
}
"""

SECOND_TRAVERSE = """
{
  "next_link": "",
  "items": ["sheep", "sleepy_sheep"]
}
"""

THIRD_TRAVERSE = """
{
  "next_link": "",
  "items": ["jabber", "chester"]
}
"""

CONSTITUENTS = """
{
  "api_version": "1.0",
  "items_count": 2,
  "total_items": 106,
  "limit": 2,
  "offset": 0,
  "next_item": 0,
  "next_link": "",
  "item_type": "constituent",
  "items": [
    {
      "id": 100,
      "external_constituent_id": "",
      "is_org": false,
      "constituent_contact_type_id": 1177,
      "constituent_contact_type_name": "Primary",
      "prefix": null,
      "first_name": "Bruce",
      "middle_name": "",
      "last_name": "Adler",
      "suffix": null,
      "spouse_name": "",
      "org_name": "",
      "job_title": null,
      "addressee": "Bruce Adler",
      "salutation": "Bruce",
      "sort_name": "Adler, Bruce",
      "constituent_interest_level_id": null,
      "constituent_interest_level_name": null,
      "constituent_rating_id": null,
      "constituent_rating_name": null,
      "is_deceased": false,
      "deceased_date": null,
      "annual_report_name": "Bruce Adler",
      "birthday": null,
      "gender": null,
      "maiden_name": "",
      "nick_name": "",
      "spouse_nick_name": "",
      "date_added": "2017-09-21",
      "alt_salutation": "Bruce",
      "alt_addressee": "Bruce Adler",
      "honorary_name": "Bruce Adler",
      "assistant_name": null,
      "marital_status_id": null,
      "marital_status_name": null,
      "is_anon": false,
      "created_at": "2017-09-21T22:53:08Z",
      "updated_at": "2018-12-18T20:05:25Z"
    },
    {
      "id": 101,
      "external_constituent_id": "t00012",
      "is_org": false,
      "constituent_contact_type_id": 1180,
      "constituent_contact_type_name": "Other",
      "prefix": null,
      "first_name": "Susan",
      "middle_name": "",
      "last_name": "Alexander",
      "suffix": null,
      "spouse_name": "",
      "org_name": "Citizen Kane",
      "job_title": null,
      "addressee": "Mrs. Susan Alexander",
      "salutation": "Susan",
      "sort_name": "Alexander, Susan",
      "constituent_interest_level_id": null,
      "constituent_interest_level_name": null,
      "constituent_rating_id": null,
      "constituent_rating_name": null,
      "is_deceased": false,
      "deceased_date": null,
      "annual_report_name": "Mrs. Susan Alexander",
      "birthday": "1909-01-01",
      "gender": null,
      "maiden_name": "",
      "nick_name": "",
      "spouse_nick_name": "",
      "date_added": "2014-07-23",
      "alt_salutation": "Susan",
      "alt_addressee": "Mrs. Susan Alexander",
      "honorary_name": "Mrs. Susan Alexander",
      "assistant_name": null,
      "marital_status_id": null,
      "marital_status_name": null,
      "is_anon": true,
      "created_at": "2014-07-23T16:47:52Z",
      "updated_at": "2019-08-14T18:30:13Z"
    }
  ]
}
"""

STREET_ADDRESSES = """
{
  "api_version": "1.0",
  "items_count": 1,
  "total_items": 1,
  "limit": 25,
  "offset": 0,
  "item_type": "street_address",
  "items": [
    {
      "id": 3,
      "item_id": 952156,
      "item_type": "Constituent",
      "street": "711 Calhoun Street",
      "city": "Chicago",
      "state": "IL",
      "country": "US",
      "postal_code": "60603",
      "county": null,
      "street_address_type_id": 1,
      "street_type_name": "Home",
      "is_preferred": true,
      "not_current": false,
      "parent_id": null,
      "seasonal_from": "01-01",
      "seasonal_to": "12-31",
      "seasonal": null,
      "lat": null,
      "lng": null,
      "zip5": "60603",
      "verified": false,
      "verified_on": null,
      "created_at": "2014-07-23T16:47:53Z",
      "updated_at": "2018-11-30T18:25:41Z"
    }
  ]
}
"""

EMAIL_ADDRESSES = """
{
  "api_version": "1.0",
  "items_count": 2,
  "total_items": 2,
  "limit": 25,
  "offset": 0,
  "item_type": "email_address",
  "items": [
    {
      "id": 281309,
      "item_id": 952156,
      "item_type": "Constituent",
      "address": "carl@camels.com",
      "email_address_type_id": 1,
      "email_type_name": "Home",
      "is_preferred": true,
      "not_current": false,
      "parent_id": null,
      "created_at": "2014-07-23T16:47:53Z",
      "updated_at": "2017-10-05T21:28:38Z"
    },
    {
      "id": 281533,
      "item_id": 952156,
      "item_type": "Constituent",
      "address": "jabber@parrots.com",
      "email_address_type_id": 2,
      "email_type_name": "Work",
      "is_preferred": false,
      "not_current": false,
      "parent_id": null,
      "created_at": "2018-06-08T18:58:34Z",
      "updated_at": "2018-06-08T18:58:35Z"
    }
  ]
}
"""
