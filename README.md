# Website Cloner

A production-ready desktop GUI application for cloning any website into a local static copy. Downloads HTML, CSS, JavaScript, images, fonts, videos, and rewrites all URLs for offline browsing.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey" alt="Platform">
</p>

---

## How It Works

The cloner runs a four-phase pipeline:

| Phase | Description |
|---|---|
| **1. Crawl** | Fetches the target URL. If multi-page crawling is enabled (depth > 1), it discovers and queues all same-domain `<a href>` links up to the configured depth. |
| **2. Collect** | Parses every page with BeautifulSoup and extracts asset references from `<img>`, `<link>`, `<script>`, `<video>`, `<audio>`, `<source>`, `<iframe>`, `<embed>`, `<object>`, `srcset` attributes, and CSS `url()`/`@import` declarations. |
| **3. Download** | All discovered assets are downloaded in parallel using a thread pool (configurable 1-20 workers). Progress, speed, and per-file status are streamed to the GUI in real time. |
| **4. Rewrite** | Every asset URL in the HTML is replaced with a local relative path. CSS files have their `url()` references rewritten. Optional: inline CSS/JS directly into the HTML, or minify the output. |

```
GET https://example.com
  |
  +-> Parse HTML, find <img>, <link>, <script>...
  +-> Parse CSS, find url() references, @import
  +-> Discover same-domain links (if depth > 1)
  |
  Parallel download (8 threads default)
  |  /assets/img/hero.png
  |  /assets/css/style.css
  |  /assets/js/app.js
  |  /assets/fonts/Inter.woff2
  |  ...
  |
  Rewrite all paths -> relative
  Save index.html + manifest
```

### Output Structure

```
cloned_site/
  index.html                  # Main page (URLs rewritten to local)
  page/subpage.html           # Additional crawled pages
  cloner_manifest.json        # Metadata: source URL, timestamps, asset map, errors
  assets/
    img/                      # Downloaded images
    css/                      # Stylesheets (url() references rewritten)
    js/                       # JavaScript files
    fonts/                    # Web fonts (woff2, ttf, etc.)
    videos/                   # Video files
    audio/                    # Audio files
    data/                     # JSON, XML, etc.
    other/                    # Everything else
```

---

## Quick Start

### Prerequisites

- **Python 3.9+**
- **pip**

### 1. Clone

```bash
git clone https://github.com/JamesCowx/website-cloner.git
cd website-cloner
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Launch

```bash
python cloner.py
```

Or on Windows, double-click **`run.bat`**.

### 4. Use

1. Paste a URL (or press `Ctrl+V`)
2. Pick an output directory with **...**
3. Toggle options as needed
4. Press **CLONE** (or hit `Enter`)
5. Watch progress in real time
6. Click **Open Site** to view the result

---

## Command-Line Mode

Run headlessly from a terminal or script:

```bash
python cloner.py https://example.com --headless -o ./mysite -d 2
```

| Flag | Description |
|---|---|
| `--headless`, `-h` | Run without GUI |
| `--output`, `-o <dir>` | Output directory (default: `./cloned_site`) |
| `--depth`, `-d <n>` | Crawl depth for linked pages (default: 1) |

---

## Options

| Option | Default | Description |
|---|---|---|
| Images | On | Download `<img>` assets (png, jpg, svg, webp, etc.) |
| CSS | On | Download stylesheets |
| JavaScript | On | Download `<script src>` files |
| Fonts | On | Download web fonts (woff2, ttf, otf) |
| Same domain | On | Only download assets and links from the target domain |
| Strip params | On | Remove query strings from asset URLs |
| Rewrite CSS | On | Rewrite `url()` references in CSS to local paths |
| Minify HTML | Off | Strip extra whitespace from output |
| Inline CSS | Off | Embed CSS directly into HTML `<style>` tags |
| Inline JS | Off | Embed JS directly into HTML `<script>` tags |

### Advanced

| Setting | Default | Description |
|---|---|---|
| Depth | 1 | How many levels of linked pages to crawl |
| Workers | 8 | Number of parallel download threads |
| Delay (s) | 0.1 | Wait between requests to avoid rate limiting |
| Timeout (s) | 30 | HTTP request timeout per asset |
| User-Agent | (Chrome) | Custom UA string (blank = default) |
| Proxy | (none) | HTTP/HTTPS proxy address |

---

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `Enter` | Start clone |
| `Escape` | Cancel clone |
| `Ctrl+V` | Paste URL from clipboard |
| `Ctrl+L` | Focus URL field |

---

## Features

- Full dark-themed GUI with real-time stats and progress
- Multi-threaded asset downloading (configurable concurrency)
- Multi-page crawling with depth control
- URL rewriting for offline browsing
- CSS `url()` and `@import` parsing and rewriting
- Export cloned site as ZIP
- Session persistence — remembers settings, window size, and recent URLs
- Validate URLs before cloning
- Rate limiting with configurable request delay
- Proxy support
- Custom User-Agent
- Asset tree with per-file status (OK / FAIL)
- Color-coded console log
- Manifest file with full metadata and error tracking

---

## Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP client with session support |
| `beautifulsoup4` | HTML parser |
| `tkinter` | GUI toolkit (bundled with Python) |

---

## License

MIT
