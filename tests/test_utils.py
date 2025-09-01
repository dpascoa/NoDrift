
import builtins
import pytest
from crawler.utils import is_same_domain, normalize_url, get_absolute_url

 # Test case 1:
def test_is_same_domain_exact_match():
    """
    Checks that the function correctly identifies a URL on the same domain.
    """
    assert is_same_domain("https://example.com", "https://example.com/page") is True

 # Test case 2:
@pytest.mark.parametrize("link", [
    "http://example.com/",
    "https://example.com",
    "https://example.com/other",
])
def test_is_same_domain_protocol_does_not_matter(link):
    """
    Uses parametrize to run the same test with different inputs.
    It verifies that the function correctly identifies links on the same domain,
    regardless of whether the protocol is 'http' or 'https'.
    """
    assert is_same_domain("http://example.com", link) is True

 # Test case 3:
@pytest.mark.parametrize("link", [
    "https://sub.example.com/",
    "https://other.com",
    "https://example.org",
])
def test_is_same_domain_rejects_subdomains_and_others(link):
    """
    Checks that is_same_domain returns False for subdomains and other domains.
    """
    assert is_same_domain("https://example.com", link) is False

# Test case 4:
def test_normalize_url_strips_trailing_slash_and_query_and_fragment():
    """
    Checks that normalize_url strips trailing slash, query, and fragment.
    """
    assert normalize_url("https://example.com/path/?q=1#frag") == "https://example.com/path"

 # Test case 5:
def test_normalize_url_keeps_root_path():
    """
    Checks that normalize_url keeps root path without trailing slash.
    """
    assert normalize_url("https://example.com/") == "https://example.com"

 # Test case 6:
def test_get_absolute_url_joins_relative():
    """
    Checks that the 'get_absolute_url' function correctly converts
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
