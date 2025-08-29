import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'NoDrift' in response.data

def test_start_crawl_missing_url(client):
    response = client.post('/api/start_crawl', json={})
    assert response.status_code == 400
    assert b'URL is required' in response.data

def test_start_crawl_invalid_url(client):
    response = client.post('/api/start_crawl', json={'url': 'not a url'})
    assert response.status_code == 400
    assert (
        b'Invalid domain format' in response.data or
        b'Invalid URL format' in response.data or
        b'Invalid URL' in response.data
    )

def test_crawl_status_not_found(client):
    response = client.get('/api/crawl_status/invalid_session_id')
    assert response.status_code == 404
    assert b'Session not found' in response.data

def test_stop_crawl_not_found(client):
    response = client.post('/api/stop_crawl/invalid_session_id')
    assert response.status_code == 404
    assert b'Session not found' in response.data

def test_download_log_not_found(client):
    response = client.get('/api/download_log/invalid_session_id')
    assert response.status_code == 404
    assert b'Session not found' in response.data
