
import pytest
from crawler.crawler import Crawler

HTML_SAMPLE = """
<html><body>
  <a href="/about">About</a>
  <a href="https://example.com/contact/">Contact</a>
  <a href="https://sub.example.com/page">Subdomain</a>
  <a href="https://other.com/">Other</a>
  <a href="mailto:test@example.com">Mail</a>
  <a href="javascript:void(0)">JS</a>
  <a href="#fragment">Fragment</a>
  <a href="/about?utm_source=x">About with query</a>
  <a>Missing href</a>
</body></html>
"""

def test_init_normalizes_base_url():
    """
    Test case 1: Check that the crawler's base URL is always stored in a clean, consistent format.
    The trailing slash is removed for consistency.
    """
    c = Crawler("https://example.com/")
    assert c.base_url == "https://example.com"

def test_parse_links_filters_and_normalizes():
    """
    Test case 2: Verify that the `parse_links` method correctly finds, filters, and normalizes URLs.
    It should only return valid links on the same domain.
    """
    c = Crawler("https://example.com")
    links = c.parse_links("https://example.com", HTML_SAMPLE)
    # Should include about/contact and a normalized root for the fragment link
    assert set(links) == {
        "https://example.com/about",
        "https://example.com/contact",
        "https://example.com",
    }

def test_parse_links_deduplicates_and_same_domain_only():
    """
    Test case 3: Ensure `parse_links` handles duplicate links and only extracts links from the same domain.
    """
    c = Crawler("https://example.com")
    html = '<a href="/a"></a><a href="https://example.com/a/"></a><a href="https://other.com/a"></a>'
    links = c.parse_links("https://example.com", html)

    # Check that the link "https://example.com/a" appears exactly once. This proves deduplication.
    assert links.count("https://example.com/a") == 1

    # Check that every single link in the resulting list starts with our base URL.
    # This proves that external links (like "other.com") are correctly filtered out.
    assert all(u.startswith("https://example.com") for u in links)
