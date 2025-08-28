import asyncio
import time
from collections import deque
import aiohttp
from bs4 import BeautifulSoup
from .utils import is_same_domain, normalize_url, get_absolute_url, validate_and_complete_url

class Crawler:
    def __init__(self, base_url: str, max_concurrent: int = 10):
        # Validate and complete the URL before storing it
        try:
            completed_url = validate_and_complete_url(base_url)
            self.base_url = normalize_url(completed_url)
        except ValueError as e:
            raise ValueError(f"Invalid base URL '{base_url}': {e}")
            
        self.visited = set()
        self.pages_crawled = 0                                              # Count successfully crawled pages
        self.semaphore = asyncio.Semaphore(max_concurrent)                  # Limit concurrent requests
        self.session = None
        self.start_time = time.perf_counter()                               # Start timer

    async def start(self):
        self.session = aiohttp.ClientSession()                              # Initialize session
        queue = deque([self.base_url])                                      # Start with the base URL
        tasks = []                                                          # Store pending async tasks       

        try:
            while queue:
                url = queue.popleft()                                       # Get next URL from queue
                if url in self.visited:                                     # Skip if already crawled
                    continue
                
                self.visited.add(url)

                # Schedule fetching & processing
                tasks.append(self.fetch_and_process(url, queue))

                # Process in small batches (5 tasks at a time)
                if len(tasks) >= 5 or not queue:
                    await asyncio.gather(*tasks, return_exceptions=True)
                    tasks = []
        finally:
            # Close session & print stats
            await self.session.close()
            elapsed_time = time.perf_counter() - self.start_time
            print("\nCrawl Summary:")
            print(f"Elapsed Time: {elapsed_time:.2f} seconds")
            print(f"Pages Crawled: {self.pages_crawled}")

    async def fetch_and_process(self, url: str, queue: deque):
        async with self.semaphore:                                          # Limit concurrency        
            try:
                async with self.session.get(url, timeout=10) as response:
                    # Only process HTML pages with 200 OK
                    if response.status != 200 or 'text/html' not in response.content_type:
                        return
                    
                    html = await response.text()                            # Read HTML content
                    self.pages_crawled += 1                                 # Increment page counter
                    links = self.parse_links(url, html)

                    print(f"\n\nPage: {url}")
                    for link in sorted(links):                              # Sort for consistent output
                        print(f"  - {link}")
                        if link not in self.visited:
                            queue.append(link)                              # Enqueue unseen links                       

                    # Print elapsed time after each page
                    elapsed_time = time.perf_counter() - self.start_time
                    print(f"\nElapsed Time: {elapsed_time:.2f} seconds")

            except Exception as e:
                print(f"\n\nError fetching {url}: {e}")

    def parse_links(self, base: str, html: str) -> list:
        soup = BeautifulSoup(html, 'lxml')                                  # Parse HTML      
        links = []

        for a in soup.find_all('a', href=True):                             # Find all anchor tags with href
            link = get_absolute_url(base, a['href'])
            normalized = normalize_url(link)
            if is_same_domain(self.base_url, normalized):                   # Keep only same-domain links  
                links.append(normalized)

        return list(set(links))  # Deduplicate for this page