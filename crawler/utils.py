from urllib.parse import urlparse, urljoin

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