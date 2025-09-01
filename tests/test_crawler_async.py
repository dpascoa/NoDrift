
import asyncio
import pytest

from crawler.crawler import Crawler

class FakeResponse:
    """
    A fake object that mimics a web server's response.
    This lets us simulate different scenarios like successful pages,
    errors (404), or non-HTML content without connecting to the internet.
    """
    def __init__(self, status=200, content_type='text/html', body=''):
        self.status = status
        self.content_type = content_type
        self._body = body

    async def text(self):
        return self._body

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

class FakeSession:
    """
    A fake object that mimics an aiohttp.ClientSession.
    It provides a 'get' method that returns our FakeResponse instead
    of making an actual web request.
    """
    def __init__(self, response: FakeResponse):
        self._response = response
        self.closed = False

    def get(self, url, timeout=None):
        return self._response

    async def close(self):
        self.closed = True

@pytest.mark.asyncio
# Test case 1:
async def test_fetch_and_process_skips_non_200():
    """
    Ensures the crawler ignores pages with a non-200 status code.
    Simulates a 404 "Not Found" error.
    """
    # Setup crawler and fake session
    c = Crawler("https://example.com")
    c.session = FakeSession(FakeResponse(status=404, content_type='text/html', body='ignored'))
    from collections import deque
    dq = deque()
    # Run fetch_and_process and check results
    await c.fetch_and_process("https://example.com", dq)
    assert c.pages_crawled == 0
    assert list(dq) == []

@pytest.mark.asyncio
# Test case 2:
async def test_fetch_and_process_skips_non_html():
    """
    Ensures the crawler only processes pages with HTML content.
    Simulates a JSON response, which should be ignored.
    """
    # Setup crawler and fake session
    c = Crawler("https://example.com")
    c.session = FakeSession(FakeResponse(status=200, content_type='application/json', body='{}'))
    from collections import deque
    dq = deque()
    # Run fetch_and_process and check results
    await c.fetch_and_process("https://example.com", dq)
    assert c.pages_crawled == 0
    assert list(dq) == []

@pytest.mark.asyncio
# Test case 3:
async def test_fetch_and_process_enqueues_links_and_counts_pages():
    """
    Ensures the crawler correctly finds and adds valid links to the queue.
    Also checks that it correctly counts the page.
    """
    # HTML with various types of links
    html = """
    <a href="/a"></a>
    <a href="https://example.com/b/"></a>
    <a href="https://other.com/c"></a>
    <a href="#frag"></a>
    <a href="mailto:x@example.com"></a>
    <a href="javascript:void(0)"></a>
    """
    c = Crawler("https://example.com")
    c.session = FakeSession(FakeResponse(status=200, content_type='text/html', body=html))
    from collections import deque
    dq = deque()
    # Run fetch_and_process and check results
    await c.fetch_and_process("https://example.com", dq)
    assert c.pages_crawled == 1
    assert set(dq) == {"https://example.com/a", "https://example.com/b", "https://example.com"}

@pytest.mark.asyncio
# Test case 4:
async def test_start_uses_fake_client_and_closes_session(monkeypatch):
    """
    Ensures the crawler's main 'start' function properly initializes a session and closes it when done.
    Uses monkeypatch to replace parts of the code for testing.
    """
    # Track calls to fetch_and_process
    calls = {"count": 0}

    async def fake_fetch_and_process(self, url, queue=None):
        calls["count"] += 1

    import crawler.crawler as crawler_mod

    class FakeClientSession:
        def __init__(self): self.closed = False
        async def close(self): self.closed = True
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): return False
        def head(self, url, timeout=None, **kwargs):
            class FakeHeadResponse:
                status = 200
                async def __aenter__(self): return self
                async def __aexit__(self, exc_type, exc, tb): return False
            return FakeHeadResponse()

    # Monkeypatch aiohttp.ClientSession and Crawler.fetch_and_process
    monkeypatch.setattr(crawler_mod.aiohttp, "ClientSession", FakeClientSession)
    monkeypatch.setattr(crawler_mod.Crawler, "fetch_and_process", fake_fetch_and_process, raising=False)

    # Run start and check session closed
    c = Crawler("https://example.com")
    await c.start()
    assert c.session.closed is True
