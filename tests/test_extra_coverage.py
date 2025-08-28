
import pytest
from crawler.crawler import Crawler
import crawler.crawler as crawler_mod

class BoomSession:
    def get(self, url, timeout=None):
        raise RuntimeError("boom")
    async def close(self):
        pass

@pytest.mark.asyncio
async def test_fetch_and_process_exception_branch(capsys):
    """
    Test case 1: Tests that the crawler logs an error when a request fails and does not add new links to the queue.
    """
    c = Crawler("https://example.com")
    c.session = BoomSession()
    from collections import deque
    dq = deque()
    await c.fetch_and_process("https://example.com", dq)
    out = capsys.readouterr().out
    assert "Error fetching https://example.com" in out
    assert list(dq) == []

@pytest.mark.asyncio
async def test_start_skips_already_visited(monkeypatch):
    """
    Test case 2: Tests that the crawler skips already-visited URLs by checking the visited set before fetching.
    """
    class FakeClientSession:
        async def close(self): pass

    async def fake_fetch_and_process(self, url, queue):
        raise AssertionError("fetch_and_process should not be called")

    monkeypatch.setattr(crawler_mod.aiohttp, "ClientSession", FakeClientSession)
    monkeypatch.setattr(crawler_mod.Crawler, "fetch_and_process", fake_fetch_and_process, raising=False)

    c = Crawler("https://example.com")
    c.visited.add("https://example.com")
    await c.start()
