
import builtins
import pytest
from crawler.utils import is_same_domain, normalize_url, get_absolute_url

def test_is_same_domain_exact_match():
    """
    Test case 1: Checks that the function correctly identifies a URL on the same domain.
    """
    assert is_same_domain("https://example.com", "https://example.com/page") is True

@pytest.mark.parametrize("link", [
    "http://example.com/",
    "https://example.com",
    "https://example.com/other",
])
def test_is_same_domain_protocol_does_not_matter(link):
    """
    Test case 2: Uses parametrize to run the same test with different inputs.
    It verifies that the function correctly identifies links on the same domain,
    regardless of whether the protocol is 'http' or 'https'.
    """
    assert is_same_domain("http://example.com", link) is True

@pytest.mark.parametrize("link", [
    "https://sub.example.com/",
    "https://other.com",
    "https://example.org",
])
def test_is_same_domain_rejects_subdomains_and_others(link):
    """
    Test case 3: Again using parametrize, this test checks that the function
    correctly rejects URLs from different domains or subdomains.
    This is critical for a crawler to stay within its designated website.
    """
    assert is_same_domain("https://example.com", link) is False

def test_normalize_url_strips_trailing_slash_and_query_and_fragment():
    """
    Test case 4: Ensures the 'normalize_url' function cleans up a URL by
    removing a trailing slash, any query parameters (like '?q=1'), and
    URL fragments (like '#frag').
    """
    assert normalize_url("https://example.com/path/?q=1#frag") == "https://example.com/path"

def test_normalize_url_keeps_root_path():
    """
    Test case 5: Verifies that a root URL with a trailing slash is correctly
    normalized to a clean root URL without the slash.
    """
    assert normalize_url("https://example.com/") == "https://example.com"

def test_get_absolute_url_joins_relative():
    """
    Test case 6: Checks that the 'get_absolute_url' function correctly converts
    relative URLs into full, absolute URLs.
    It tests three different types of relative links:
    - "../other": A link that goes up one directory.
    - "/root": A link that goes to the root of the website.
    - "child": A link to a child page in the current directory.
    """
    base = "https://example.com/dir/page"
    assert get_absolute_url(base, "../other") == "https://example.com/other"
    assert get_absolute_url(base, "/root") == "https://example.com/root"
    assert get_absolute_url(base, "child") == "https://example.com/dir/child"
