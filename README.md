<p align="center">
  <img src="https://img.shields.io/github/stars/JamesCowx/website-cloner?style=for-the-badge&color=6366f1" alt="Stars">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white&color=3776AB" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge&color=22c55e" alt="License">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge" alt="Platform">
</p>

<br>

<h1 align="center">
  <code>[  Website Cloner  ]</code>
</h1>

<p align="center">
  <b>Clone any website into a local static copy — with a full GUI.</b><br>
  <sub>Downloads HTML, CSS, JS, images, fonts, and more. Rewrites all paths for offline browsing.</sub>
</p>

<br>

---

##   Pipeline

```
  USER INPUT                    ENGINE                          OUTPUT
 ─────────────────────────────────────────────────────────────────────────
                                                                   
  https://example.com            . Crawl page                     
       │                        │    Fetch HTML                    cloned_site/
       ▼                        │    Discover links (depth)       ├── index.html
  ┌─────────┐                   │                              ├── page/
  │  CLONE  │ ──────────────►   │    . Collect assets            │   └── about.html
  └─────────┘                   │    <img>  <script>              ├── assets/
                                │    <link>  <video>             │   ├── img/
                                │    url()  @import              │   ├── css/
                                │                              │   ├── js/
                                │    . Download (parallel)       │   ├── fonts/
                                │    ThreadPoolExecutor           │   └── videos/
                                │    8 workers default           │
                                │                              └── cloner_manifest.json
                                │    . Rewrite
                                │    Replace all URLs →
                                │    local relative paths
                                │    Fix CSS url() refs
```

<br>

##   Quick Start

```bash
# 1. Clone
git clone https://github.com/JamesCowx/website-cloner.git
cd website-cloner

# 2. Install
pip install -r requirements.txt

# 3. Launch
python cloner.py          # GUI mode
#  OR
python cloner.py https://example.com --headless -o ./mysite   # CLI mode
```

### No Python? Download the .exe

Grab the standalone executable from [**Releases**](https://github.com/JamesCowx/website-cloner/releases) — no Python required.

<table>
<tr><td><b>Windows (.exe)</b></td><td>Download <code>WebsiteCloner.exe</code>, double-click to run</td></tr>
<tr><td><b>Windows (source)</b></td><td>Double-click <code>run.bat</code></td></tr>
<tr><td><b>macOS / Linux</b></td><td><code>python cloner.py</code></td></tr>
</table>

<br>

## ⌨️  Keyboard Shortcuts

| Key | Action |
|:---:|:---|
| `Enter` | Start clone |
| `Escape` | Cancel clone |
| `Ctrl + V` | Paste URL from clipboard |
| `Ctrl + L` | Focus URL field |

<br>

## ⚙️  Options

### Content

| Option | Default | Description |
|:---|:---:|:---|
| **Images** | On | Downloads `png`, `jpg`, `svg`, `webp`, `ico`, `gif`, `bmp` |
| **CSS** | On | Downloads stylesheets & parses `url()` / `@import` references |
| **JavaScript** | On | Downloads `<script src>` files |
| **Fonts** | On | Downloads `woff2`, `ttf`, `otf`, `eot` |

### Processing

| Option | Default | Description |
|:---|:---:|:---|
| **Same domain** | On | Only download assets from the target domain |
| **Strip params** | On | Remove `?v=1.2.3` query strings from asset URLs |
| **Rewrite CSS** | On | Rewrite `url()` references in CSS to local paths |
| **Minify HTML** | Off | Strip extra whitespace from output |
| **Inline CSS** | Off | Embed stylesheets directly into `<style>` tags |
| **Inline JS** | Off | Embed scripts directly into `<script>` tags |

### Advanced

| Setting | Default | Range | Description |
|:---|:---:|:---:|:---|
| **Depth** | 1 | 1-10 | How many levels of linked pages to crawl |
| **Workers** | 8 | 1-20 | Concurrent download threads |
| **Delay** | 0.1 s | 0-5 s | Wait between requests to avoid rate limiting |
| **Timeout** | 30 s | 5-120 s | Per-request timeout |
| **User-Agent** | Chrome 125 | any | Custom UA string |
| **Proxy** | none | `host:port` | Route traffic through HTTP proxy |

<br>

##   Features

<table>
<tr>
  <td width="50%">

###   UI
- Dark-themed polished GUI
- Real-time progress bar with animation
- Live stats dashboard (pages, assets, size, speed)
- Asset tree with per-file status (OK / FAIL)
- Color-coded console log
- Collapsible advanced settings panel
- Clickable recent-URL history

  </td>
  <td width="50%">

###   Engine
- Multi-threaded parallel downloads
- Depth-controlled multi-page crawling
- css `url()` & `@import` reference parsing
- Full URL → local path rewriting
- Rate limiting with configurable delay
- Proxy support & custom User-Agent
- Session persistence (remembers all settings)

  </td>
</tr>
<tr>
  <td width="50%">

###   I/O
- Export cloned site as ZIP
- `cloner_manifest.json` with full metadata
- CLI headless mode for scripting
- Config saved to `%APPDATA%\WebsiteCloner\`
- Input validation (URL format check)

  </td>
  <td width="50%">

###   Output
```
cloned_site/
  index.html
  page/subpage.html
  cloner_manifest.json
  assets/
    img/      # Downloaded images
    css/      # Stylesheets (url paths rewritten)
    js/       # JavaScript files
    fonts/    # Web fonts
    videos/   # Video files
    audio/    # Audio files
    other/    # Everything else
```

  </td>
</tr>
</table>

<br>

##   Command-Line Mode

```bash
# Basic: clone a single page
python cloner.py https://example.com --headless

# With output directory and crawl depth
python cloner.py https://example.com --headless -o ./myclone -d 3

# All flags
python cloner.py <url> [--headless] [--output <dir>] [--depth <n>]
```

| Flag | Alias | Description |
|:---|:---|:---|
| `--headless` | `-h` | Run without opening the GUI |
| `--output <dir>` | `-o` | Output directory path |
| `--depth <n>` | `-d` | Crawl depth for linked pages |

<br>

##   Architecture

```
cloner.py
  │
  ├── WebsiteCloner           # Cloning engine
  │   ├── clone()             #   Main entry point
  │   ├── _collect()          #   Asset discovery (HTML + CSS)
  │   ├── _download_all()     #   ThreadPoolExecutor fan-out
  │   ├── _write_pages()      #   URL rewriting + CSS fixing
  │   └── _manifest()         #   Metadata export
  │
  ├── RoundedFrame            #   Canvas-based card with shadow
  ├── ProgressBar             #   Animated progress with interpolation
  ├── Console                 #   Color-coded log (info/ok/err/warn)
  ├── AssetTree               #   Live treeview of downloaded files
  │
  └── ClonerApp               #   Tkinter GUI
      ├── _build()            #     Layout construction
      ├── _start() / _done()  #     Clone lifecycle
      ├── _poll()             #     Thread-safe queue → UI
      ├── _on_close()         #     Config persistence
      └── _bind_keys()        #     Keyboard shortcuts
```

<br>

##   Dependencies

| Package | Version | Purpose |
|:---|:---|:---|
| `requests` | >=2.31 | HTTP client with session + streaming |
| `beautifulsoup4` | >=4.12 | HTML parser |
| `tkinter` | bundled | GUI toolkit (included with Python) |

```bash
pip install -r requirements.txt
```

<br>

##   License

MIT © 2026

---

<p align="center">
  <sub>Built with Python + Tkinter • No external GUI frameworks • No API keys needed</sub>
</p>
