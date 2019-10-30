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


def lgl_request(url, headers=None):
    """Mocks reponses based on the documentation found at
    https://api.littlegreenlight.com/api-docs/static.html"""
    base_url = 'https://api.littlegreenlight.com/api/v1'
    if url.startswith(base_url + '/test'):
        return fake_request(text="""{"test": "success"}""",
                            status_code=200,
                            auth_method='header',
                            headers=headers)
