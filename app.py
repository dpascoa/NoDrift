from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import asyncio
import threading
import time
from collections import deque
import uuid
import aiohttp
from crawler.crawler import Crawler

app = Flask(__name__)
CORS(app)

# Store active crawl sessions
crawl_sessions = {}

class WebCrawler(Crawler):
    def __init__(self, base_url: str, session_id: str, max_concurrent: int = 10):
        super().__init__(base_url, max_concurrent)
        self.session_id = session_id
        self.status = "initializing"
        self.current_url = ""
        self.found_links = []
        
    async def start(self):
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
                
                # Update session data
                crawl_sessions[self.session_id].update({
                    "current_url": url,
                    "pages_crawled": self.pages_crawled,
                    "elapsed_time": time.perf_counter() - self.start_time,
                    "total_found": len(self.visited)
                })

                tasks.append(self.fetch_and_process(url, queue))

                if len(tasks) >= 5 or not queue:
                    await asyncio.gather(*tasks, return_exceptions=True)
                    tasks = []
                    
        except Exception as e:
            self.status = "error"
            crawl_sessions[self.session_id]["status"] = "error"
            crawl_sessions[self.session_id]["error"] = str(e)
        finally:
            if self.session:
                await self.session.close()
            
            elapsed_time = time.perf_counter() - self.start_time
            self.status = "completed"
            crawl_sessions[self.session_id].update({
                "status": "completed",
                "elapsed_time": elapsed_time,
                "pages_crawled": self.pages_crawled
            })

    async def fetch_and_process(self, url: str, queue: deque):
        async with self.semaphore:
            try:
                async with self.session.get(url, timeout=10) as response:
                    if response.status != 200 or 'text/html' not in response.content_type:
                        return
                    
                    html = await response.text()
                    self.pages_crawled += 1
                    links = self.parse_links(url, html)
                    
                    # Store found links for this page
                    page_links = []
                    for link in sorted(links):
                        page_links.append(link)
                        if link not in self.visited:
                            queue.append(link)
                    
                    # Update session with new page data
                    crawl_sessions[self.session_id]["pages"].append({
                        "url": url,
                        "links": page_links,
                        "timestamp": time.time()
                    })

            except Exception as e:
                print(f"Error fetching {url}: {e}")

def run_crawler_async(base_url, session_id):
    """Run crawler in a separate thread with asyncio"""
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        crawler = WebCrawler(base_url, session_id)
        loop.run_until_complete(crawler.start())
    
    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start_crawl', methods=['POST'])
def start_crawl():
    data = request.get_json()
    base_url = data.get('url')
    
    if not base_url:
        return jsonify({"error": "URL is required"}), 400
    
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    
    # Initialize session data
    crawl_sessions[session_id] = {
        "base_url": base_url,
        "status": "initializing",
        "pages_crawled": 0,
        "elapsed_time": 0,
        "current_url": "",
        "total_found": 0,
        "pages": [],
        "start_time": time.time()
    }
    
    # Start crawling in background
    run_crawler_async(base_url, session_id)
    
    return jsonify({"session_id": session_id})

@app.route('/api/crawl_status/<session_id>')
def get_crawl_status(session_id):
    if session_id not in crawl_sessions:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify(crawl_sessions[session_id])

@app.route('/api/stop_crawl/<session_id>', methods=['POST'])
def stop_crawl(session_id):
    if session_id not in crawl_sessions:
        return jsonify({"error": "Session not found"}), 404
    
    crawl_sessions[session_id]["status"] = "stopped"
    return jsonify({"message": "Crawl stopped"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)