import argparse
import asyncio
from crawler.crawler import Crawler

def main():
    parser = argparse.ArgumentParser(description="Web Crawler")
    parser.add_argument("base_url", help="Base URL to crawl (e.g., https://example.com)")
    args = parser.parse_args()

    crawler = Crawler(args.base_url)
    asyncio.run(crawler.start())

if __name__ == "__main__":
    main()