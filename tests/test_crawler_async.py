
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
async def test_fetch_and_process_skips_non_200():
    """
    Test case 1: Ensures the crawler ignores pages with a non-200 status code.
    Here, we simulate a 404 "Not Found" error.
    """
    c = Crawler("https://example.com")
    c.session = FakeSession(FakeResponse(status=404, content_type='text/html', body='ignored'))
    from collections import deque
    dq = deque()
    await c.fetch_and_process("https://example.com", dq)
    assert c.pages_crawled == 0
    assert list(dq) == []

@pytest.mark.asyncio
async def test_fetch_and_process_skips_non_html():
    """
    Test case 2: Ensures the crawler only processes pages with HTML content.
    Here, we simulate a JSON response, which should be ignored.
    """
    c = Crawler("https://example.com")
    c.session = FakeSession(FakeResponse(status=200, content_type='application/json', body='{}'))
    from collections import deque
    dq = deque()
    await c.fetch_and_process("https://example.com", dq)
    assert c.pages_crawled == 0
    assert list(dq) == []

@pytest.mark.asyncio
async def test_fetch_and_process_enqueues_links_and_counts_pages():
    """
    Test case 3: Ensures the crawler correctly finds and adds valid links to the queue.
    It also checks that it correctly counts the page.
    """
    # A block of HTML with various types of links (valid, invalid, external, etc.)
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
    await c.fetch_and_process("https://example.com", dq)
    assert c.pages_crawled == 1
    assert set(dq) == {"https://example.com/a", "https://example.com/b", "https://example.com"}

@pytest.mark.asyncio
async def test_start_uses_fake_client_and_closes_session(monkeypatch):
    """
    Test case 4: Ensures the crawler's main 'start' function properly
    initializes a session and, importantly, closes it when it's done.
    'monkeypatch' is a powerful pytest feature to temporarily replace
    parts of the code.
    """
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

    monkeypatch.setattr(crawler_mod.aiohttp, "ClientSession", FakeClientSession)
    monkeypatch.setattr(crawler_mod.Crawler, "fetch_and_process", fake_fetch_and_process, raising=False)

    c = Crawler("https://example.com")
    await c.start()
    assert c.session.closed is True
