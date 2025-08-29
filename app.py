from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import asyncio
import threading
import time
import os
from collections import deque
import uuid
import aiohttp
from crawler.crawler import Crawler

app = Flask(__name__)
CORS(app)

# Global dictionary to store active crawl sessions by session_id
crawl_sessions = {}


class WebCrawler(Crawler):
    """
    Web-specific extension of the Crawler class for integration with the Flask app.
    Adds session management and UI update support.
    """

    def __init__(self, base_url: str, session_id: str, max_concurrent: int = 10):
        """
        Initialize the WebCrawler.

        Args:
            base_url (str): The base URL to crawl.
            session_id (str): Unique identifier for the crawl session.
            max_concurrent (int, optional): Maximum concurrent requests. Defaults to 10.
        """
        super().__init__(base_url, max_concurrent, enable_logging=True)
        self.session_id = session_id
        self.status = "initializing"
        self.current_url = ""
        self.found_links = []  # Not used; kept for potential future expansion

    async def start(self):
        """
        Start the crawling process asynchronously.
        Verifies URL accessibility, processes the queue, and updates session status.
        """
        # First verify URL accessibility
        try:
            from crawler.utils import verify_url_accessibility
            accessible, error_msg = await verify_url_accessibility(self.base_url)
            if not accessible:
                self.status = "invalid"
                crawl_sessions[self.session_id]["status"] = "invalid"
                crawl_sessions[self.session_id]["error"] = f"Invalid URL: {error_msg}"
                if self.logger:
                    self.logger.log_invalid_url(self.original_url, error_msg)
                    self.logger.log_summary(0, 0, 1, "invalid")
                return
        except Exception as e:
            self.status = "invalid"
            crawl_sessions[self.session_id]["status"] = "invalid"
            crawl_sessions[self.session_id]["error"] = f"URL verification failed: {str(e)}"
            if self.logger:
                self.logger.log_invalid_url(self.original_url, str(e))
                self.logger.log_summary(0, 0, 1, "invalid")
            return

        self.status = "running"
        crawl_sessions[self.session_id]["status"] = "running"

        self.session = aiohttp.ClientSession()
        queue = deque([self.base_url])
        tasks = []

        try:
            while queue and self.status == "running":
                url = queue.popleft()
                if url in self.visited:
                    continue

                self.visited.add(url)
                self.current_url = url

                # Update session data for real-time UI polling
                crawl_sessions[self.session_id].update({
                    "current_url": url,
                    "pages_crawled": self.pages_crawled,
                    "elapsed_time": time.perf_counter() - self.start_time,
                    "total_found": len(self.visited)
                })

                tasks.append(self.fetch_and_process(url, queue))

                # Process tasks in batches for efficiency
                if len(tasks) >= 5 or not queue:
                    await asyncio.gather(*tasks, return_exceptions=True)
                    tasks = []

        except Exception as e:
            self.status = "error"
            crawl_sessions[self.session_id]["status"] = "error"
            crawl_sessions[self.session_id]["error"] = str(e)
            if self.logger:
                self.logger.log_error("general", e)
        finally:
            if self.session:
                await self.session.close()

            elapsed_time = time.perf_counter() - self.start_time
            self.status = "completed" if self.status == "running" else self.status

            # Log final summary if logging is enabled
            if self.logger:
                final_status = self.status if self.status != "running" else "completed"
                log_file = self.logger.log_summary(
                    self.pages_crawled,
                    len(self.visited),
                    self.error_count,
                    final_status
                )
                crawl_sessions[self.session_id]["log_file"] = log_file

            # Update final session data
            crawl_sessions[self.session_id].update({
                "status": self.status,
                "elapsed_time": elapsed_time,
                "pages_crawled": self.pages_crawled,
                "error_count": self.error_count
            })

    async def fetch_and_process(self, url: str, queue: deque):
        """
        Fetch and process a single URL, parsing links and updating the queue.

        Args:
            url (str): The URL to fetch.
            queue (deque): The queue of URLs to visit.
        """
        async with self.semaphore:
            try:
                async with self.session.get(url, timeout=10) as response:
                    if response.status != 200:
                        if self.logger:
                            self.logger.log_page_skipped(url, "Non-200 status", response.status)
                        return

                    if 'text/html' not in response.content_type:
                        if self.logger:
                            self.logger.log_page_skipped(url, "Non-HTML content", response.status)
                        return

                    html = await response.text()
                    self.pages_crawled += 1
                    links = self.parse_links(url, html)

                    # Log the crawled page if logging is enabled
                    if self.logger:
                        self.logger.log_page_crawled(url, links, response.status)

                    # Store found links for this page in session data
                    page_links = []
                    for link in sorted(links):
                        page_links.append(link)
                        if link not in self.visited:
                            queue.append(link)

                    # Update session with new page data for detailed view
                    crawl_sessions[self.session_id]["pages"].append({
                        "url": url,
                        "links": page_links,
                        "timestamp": time.time()
                    })

            except Exception as e:
                self.error_count += 1
                if self.logger:
                    self.logger.log_error(url, e)
                print(f"Error fetching {url}: {e}")


def run_crawler_async(base_url: str, session_id: str):
    """
    Run the crawler in a separate thread using an asyncio event loop.

    Args:
        base_url (str): The base URL to crawl.
        session_id (str): Unique session identifier.
    """
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            crawler = WebCrawler(base_url, session_id)
            loop.run_until_complete(crawler.start())
        except ValueError as e:
            # Handle invalid URL during crawler initialization
            crawl_sessions[session_id]["status"] = "invalid"
            crawl_sessions[session_id]["error"] = str(e)
        except Exception as e:
            crawl_sessions[session_id]["status"] = "error"
            crawl_sessions[session_id]["error"] = str(e)

    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()


@app.route('/')
def index():
    """Render the main index page."""
    return render_template('index.html')


@app.route('/api/start_crawl', methods=['POST'])
def start_crawl():
    """
    API endpoint to start a new crawl session.
    Validates the URL and starts the crawler in the background.
    """
    data = request.get_json()
    base_url = data.get('url')

    if not base_url:
        return jsonify({"error": "URL is required"}), 400

    # Validate and complete the URL
    try:
        from crawler.utils import validate_and_complete_url, normalize_url
        completed_url = validate_and_complete_url(base_url)
        normalized_url = normalize_url(completed_url)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Invalid URL format: {str(e)}"}), 400

    # Generate unique session ID
    session_id = str(uuid.uuid4())

    # Initialize session data
    crawl_sessions[session_id] = {
        "base_url": normalized_url,
        "original_url": base_url,
        "completed_url": completed_url,
        "status": "initializing",
        "pages_crawled": 0,
        "elapsed_time": 0,
        "current_url": "",
        "total_found": 0,
        "error_count": 0,
        "pages": [],  # List of crawled pages for detailed view
        "start_time": time.time(),
        "log_file": None
    }

    # Start crawling in background thread
    run_crawler_async(normalized_url, session_id)

    return jsonify({
        "session_id": session_id,
        "completed_url": completed_url,
        "message": f"Starting crawl of {completed_url}"
    })


@app.route('/api/crawl_status/<session_id>')
def get_crawl_status(session_id: str):
    """
    API endpoint to get the current status of a crawl session.

    Args:
        session_id (str): The session ID to query.

    Returns:
        JSON with session data or error if not found.
    """
    if session_id not in crawl_sessions:
        return jsonify({"error": "Session not found"}), 404

    return jsonify(crawl_sessions[session_id])


@app.route('/api/stop_crawl/<session_id>', methods=['POST'])
def stop_crawl(session_id: str):
    """
    API endpoint to stop an active crawl session.

    Args:
        session_id (str): The session ID to stop.

    Returns:
        JSON confirmation or error.
    """
    if session_id not in crawl_sessions:
        return jsonify({"error": "Session not found"}), 404

    crawl_sessions[session_id]["status"] = "stopped"
    return jsonify({"message": "Crawl stopped"})


@app.route('/api/download_log/<session_id>')
def download_log(session_id: str):
    """
    API endpoint to download the log file for a crawl session.
    Triggers browser download with save dialog.

    Args:
        session_id (str): The session ID.

    Returns:
        File attachment or error if not found.
    """
    if session_id not in crawl_sessions:
        return jsonify({"error": "Session not found"}), 404

    session = crawl_sessions[session_id]
    log_file = session.get("log_file")

    if not log_file or not os.path.exists(log_file):
        return jsonify({"error": "Log file not found"}), 404

    return send_file(log_file, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, port=5000)