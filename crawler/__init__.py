# NoDrift Web Crawler
# Because this crawler doesn't drift to other domains. It stays focused.

from .crawler import Crawler
from .logger import CrawlerLogger
from .utils import validate_and_complete_url, normalize_url, is_same_domain, get_absolute_url, verify_url_accessibility

__version__ = "1.0.0"
__all__ = [
    "Crawler",
    "CrawlerLogger", 
    "validate_and_complete_url",
    "normalize_url",
    "is_same_domain", 
    "get_absolute_url",
    "verify_url_accessibility"
]