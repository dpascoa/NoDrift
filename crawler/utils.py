from urllib.parse import urlparse, urljoin
import re

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
    
    # Remove common prefixes that users might accidentally include
    if url.startswith('www.www.'):
        url = url[4:]  # Remove one 'www.'
    
    # If URL doesn't start with http:// or https://, add https://
    if not re.match(r'^https?://', url):
        # If it doesn't start with www., add it for better compatibility
        if not url.startswith('www.'):
            # Check if it looks like a domain (contains a dot and no spaces)
            if '.' in url and ' ' not in url:
                url = 'www.' + url
        url = 'https://' + url
    
    # Parse to validate the URL structure
    parsed = urlparse(url)
    
    # Validate that we have a proper scheme and netloc
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL format: {url}")
    
    # Validate domain format (basic check)
    domain = parsed.netloc
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.([a-zA-Z]{2,}|[a-zA-Z]{2,}\.[a-zA-Z]{2,})$', domain):
        # Allow for subdomains
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]$', domain):
            raise ValueError(f"Invalid domain format: {domain}")
    
    return url

# Check if two URLs belong to the same domain
def is_same_domain(base_url: str, link: str) -> bool:
    # Extracts just the domain (netloc) part of the URLs, e.g. "example.com"
    base_domain = urlparse(base_url).netloc
    link_domain = urlparse(link).netloc
    return base_domain == link_domain

# Normalize a URL into a standard format
def normalize_url(url: str) -> str:
    # Parse the URL into components: scheme (http/https), domain, path, etc.
    parsed = urlparse(url)
    return parsed.scheme + "://" + parsed.netloc + parsed.path.rstrip('/')

# Convert a relative URL into an absolute one
def get_absolute_url(base: str, link: str) -> str:
    return urljoin(base, link)