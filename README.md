# Web Crawler Pro 🚀

A modern, interactive web crawler with a beautiful real-time interface. Transform your command-line crawler into a sleek web application with live progress tracking, animated statistics, and responsive design.

## ✨ Features

- **🎨 Modern UI**: Beautiful gradient design with glassmorphism effects
- **⚡ Real-time Updates**: Live progress tracking and statistics
- **📊 Interactive Dashboard**: Visual stats showing pages crawled, elapsed time, and URLs found
- **📱 Responsive Design**: Works perfectly on desktop and mobile devices  
- **🔄 Async Crawling**: Fast, concurrent web crawling with aiohttp
- **🎯 Smart Filtering**: Only crawls same-domain links with URL normalization
- **🌐 Flexible URL Input**: Automatically completes URLs - works with `example.com`, `www.example.com`, or `https://example.com`
- **⏹️ Stop/Start Control**: Full control over crawling sessions
- **📝 Detailed Logging**: See each page being crawled in real-time
- **✅ URL Validation**: Intelligent URL validation and error handling

## 🏗️ Project Structure

```
web-crawler-pro/
├── app.py                    # Flask web server
├── run_web.py               # Startup script
├── main.py                  # Original CLI version
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── crawler/                # Crawler module
│   ├── __init__.py
│   ├── crawler.py          # Main crawler class
│   └── utils.py            # Utility functions
├── test/                   # Test files
│   ├── test_crawler_async.py
│   ├── test_crawler_parse_links.py
│   ├── test_extra_coverage.py
│   └── test_utils.py
└── templates/              # HTML templates
    └── index.html          # Web interface
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Web Interface

**Option A: Using the startup script (Recommended)**
```bash
python run_web.py
```

**Option B: Direct Flask run**
```bash
python app.py
```

### 3. Open Your Browser

The application will automatically open at `http://localhost:5000`

### 4. Start Crawling

1. Enter a website URL in any of these formats:
   - `sapo.pt` (will become `https://www.sapo.pt`)
   - `www.sapo.pt` (will become `https://www.sapo.pt`) 
   - `https://www.sapo.pt` (used as-is)
2. Click "Start Crawling"
3. Watch the real-time progress!

## 🌐 URL Format Support

The crawler intelligently handles various URL formats:

| Input Format | Automatically Becomes | Notes |
|---|---|---|
| `sapo.pt` | `https://www.sapo.pt` | Adds protocol and www |
| `www.sapo.pt` | `https://www.sapo.pt` | Adds protocol only |
| `https://sapo.pt` | `https://sapo.pt` | Used as provided |
| `http://www.sapo.pt` | `http://www.sapo.pt` | Respects HTTP if specified |

### Invalid URL Examples
- Empty strings
- Plain text without domains  
- Malformed URLs

The system will show clear error messages for invalid inputs.

## 🔧