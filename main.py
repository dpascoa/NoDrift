import argparse
import asyncio
from crawler.crawler import Crawler


def main() -> int:
    """
    Main entry point for the CLI crawler.

    Parses arguments, initializes the crawler, and runs it.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(description="Web Crawler")
    parser.add_argument("base_url", help="Base URL to crawl (e.g., example.com, www.example.com, or https://example.com)")
    args = parser.parse_args()

    try:
        crawler = Crawler(args.base_url)
        print(f"Starting crawl of: {crawler.base_url}")
        asyncio.run(crawler.start())
    except ValueError as e:
        print(f"Error: {e}")
        print("Please provide a valid URL (e.g., example.com, www.example.com, or https://example.com)")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())