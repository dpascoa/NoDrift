import asyncio
import time
from collections import deque
import aiohttp
from bs4 import BeautifulSoup
from .utils import is_same_domain, normalize_url, get_absolute_url, validate_and_complete_url, verify_url_accessibility
from .logger import CrawlerLogger

class Crawler:
    def __init__(self, base_url: str, max_concurrent: int = 10, enable_logging: bool = True):
        # Validate and complete the URL before storing it
        try:
            completed_url = validate_and_complete_url(base_url)
            self.base_url = normalize_url(completed_url)
        except ValueError as e:
            raise ValueError(f"Invalid base URL '{base_url}': {e}")
            
        self.original_url = base_url  # Store original for logging
        self.to_visit = deque([self.base_url]) # Use a deque for the queue
        self.visited = set()
        self.pages_crawled = 0
        self.error_count = 0
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session = None
        self.start_time = time.perf_counter()
        
        # Initialize logging
        self.enable_logging = enable_logging
        self.logger = None
        if enable_logging:
            self.logger = CrawlerLogger(self.base_url)

    async def start(self):
        # First verify the URL is accessible
        try:
            accessible, error_msg = await verify_url_accessibility(self.base_url)
            if not accessible:
                if self.logger:
                    self.logger.log_invalid_url(self.original_url, error_msg)
                    self.logger.log_summary(0, 0, 1, "invalid")
                raise ValueError(f"URL is not accessible: {error_msg}")
        except Exception as e:
            if self.logger:
                self.logger.log_invalid_url(self.original_url, str(e))
                self.logger.log_summary(0, 0, 1, "invalid")
            raise ValueError(f"Cannot verify URL accessibility: {str(e)}")
        
        self.session = aiohttp.ClientSession()
        
        try:
            tasks = []
            while self.to_visit or tasks:
                while self.to_visit and len(tasks) < self.semaphore._value:
                    url = self.to_visit.popleft()
                    if url not in self.visited:
                        self.visited.add(url)
                        task = asyncio.create_task(self.fetch_and_process(url))
                        tasks.append(task)
                
                if tasks:
                    done, pending = await asyncio.wait(
                        tasks,
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    
                    for task in done:
                        # Catch exceptions if any occurred in the task
                        task.result() 

                    tasks = list(pending)

                # Log progress periodically
                if self.logger and self.pages_crawled > 0 and self.pages_crawled % 5 == 0:
                    elapsed = time.perf_counter() - self.start_time
                    self.logger.log_progress(self.pages_crawled, len(self.visited), elapsed)

        finally:
            if self.session:
                await self.session.close()

            elapsed_time = time.perf_counter() - self.start_time
            print("\nCrawl Summary:")
            print(f"Elapsed Time: {elapsed_time:.2f} seconds")
            print(f"Pages Crawled: {self.pages_crawled}")
            print(f"Errors: {self.error_count}")
            
            if self.logger:
                log_file = self.logger.log_summary(
                    self.pages_crawled, 
                    len(self.visited), 
                    self.error_count, 
                    "completed"
                )
                print(f"Log saved to: {log_file}")

    async def fetch_and_process(self, url: str):
        async with self.semaphore:
            try:
                async with self.session.get(url, timeout=10) as response:
                    # Check for redirects or success (2xx and 3xx)
                    if response.status >= 400:
                        if self.logger:
                            self.logger.log_page_skipped(url, "Non-2xx/3xx status", response.status)
                        return
                    
                    if 'text/html' not in response.content_type:
                        if self.logger:
                            self.logger.log_page_skipped(url, "Non-HTML content", response.status)
                        return
                    
                    html = await response.text()
                    self.pages_crawled += 1
                    links = self.parse_links(url, html)

                    if self.logger:
                        self.logger.log_page_crawled(url, links, response.status)

                    print(f"\n\nPage: {url}")
                    for link in sorted(links):
                        print(f"  - {link}")
                        if link not in self.visited:
                            self.to_visit.append(link)

            except Exception as e:
                self.error_count += 1
                error_msg = f"Error fetching {url}: {e}"
                print(f"\n\n{error_msg}")
                
                if self.logger:
                    self.logger.log_error(url, e)

    def parse_links(self, base: str, html: str) -> list:
        soup = BeautifulSoup(html, 'lxml')
        links = []

        for a in soup.find_all('a', href=True):
            link = get_absolute_url(base, a['href'])
            normalized = normalize_url(link)
            if is_same_domain(self.base_url, normalized):
                links.append(normalized)

        return list(set(links))