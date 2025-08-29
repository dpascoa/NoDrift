from urllib.parse import urlparse, urljoin
import re
import aiohttp
import asyncio

def validate_and_complete_url(url: str) -> str:
    """
    Validates and completes a URL, adding protocol if missing.

    Args:
        url: The URL to validate and complete

    Returns:
        A complete, valid URL with protocol

    Raises:
        ValueError: If the URL is invalid or empty
    """
    if not url or not url.strip():
        raise ValueError("URL cannot be empty")

    url = url.strip()

    # If URL doesn't start with http:// or https://, add https://
    # This check is performed first to ensure proper parsing later.
    if not urlparse(url).scheme:
        # A common and robust way to handle this is to prepend the scheme
        # and let urlparse handle the rest.
        url = 'https://' + url

    # Parse to validate the URL structure and extract components
    parsed = urlparse(url)

    # Validate that we have a proper scheme and netloc (domain)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL format: {url}")

    # Simplified and more robust domain validation using a single regex.
    # This regex checks for a valid domain name, including subdomains and TLDs.
    # It accounts for hyphens and numbers correctly.
    domain_pattern = re.compile(
        r'^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.([a-zA-Z]{2,}|[a-zA-Z]{2,}\.[a-zA-Z]{2,})'
    )
    if not domain_pattern.match(parsed.netloc):
        raise ValueError(f"Invalid domain format: {parsed.netloc}")

    return url

async def verify_url_accessibility(url: str, timeout: int = 10) -> tuple[bool, str]:
    """
    Verify if a URL is accessible by making a HEAD request.

    Args:
        url: The URL to verify
        timeout: Request timeout in seconds

    Returns:
        Tuple of (is_accessible, error_message)
    """
    try:
        async with aiohttp.ClientSession() as session:
            # Using a context manager for the request to ensure it's closed
            async with session.head(url, timeout=timeout, allow_redirects=True) as response:
                if response.status == 200:
                    return True, "URL is accessible"
                elif response.status in [301, 302, 303, 307, 308]:
                    return True, f"URL redirects (Status: {response.status})"
                else:
                    return False, f"Unexpected status code: {response.status}"

    except asyncio.TimeoutError:
        return False, "Request timed out - server may be unreachable"
    except aiohttp.ClientConnectorError:
        return False, "Cannot connect to server - check if domain exists"
    except aiohttp.InvalidURL:
        return False, "Invalid URL format"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

# Check if two URLs belong to the same domain
def is_same_domain(base_url: str, link: str) -> bool:
    # Extracts just the domain (netloc) part of the URLs, e.g. "example.com"
    try:
        base_domain = urlparse(base_url).netloc
        link_domain = urlparse(link).netloc
        return base_domain == link_domain
    except ValueError:
        return False

# Normalize a URL into a standard format
def normalize_url(url: str) -> str:
    # Parse the URL into components: scheme (http/https), domain, path, etc.
    parsed = urlparse(url)
    return parsed.scheme + "://" + parsed.netloc + parsed.path.rstrip('/')

# Convert a relative URL into an absolute one
def get_absolute_url(base: str, link: str) -> str:
    return urljoin(base, link)