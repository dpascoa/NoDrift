import logging
import os
import time
from datetime import datetime
from typing import List, Optional

class CrawlerLogger:
    """
    Comprehensive logging utility for the web crawler.
    Creates detailed logs with timestamps, statistics, and all discovered links.
    """
    
    def __init__(self, base_url: str, log_dir: str = "logs"):
        self.base_url = base_url
        self.log_dir = log_dir
        self.start_time = time.time()
        
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Generate log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain = self._extract_domain(base_url)
        self.log_filename = f"{log_dir}/crawl_{domain}_{timestamp}.txt"
        
        # Initialize logging
        self.logger = logging.getLogger(f"crawler_{timestamp}")
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers = []
        
        # Create file handler
        file_handler = logging.FileHandler(self.log_filename, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
        
        # Log session start
        self.log_start()
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain name for filename"""
        from urllib.parse import urlparse
        try:
            domain = urlparse(url).netloc
            # Clean domain for filename (remove www, replace dots)
            domain = domain.replace('www.', '').replace('.', '_')
            return domain[:20]  # Limit length
        except:
            return "unknown"
    
    def log_start(self):
        """Log the start of a crawling session"""
        self.logger.info("=" * 80)
        self.logger.info("NODRIFT WEB CRAWLER - SESSION START")
        self.logger.info("=" * 80)
        self.logger.info(f"Target URL: {self.base_url}")
        self.logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Log File: {self.log_filename}")
        self.logger.info("=" * 80)
    
    def log_page_crawled(self, url: str, links: List[str], status_code: int = 200):
        """Log a successfully crawled page with its links"""
        self.logger.info(f"CRAWLED: {url} (Status: {status_code})")
        self.logger.info(f"  → Found {len(links)} links:")
        for link in sorted(links):
            self.logger.info(f"    • {link}")
        self.logger.info("")  # Empty line for readability
    
    def log_page_skipped(self, url: str, reason: str, status_code: Optional[int] = None):
        """Log a skipped page with reason"""
        status_info = f" (Status: {status_code})" if status_code else ""
        self.logger.info(f"SKIPPED: {url}{status_info} - {reason}")
    
    def log_error(self, url: str, error: Exception):
        """Log an error encountered during crawling"""
        self.logger.error(f"ERROR: {url} - {str(error)}")
    
    def log_invalid_url(self, original_url: str, error_msg: str):
        """Log invalid URL attempts"""
        self.logger.error(f"INVALID URL: '{original_url}' - {error_msg}")
    
    def log_progress(self, pages_crawled: int, total_found: int, elapsed_time: float):
        """Log current progress statistics"""
        self.logger.info(f"PROGRESS: {pages_crawled} pages crawled, {total_found} URLs found, {elapsed_time:.2f}s elapsed")
    
    def log_summary(self, pages_crawled: int, total_urls_found: int, total_errors: int, status: str):
        """Log final crawling statistics"""
        elapsed_time = time.time() - self.start_time
        
        self.logger.info("=" * 80)
        self.logger.info("CRAWLING SESSION SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"Target URL: {self.base_url}")
        self.logger.info(f"Final Status: {status.upper()}")
        self.logger.info(f"Pages Successfully Crawled: {pages_crawled}")
        self.logger.info(f"Total URLs Found: {total_urls_found}")
        self.logger.info(f"Errors Encountered: {total_errors}")
        self.logger.info(f"Total Elapsed Time: {elapsed_time:.2f} seconds")
        
        if pages_crawled > 0:
            self.logger.info(f"Average Time per Page: {elapsed_time/pages_crawled:.2f} seconds")
        
        self.logger.info(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 80)
        
        # Close logging handlers to ensure file is written
        for handler in self.logger.handlers:
            handler.close()
        
        return self.log_filename
    
    def get_log_filename(self) -> str:
        """Get the current log filename"""
        return self.log_filename