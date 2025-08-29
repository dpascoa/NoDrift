import asyncio
import time
from collections import deque
import aiohttp
from bs4 import BeautifulSoup
from .utils import is_same_domain, normalize_url, get_absolute_url, validate_and_complete_url, verify_url_accessibility
from .logger import CrawlerLogger


class Crawler:
    """
    Asynchronous web crawler that stays within the same domain.
    Crawls pages, parses links, and logs progress.
    """

    def __init__(self, base_url: str, max_concurrent: int = 10, enable_logging: bool = True):
        """
        Initialize the Crawler.

        Args:
            base_url (str): The starting URL for the crawl.
            max_concurrent (int, optional): Maximum concurrent requests. Defaults to 10.
            enable_logging (bool, optional): Whether to enable logging. Defaults to True.

        Raises:
            ValueError: If the base URL is invalid.
        """
        # Validate and complete the URL before storing it
        try:
            completed_url = validate_and_complete_url(base_url)
            self.base_url = normalize_url(completed_url)
        except ValueError as e:
            raise ValueError(f"Invalid base URL '{base_url}': {e}")

        self.original_url = base_url  # Store original for logging
        self.to_visit = deque([self.base_url])  # Use a deque for efficient queue operations
        self.visited = set()  # Set to track visited URLs
        self.pages_crawled = 0  # Counter for successfully crawled pages
        self.error_count = 0  # Counter for errors encountered
        self.semaphore = asyncio.Semaphore(max_concurrent)  # Limit concurrent requests
        self.session = None  # aiohttp session (initialized later)
        self.start_time = time.perf_counter()  # Track start time for elapsed calculations

        # Initialize logging if enabled
        self.enable_logging = enable_logging
        self.logger = None
        if enable_logging:
            self.logger = CrawlerLogger(self.base_url)

    async def start(self):
        """
        Start the crawling process.
        Verifies URL accessibility, processes the queue, and handles cleanup.
        """
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
                # Add tasks up to the concurrency limit
                while self.to_visit and len(tasks) < self.semaphore._value:
                    url = self.to_visit.popleft()
                    if url not in self.visited:
                        self.visited.add(url)
                        task = asyncio.create_task(self.fetch_and_process(url))
                        tasks.append(task)

                if tasks:
                    # Wait for the first task to complete
                    done, pending = await asyncio.wait(
                        tasks,
                        return_when=asyncio.FIRST_COMPLETED
                    )

                    for task in done:
                        # Raise if the task had an exception
                        task.result()

                    tasks = list(pending)

                # Log progress periodically if logging is enabled
                if self.logger and self.pages_crawled > 0 and self.pages_crawled % 5 == 0:
                    elapsed = time.perf_counter() - self.start_time
                    self.logger.log_progress(self.pages_crawled, len(self.visited), elapsed)

        finally:
            # Cleanup: Close the session
            if self.session:
                await self.session.close()

            # Calculate elapsed time and print summary
            elapsed_time = time.perf_counter() - self.start_time
            print("\nCrawl Summary:")
            print(f"Elapsed Time: {elapsed_time:.2f} seconds")
            print(f"Pages Crawled: {self.pages_crawled}")
            print(f"Errors: {self.error_count}")

            # Log final summary if logging is enabled
            if self.logger:
                log_file = self.logger.log_summary(
                    self.pages_crawled,
                    len(self.visited),
                    self.error_count,
                    "completed"
                )
                print(f"Log saved to: {log_file}")

    async def fetch_and_process(self, url: str):
        """
        Fetch a URL, process its content, parse links, and add to queue.

        Args:
            url (str): The URL to fetch and process.
        """
        async with self.semaphore:
            try:
                async with self.session.get(url, timeout=10) as response:
                    # Check for success (2xx) or redirects (3xx); skip otherwise
                    if response.status >= 400:
                        if self.logger:
                            self.logger.log_page_skipped(url, "Non-2xx/3xx status", response.status)
                        return

                    # Skip non-HTML content
                    if 'text/html' not in response.content_type:
                        if self.logger:
                            self.logger.log_page_skipped(url, "Non-HTML content", response.status)
                        return

                    html = await response.text()
                    self.pages_crawled += 1
                    links = self.parse_links(url, html)

                    # Log if enabled
                    if self.logger:
                        self.logger.log_page_crawled(url, links, response.status)

                    # Print and add new links to queue
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
        """
        Parse HTML for links within the same domain.

        Args:
            base (str): The base URL for resolving relative links.
            html (str): The HTML content to parse.

        Returns:
            list: List of normalized same-domain links.
        """
        soup = BeautifulSoup(html, 'lxml')
        links = []

        for a in soup.find_all('a', href=True):
            link = get_absolute_url(base, a['href'])
            normalized = normalize_url(link)
            if is_same_domain(self.base_url, normalized):
                links.append(normalized)

        return list(set(links))  # Remove duplicates