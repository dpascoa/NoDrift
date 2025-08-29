#!/usr/bin/env python3
"""
Web Crawler Pro - Startup Script
Run this file to start the web interface for the crawler.
"""

import os
import sys
import webbrowser
import time
from threading import Timer
from app import app


def open_browser():
    """Open the web browser after a short delay to access the local server."""
    webbrowser.open('http://localhost:5000')


def main():
    """Main entry point to start the Flask server and open the browser."""
    print("🚀 Starting Web Crawler Pro...")
    print("=" * 50)

    # Check if required modules are available
    try:
        import flask
        import aiohttp
        from bs4 import BeautifulSoup
        print("✅ All required modules found")
    except ImportError as e:
        print(f"❌ Missing required module: {e}")
        print("Please install requirements with: pip install -r requirements.txt")
        sys.exit(1)

    # Check if crawler module exists
    if not os.path.exists('crawler'):
        print("❌ Crawler module not found")
        print("Please ensure the 'crawler' folder exists with crawler.py and utils.py")
        sys.exit(1)

    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
        print("📁 Created templates directory")

    print("🌐 Starting Flask server...")
    print("📱 Web interface will be available at: http://localhost:5000")
    print("🔄 Opening browser in 3 seconds...")

    # Open browser after 3 seconds
    Timer(3.0, open_browser).start()

    # Import and run the Flask app
    try:
        from app import app
        app.run(debug=True, port=5000, use_reloader=False)
    except ImportError:
        print("❌ Could not import app.py")
        print("Please ensure app.py exists in the current directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()