import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

 # Test case 1:
def test_index_route(client):
    """
    Checks that the index route returns status 200 and contains 'NoDrift'.
    """
    # Send GET request to index
    response = client.get('/')
    assert response.status_code == 200
    assert b'NoDrift' in response.data

 # Test case 2:
def test_start_crawl_missing_url(client):
    """
    Checks that starting a crawl without a URL returns status 400 and error message.
    """
    # Send POST request with missing URL
    response = client.post('/api/start_crawl', json={})
    assert response.status_code == 400
    assert b'URL is required' in response.data

 # Test case 3:
def test_start_crawl_invalid_url(client):
    """
    Checks that starting a crawl with an invalid URL returns status 400 and error message.
    """
    # Send POST request with invalid URL
    response = client.post('/api/start_crawl', json={'url': 'not a url'})
    assert response.status_code == 400
    assert (
        b'Invalid domain format' in response.data or
        b'Invalid URL format' in response.data or
        b'Invalid URL' in response.data
    )

 # Test case 4:
def test_crawl_status_not_found(client):
    """
    Checks that requesting crawl status for an invalid session returns 404 and error message.
    """
    # Send GET request for invalid session
    response = client.get('/api/crawl_status/invalid_session_id')
    assert response.status_code == 404
    assert b'Session not found' in response.data

 # Test case 5:
def test_stop_crawl_not_found(client):
    """
    Checks that stopping a crawl for an invalid session returns 404 and error message.
    """
    # Send POST request to stop crawl for invalid session
    response = client.post('/api/stop_crawl/invalid_session_id')
    assert response.status_code == 404
    assert b'Session not found' in response.data

 # Test case 6:
def test_download_log_not_found(client):
    """
    Checks that downloading a log for an invalid session returns 404.
    """
    # Send GET request to download log for invalid session
    response = client.get('/api/download_log/invalid_session_id')
    assert response.status_code == 404
    assert b'Session not found' in response.data
