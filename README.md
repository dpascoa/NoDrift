# NoDrift — Fast, Domain‑Scoped Python Web Crawler

<img width="986" height="666" alt="image" src="https://github.com/user-attachments/assets/1f655482-f18b-419a-99d6-21dd8afb8df5" />


> A command‑line and (optional) web UI crawler that prints each page it visits and all links it finds, while **staying strictly within the starting domain (no subdomains)**. Built with asyncio + aiohttp and BeautifulSoup for speed and simplicity.

---

## ✨ Features at a glance

- **Domain‑scoped crawl** — only the exact domain of the base URL; external domains & subdomains are ignored.
- **Asynchronous core** — concurrency with `asyncio` + `aiohttp` for efficient, non‑blocking I/O.
- **Robust parsing** — link extraction via BeautifulSoup; relative → absolute URL normalization.
- **BFS traversal** — queue (deque) based breadth‑first crawl; visited set for dedupe.
- **CLI first** — simple `python main.py <base_url>` entrypoint.
- **Optional Web UI** — Flask app to start/stop a crawl and download logs.
- **Structured logging** — per‑session log files under `logs/`, with progress & summary.

---

## 🧰 Requirements

- Python **3.10+** (project tested with 3.11/3.12)
- pip / venv (recommended)

Project dependencies are listed in `requirements.txt`:
```
aiohttp
beautifulsoup4
flask
flask-cors
lxml
pytest
```

> Optional (for coverage reports): install `pytest-cov`.

---

## 🚀 Quick start (CLI)

1) **Create & activate a virtual environment**
```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

2) **Install dependencies**
```bash
pip install -r requirements.txt
```

3) **Run the crawler**
```bash
python main.py <base_url>
# examples:
python main.py zego.com
python main.py www.zego.com
python main.py https://www.zego.com
```

The CLI accepts one **positional** argument:
- `base_url` — the starting URL or hostname. The app auto‑completes bare hostnames (e.g., `zego.com`) to a valid URL.

**What you’ll see:** for each crawled page, the program prints the page URL and the list of links discovered on that page (filtered to the same domain).

**Logs:** when logging is enabled (default), session logs are written to `logs/` with a timestamped filename derived from the domain.

---

## 🌐 Optional Web UI

Start the Flask app:
```bash
python run_web.py
```
In 3 seconds, the page will automatically open in your browser.

### API endpoints (used by the UI)
- `POST /api/start_crawl` — body includes the `base_url`; starts a new crawl session.
- `GET /api/status/<session_id>` — get live progress for a session.
- `POST /api/stop/<session_id>` — stop a running session.
- `GET /api/download_log/<session_id>` — download the session log file.

> The root route `/` serves the simple UI (templates under `templates/`).

---

## 🧪 Testing

Run all tests:
```bash
pytest -q
```

Optional coverage (if you install `pytest-cov`):
```bash
pip install pytest-cov
pytest --cov=crawler --cov=main --cov=app --cov=run_web -q
```

> At submission time, the author reported **34 tests passing** and coverage similar to:
>
> | Module                | Stmts | Miss | Cover |
> |-----------------------|------:|-----:|------:|
> | app.py (Web UI)       |   161 |   93 |  42%  |
> | crawler/__init__.py   |     5 |    0 | 100%  |
> | crawler/crawler.py    |   105 |   11 |  90%  |
> | crawler/logger.py     |    74 |    6 |  92%  |
> | crawler/utils.py      |    52 |   16 |  69%  |
> | main.py               |    21 |    1 |  95%  |
> | run_web.py (Web UI)   |    43 |   34 |  21%  |

(These numbers may vary on your machine; the focus of the exercise is the crawler core.)

---

## 🏗️ Project structure

```
NoDrift/
├─ main.py                # CLI entrypoint
├─ run_web.py             # Flask server entry
├─ app.py                 # Web UI + REST API
├─ crawler/
│  ├─ __init__.py
│  ├─ crawler.py          # Crawler (async core, BFS, concurrency, logging hooks)
│  ├─ utils.py            # URL utils: normalization, same-domain checks, etc.
│  └─ logger.py           # Session logger (files under logs/)
├─ templates/             
│  ├─ index.html          # HTML for the Web UI
├─ logs/                  # Session logs (created at runtime)
└─ tests/                 # Pytest suite
```

---

## ⚙️ How it works (core design)

### Responsibilities & separation of concerns
1. **URL utilities (`crawler/utils.py`)**  
   - Normalize URLs (complete schemeless hostnames, resolve relatives)
   - Determine whether a link belongs to the **same domain (strict, no subdomains)**
2. **Crawler (`crawler/crawler.py`)**  
   - Asynchronous fetch with `aiohttp`
   - Parse links with BeautifulSoup
   - Maintain `deque` queue (BFS) and `set` of visited URLs
   - Concurrency control (`max_concurrent`), graceful error handling
   - Structured logging of progress and summaries
3. **CLI (`main.py`)**  
   - Single positional `base_url` argument
   - URL verification before crawl; prints each page + links

### Why asyncio + aiohttp?
- **Concurrency for speed.** Non‑blocking I/O lets us fetch multiple pages concurrently, far faster than a purely synchronous `requests` loop for medium/large crawls.  
- **Simplicity over threads.** Avoids Python’s GIL issues for I/O workloads without thread management overhead.  
- **Trade‑off:** async adds complexity (event loop, coroutines), but it **scales cleanly** and uses resources efficiently — aligning with “fast without wasting compute.”

### Data structures
- **`set`** for O(1) visited‑URL membership checks.
- **`collections.deque`** for BFS: append to the right, pop from the left — both O(1).

### Domain filtering
- The crawler compares the `netloc` (from `urllib.parse`) of candidate links to the starting URL **exactly**; subdomains are ignored by design per the brief.

### Error handling & resilience
- Network and parsing errors are caught and logged; the crawl **skips & continues** rather than failing the whole run.
- Progress logs include elapsed time, total pages crawled, and URLs discovered.

---

## 🗒️ Notes from the author (refined & structured)

### Initial approach (Selenium)
- Started with a **Selenium** proof‑of‑concept to collect links and drive a browser.
- It helped clarify the problem but was **not optimal for speed or headless CLI use**.  
  _Trade‑off:_ browser realism vs. performance & simplicity. (Selenium version is not included here; it was a stepping stone.)

### Moving to a CLI‑first async design
- Implemented a straightforward **synchronous** version first for correctness, then upgraded to an **async** crawler using `asyncio + aiohttp` for concurrency.
- Adopted **BFS** with a `deque` and a **visited** set to avoid repeats.
- Chose **BeautifulSoup** for readability & reliability (considered `lxml` for speed but kept dependencies lean).

### URL normalization & acceptance
- The CLI accepts `zego.com`, `www.zego.com`, or `https://www.zego.com` — utilities normalize these to a canonical absolute URL before crawling.

### Logging & progress
- Introduced a structured logger that writes to `logs/`, including:
  - session header (target URL, start time, log filename),
  - per‑page status & links found,
  - **elapsed time** updates and a final summary (pages crawled, total links, errors).
- Log filenames are based on the domain and timestamp for easy retrieval.

### Testing approach
- **Layered tests**:
  - Unit tests for pure utilities (`normalize_url`, domain checks, absolute resolution).
  - Component tests for link parsing with controlled HTML.
  - Async tests for crawler start/fetch logic using **mocks/fakes** to avoid real HTTP.
- Learned and used **pytest monkeypatch** to safely override environment/attributes within test scopes — automatically undone after each test.
- After adding Web UI & logging features, **additional tests** were created (some with assistance from AI tools) to cover:
  - Logger edge cases and file errors
  - Flask API endpoint behavior (`app.py`)
  - Stopping & resuming sessions
  - Downloading logs via API
- **Results (at the time of writing):** 34 tests passing; core crawler coverage is high, UI coverage is intentionally lower due to time constraints.

### Tools & workflow
- **IDE:** Visual Studio Code  
  Extensions: Python; ran app & tests via integrated terminal.
- **Primary libraries:** `aiohttp`, `beautifulsoup4`, `lxml` (parser), `pytest`, `flask`, `flask-cors`.
- **Interactive AI usage:**  
  Used ChatGPT, Grok (xAI), Gemini and Claude to brainstorm strategies, discuss trade‑offs (sync vs. async, malformed HTML handling), and suggest missing tests.  
  Additionally used GitHub Copilot selectively near the end to scaffold a few **test cases** for the new UI/logging code. All AI suggestions were **reviewed, adapted, and validated** via tests before inclusion.

### If given more time
- **Performance:** add a semaphore to cap concurrency per host; implement polite crawling (`robots.txt`, delay/backoff); streaming parse for large pages.
- **Extensibility:** pluggable outputs (JSON/CSV/DB), configuration file & CLI flags (max depth, parallelism), multi‑domain crawl controller & dashboard.
- **Robustness:** improved encoding detection; retries with exponential backoff & jitter.
- **CI/CD:** GitHub Actions for linting, tests, and coverage badges; split dev dependencies (`requirements-dev.txt`).

---

## 🔧 Configuration & flags

Current CLI accepts only the `base_url`. Internal defaults include:
- `max_concurrent=10` — maximum concurrent fetches (adjustable in code or via future CLI flag).
- Logging **enabled** by default — log files go to `logs/` (auto‑created).

> Future work: promote these to CLI flags or a config file (e.g. depth limits, parallelism, user‑agent, politeness).

---

## 🧭 Usage examples

```bash
# Basic crawl with hostname
python main.py zego.com

# Full URL (https)
python main.py https://www.zego.com

# Local development server via Web UI
python run_web.py
(Opening in your browser in 3 seconds...)
```

---

## 🧹 Housekeeping

- Create the `logs/` directory if it does not exist (the app attempts to create it automatically).
- The crawler **does not** fetch subdomains — `blog.example.com` is ignored if you start from `example.com`.
- Avoid pointing at sites you do not control during testing; be polite with concurrency to prevent undue load.
- Consider using https://quotes.toscrape.com/ or https://books.toscrape.com/.

---

## 🙌 Credits

Authored for a coding exercise. The “NoDrift” name refers to staying within domain — no drifting to subdomains or external links.
