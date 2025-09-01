import pytest
from crawler.utils import validate_and_complete_url
from crawler.crawler import Crawler

class TestURLValidation:
    """Test cases for URL validation and completion functionality"""
    
    # Test case 1:
    def test_complete_urls_pass_through(self):
        """
        Checks that complete URLs pass through unchanged.
        """
        complete_urls = [
            "https://example.com",
            "http://example.com",
            "https://www.example.com",
            "http://www.example.com/path",
            "https://subdomain.example.com"
        ]
        
        for url in complete_urls:
            result = validate_and_complete_url(url)
            assert result == url
    
    # Test case 2:
    def test_domain_only_gets_protocol(self):
        """
        Checks that domain-only URLs get https:// protocol added.
        """
        test_cases = [
            ("example.com", "https://example.com"),
            ("google.com", "https://google.com"),
            ("sapo.pt", "https://sapo.pt"),
            ("github.io", "https://github.io")
        ]
        for input_url, expected in test_cases:
            result = validate_and_complete_url(input_url)
            assert result == expected
    
    # Test case 3:
    def test_www_prefix_gets_protocol(self):
        """
        Checks that URLs with www. but no protocol get https:// added.
        """
        test_cases = [
            ("www.example.com", "https://www.example.com"),
            ("www.sapo.pt", "https://www.sapo.pt"),
            ("www.google.com/search", "https://www.google.com/search")
        ]
        
        for input_url, expected in test_cases:
            result = validate_and_complete_url(input_url)
            assert result == expected
    
    # Test case 4:
    def test_double_www_gets_cleaned(self):
        """
        Checks that double www. prefixes are cleaned to a single www.
        """
        result = validate_and_complete_url("www.www.example.com")
        assert result == "https://www.example.com"
    
    # Test case 5:
    def test_subdomains_work(self):
        """
        Checks that subdomains are properly handled.
        """
        test_cases = [
            ("api.example.com", "https://api.example.com"),
            ("mail.google.com", "https://mail.google.com"),
            ("https://api.github.com", "https://api.github.com")  # Already complete
        ]
        for input_url, expected in test_cases:
            result = validate_and_complete_url(input_url)
            assert result == expected
    
    # Test case 6:
    def test_paths_and_queries_preserved(self):
        """
        Checks that paths and query parameters are preserved.
        """
        test_cases = [
            ("example.com/path", "https://example.com/path"),
            ("example.com/path?query=1", "https://example.com/path?query=1"),
            ("www.example.com/path#fragment", "https://www.example.com/path#fragment")
        ]
        for input_url, expected in test_cases:
            result = validate_and_complete_url(input_url)
            assert result == expected
    
    # Test case 7:
    def test_invalid_urls_raise_errors(self):
        """
        Checks that invalid URLs raise ValueError.
        """
        invalid_urls = [
            "",                    # Empty string
            "   ",                # Whitespace only
            "not a url",          # No domain structure
            "http://",            # No domain
            "https://",           # No domain
            "just text",          # Plain text
            "ftp://example.com",  # Valid but gets converted to https
        ]
        
        for invalid_url in invalid_urls[:6]:  # Skip FTP test for now
            with pytest.raises(ValueError):
                validate_and_complete_url(invalid_url)
    
    # Test case 8:
    def test_crawler_accepts_incomplete_urls(self):
        """
        Checks that the crawler accepts incomplete URLs and completes them.
        """
        test_cases = [
            "example.com",
            "www.example.com", 
            "sapo.pt"
        ]
        
        for url in test_cases:
            # Should not raise an exception
            crawler = Crawler(url)
            # The base_url should be properly formatted
            assert crawler.base_url.startswith("https://")
            assert "example.com" in crawler.base_url or "sapo.pt" in crawler.base_url
    
    # Test case 9:
    def test_crawler_rejects_invalid_urls(self):
        """
        Checks that the crawler rejects truly invalid URLs.
        """
        invalid_urls = [
            "",
            "   ",
            "not a url",
            "just text"
        ]
        
        for invalid_url in invalid_urls:
            with pytest.raises(ValueError):
                Crawler(invalid_url)
    
    # Test case 10:
    def test_common_tlds_work(self):
        """
        Checks that common top-level domains work.
        """
        tlds = ["com", "org", "net", "edu", "gov", "pt", "uk", "de", "fr"]
        for tld in tlds:
            url = f"example.{tld}"
            result = validate_and_complete_url(url)
            expected = f"https://example.{tld}"
            assert result == expected
    
    # Test case 11:
    def test_country_code_domains(self):
        """
        Checks that country code domains work properly.
        """
        test_cases = [
            ("sapo.pt", "https://sapo.pt"),
            ("bbc.co.uk", "https://bbc.co.uk"),
            ("example.com.br", "https://example.com.br")
        ]
        for input_url, expected in test_cases:
            result = validate_and_complete_url(input_url)
            assert result == expected