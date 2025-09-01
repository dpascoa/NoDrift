
import pytest
from crawler.crawler import Crawler
import crawler.crawler as crawler_mod

class BoomSession:
    def get(self, url, timeout=None):
        raise RuntimeError("boom")
    async def close(self):
        pass

@pytest.mark.asyncio
# Test case 1:
async def test_fetch_and_process_exception_branch(capsys):
    """
    Checks that the crawler logs an error when a request fails and does not add new links to the queue.
    """
    # Setup crawler and BoomSession
    c = Crawler("https://example.com")
    c.session = BoomSession()
    from collections import deque
    dq = deque()
    # Run fetch_and_process and check output
    await c.fetch_and_process("https://example.com", dq)
    out = capsys.readouterr().out
    assert "Error fetching https://example.com" in out
    assert list(dq) == []

@pytest.mark.asyncio
# Test case 2:
async def test_start_skips_already_visited(monkeypatch):
    """
    Checks that the crawler skips already-visited URLs by checking the visited set before fetching.
    """
    # Setup fake session and monkeypatch
    class FakeClientSession:
        async def close(self): pass
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): return False
        def head(self, url, timeout=None, **kwargs):
            class FakeHeadResponse:
                status = 200
                async def __aenter__(self): return self
                async def __aexit__(self, exc_type, exc, tb): return False
            return FakeHeadResponse()

    async def fake_fetch_and_process(self, url, queue):
        raise AssertionError("fetch_and_process should not be called")

    monkeypatch.setattr(crawler_mod.aiohttp, "ClientSession", FakeClientSession)
    monkeypatch.setattr(crawler_mod.Crawler, "fetch_and_process", fake_fetch_and_process, raising=False)

    # Add URL to visited and run start
    c = Crawler("https://example.com")
    c.visited.add("https://example.com")
    await c.start()
