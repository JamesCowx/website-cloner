<p align="center">
  <img src="https://img.shields.io/github/stars/JamesCowx/website-cloner?style=for-the-badge&logo=github&color=6366f1&logoColor=white" alt="Stars">
  <img src="https://img.shields.io/github/license/JamesCowx/website-cloner?style=for-the-badge&color=22c55e" alt="License">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Windows-10%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey?style=for-the-badge" alt="Cross-platform">
</p>

<br>

<p align="center">
  <img src="https://raw.githubusercontent.com/JamesCowx/website-cloner/master/docs/header.svg" width="100%" alt="Website Cloner" onerror="this.style.display='none'">
</p>

<pre align="center">
   ██╗    ██╗███████╗██████╗ ███████╗██╗████████╗███████╗     ██████╗██╗      ██████╗ ███╗   ██╗███████╗██████╗
   ██║    ██║██╔════╝██╔══██╗██╔════╝██║╚══██╔══╝██╔════╝    ██╔════╝██║     ██╔═══██╗████╗  ██║██╔════╝██╔══██╗
   ██║ █╗ ██║█████╗  ██████╔╝███████╗██║   ██║   █████╗      ██║     ██║     ██║   ██║██╔██╗ ██║█████╗  ██████╔╝
   ██║███╗██║██╔══╝  ██╔══██╗╚════██║██║   ██║   ██╔══╝      ██║     ██║     ██║   ██║██║╚██╗██║██╔══╝  ██╔══██╗
   ╚███╔███╔╝███████╗██████╔╝███████║██║   ██║   ███████╗    ╚██████╗███████╗╚██████╔╝██║ ╚████║███████╗██║  ██║
    ╚══╝╚══╝ ╚══════╝╚═════╝ ╚══════╝╚═╝   ╚═╝   ╚══════╝     ╚═════╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
</pre>

<p align="center">
  <b>Clone any website into a local static copy &mdash; with a beautiful full GUI.</b><br>
  <sub>Zero configuration. No API keys. No external services. Just paste a URL and press Clone.</sub>
</p>

<br>

<p align="center">
  <img src="https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/anonymous/raw/placeholder.json&style=flat-square" alt="" style="display:none">
  <a href="https://jamescowx.github.io/website-cloner/"><img src="https://img.shields.io/badge/Website-Landing_Page-6366f1?style=flat-square" alt="Website"></a>
  <a href="https://github.com/JamesCowx/website-cloner/releases/latest"><img src="https://img.shields.io/github/v/release/JamesCowx/website-cloner?color=22c55e&include_prereleases&style=flat-square" alt="Release"></a>
  <a href="https://github.com/JamesCowx/website-cloner/releases/latest/download/WebsiteCloner.exe"><img src="https://img.shields.io/badge/Download-.exe-4f46e5?style=flat-square&logo=windows&logoColor=white" alt="Download"></a>
  <img src="https://img.shields.io/github/repo-size/JamesCowx/website-cloner?color=f59e0b&style=flat-square" alt="Size">
</p>

<br>

---

##   Table of Contents

- [  Quick Start](#-quick-start)
- [  How It Works](#-how-it-works)
- [  Features](#-features)
- [  Options Reference](#-options-reference)
- [  Command-Line Mode](#-command-line-mode)
- [  Use Cases](#-use-cases)
- [  Keyboard Shortcuts](#-keyboard-shortcuts)
- [  Output Structure](#-output-structure)
- [  Architecture](#-architecture)
- [  FAQ](#-faq)
- [  Contributing](#-contributing)

<br>

---

##   Quick Start

<table>
<tr>
<td width="65%">

###   Option A &mdash; Download the .exe (Windows)

No Python required. Download the standalone executable and double-click.

<p align="center">
  <a href="https://github.com/JamesCowx/website-cloner/releases/latest/download/WebsiteCloner.exe">
    <img src="https://img.shields.io/badge/Download-WebsiteCloner.exe-6366f1?style=for-the-badge&logo=windows&logoColor=white" alt="Download .exe" width="320">
  </a>
</p>

> **File:** `WebsiteCloner.exe` &middot; **Size:** 12.8 MB &middot; **Requires:** Windows 10 or 11

</td>
<td width="35%">

###   Option B &mdash; Run from source

```bash
git clone https://github.com/JamesCowx/website-cloner.git
cd website-cloner
pip install -r requirements.txt
python cloner.py
```

> **Requires:** Python 3.9+ &middot; Works on Windows, macOS, and Linux

</td>
</tr>
</table>

<br>

---

##   How It Works

The cloner executes a **four-phase pipeline** that transforms a live URL into a fully-local static website.

<pre>
   <b>PHASE 1: CRAWL</b>                   <b>PHASE 2: COLLECT</b>                  <b>PHASE 3: DOWNLOAD</b>                 <b>PHASE 4: REWRITE</b>

   Fetch target URL                   Parse HTML + CSS                   Fan-out 8 threads                   Replace all URLs with
   Follow same-domain links           Extract every &lt;img&gt;,              Download in parallel               local relative paths
   Configured depth (1-10)            &lt;script&gt;, &lt;link&gt;, &lt;video&gt;,       Real-time speed + progress         Fix CSS url() refs
                                      url(), @import rules               Track per-file status              Optional: inline/minify

   <span style="color:#6366f1">  Input URL</span>                         <span style="color:#f59e0b">  250+ Assets Found</span>               <span style="color:#22c55e">  4.8 MB in 3.2s</span>                 <span style="color:#06b6d4">  100% Offline-Ready</span>
</pre>

<br>

### Pipeline Diagram

```
   https://example.com
        │
        ▼
 ┌──────────────────────────────────────────────────────────────┐
 │  CRAWL                                                       │
 │  ─────                                                       │
 │  GET /        200 OK    [depth 0]                             │
 │  GET /about   200 OK    [depth 1]  ── if depth > 1           │
 │  GET /pricing 200 OK    [depth 1]  ── if depth > 1           │
 └──────────────┬───────────────────────────────────────────────┘
                │
                ▼
 ┌──────────────────────────────────────────────────────────────┐
 │  COLLECT                                                     │
 │  ───────                                                     │
 │  <img src="hero.png">           →   /assets/img/hero.png     │
 │  <link href="style.css">        →   /assets/css/style.css    │
 │  <script src="app.js">          →   /assets/js/app.js        │
 │  url("../fonts/Inter.woff2")    →   /assets/fonts/Inter...   │
 │  @import "theme.css"            →   /assets/css/theme.css    │
 └──────────────┬───────────────────────────────────────────────┘
                │
                ▼
 ┌──────────────────────────────────────────────────────────────┐
 │  DOWNLOAD  (ThreadPoolExecutor, 8 workers)                    │
 │  ────────                                                    │
 │  [ 1] ████████████ hero.png         320 KB   ✓                │
 │  [ 2] ████████████ style.css         84 KB   ✓                │
 │  [ 3] ████████████ app.js           156 KB   ✓                │
 │  [ 4] ████████████ Inter.woff2       48 KB   ✓                │
 │  [ 5] ████████████ logo.svg           2 KB   ✓                │
 │  ...                                                          │
 │  [47] ████████████ footer-bg.jpg    120 KB   ✓                │
 └──────────────┬───────────────────────────────────────────────┘
                │
                ▼
 ┌──────────────────────────────────────────────────────────────┐
 │  REWRITE                                                     │
 │  ───────                                                     │
 │  hero.png      →   assets/img/hero.png                       │
 │  style.css     →   assets/css/style.css                      │
 │  app.js        →   assets/js/app.js                          │
 │  Inter.woff2   →   assets/fonts/Inter.woff2                  │
 │                                                               │
 │  CSS url()     →   Rewrite to local paths                    │
 │  @import       →   Rewrite to local paths                    │
 └──────────────┬───────────────────────────────────────────────┘
                │
                ▼
       ┌───────────────────┐
       │  cloned_site/     │
       │   index.html      │  ←──  Fully functional, offline
       │   about.html      │  ←──  All images load locally
       │   manifest.json   │  ←──  Complete metadata + asset log
       │   assets/         │
       │     img/          │
       │     css/          │
       │     js/           │
       │     fonts/        │
       │     videos/       │
       └───────────────────┘
```

<br>

---

##   Features

<table>
<tr>
<th width="50%">  GUI & Experience</th>
<th width="50%">  Engine & Performance</th>
</tr>
<tr>
<td>

| | |
|---|---|
| &#x1F3A8; | **Polished dark UI** with custom Canvas widgets, rounded cards, and animated progress |
| &#x1F4CA; | **Live stats dashboard** &mdash; pages, assets, download size, and transfer speed |
| &#x1F4C3; | **Asset tree view** with per-file OK/FAIL status coloring |
| &#x1F4AC; | **Color-coded console log** (blue=info, green=success, red=error, orange=warning) |
| &#x2328; | **Keyboard shortcuts** &mdash; Enter to start, Escape to cancel, Ctrl+V to paste |
| &#x1F4BE; | **Session persistence** &mdash; remembers settings, window position, and recent URLs |
| &#x1F4CB; | **Clickable history** &mdash; re-clone any of your last 5 URLs with one click |

</td>
<td>

| | |
|---|---|
| &#x26A1; | **Parallel downloads** &mdash; ThreadPoolExecutor with 1-20 configurable workers |
| &#x1F310; | **Multi-page crawl** &mdash; follows same-domain links up to configurable depth |
| &#x1F4DD; | **CSS parsing** &mdash; discovers assets in `url()` and `@import` rules |
| &#x1F504; | **URL rewriting** &mdash; all references converted to local relative paths |
| &#x1F6E1; | **Rate limiting** &mdash; configurable delay between requests to avoid server bans |
| &#x1F512; | **Proxy support** &mdash; route all traffic through your HTTP/HTTPS proxy |
| &#x1F4E6; | **ZIP export** &mdash; package the cloned site into a single archive |

</td>
</tr>
</table>

<br>

---

##   Options Reference

### Content Filters

| Option | Default | What It Controls |
|:---|:---:|:---|
| **Images** | `ON` | Downloads `png`, `jpg`, `jpeg`, `gif`, `svg`, `webp`, `ico`, `bmp` |
| **CSS** | `ON` | Downloads stylesheets, parses nested `url()` and `@import` references |
| **JavaScript** | `ON` | Downloads external `<script src="...">` files (`js`, `mjs`, `ts`) |
| **Fonts** | `ON` | Downloads web fonts (`woff`, `woff2`, `ttf`, `eot`, `otf`) |

### Processing Options

| Option | Default | What It Does |
|:---|:---:|:---|
| **Same domain** | `ON` | Only download assets and follow links from the target domain |
| **Strip params** | `ON` | Remove `?v=1.2.3` query strings from asset URLs for cleaner filenames |
| **Rewrite CSS** | `ON` | Replace CSS `url()` folder references with local paths so styles work offline |
| **Minify HTML** | `OFF` | Strip blank lines and collapse whitespace in output |
| **Inline CSS** | `OFF` | Embed external stylesheets into `<style>` tags (fewer files, larger HTML) |
| **Inline JS** | `OFF` | Embed external scripts into `<script>` tags |

### Advanced

| Setting | Default | Range | Purpose |
|:---|:---:|:---:|:---|
| **Depth** | `1` | 1-10 | Levels of linked pages to crawl |
| **Workers** | `8` | 1-20 | Concurrent download threads |
| **Delay** | `0.1s` | 0-5s | Cooldown between requests (rate limiting) |
| **Timeout** | `30s` | 5-120s | Maximum wait per HTTP request |
| **User-Agent** | `Chrome 125` | Any string | Custom browser identifier |
| **Proxy** | _(none)_ | `host:port` | Route traffic through proxy server |

<br>

---

##   Command-Line Mode

The full engine works without the GUI. Useful for scripting, CI pipelines, and batch processing.

```bash
# Clone a single page
python cloner.py https://example.com --headless

# Clone 3 levels deep, custom output
python cloner.py https://docs.python.org --headless -o ./python-docs -d 3

# All available flags
python cloner.py <url> [--headless] [--output <dir>] [--depth <n>]
```

| Flag | Alias | Description |
|:---|:---|:---|
| `<url>` | &mdash; | Website to clone (must start with `http://` or `https://`) |
| `--headless` | `-h` | Run without opening the GUI window |
| `--output <dir>` | `-o` | Directory to write the cloned site (default: `./cloned_site`) |
| `--depth <n>` | `-d` | Number of link levels to crawl (default: 1) |

<br>

---

##   Use Cases

<table>
<tr>
<td>

```markdown
  PLATFORM MIGRATION
  ──────────────────
  Moving from WordPress, Webflow,
  or Squarespace? Clone your live
  site as static HTML and deploy
  anywhere — Netlify, Vercel, S3,
  or GitHub Pages.
```

</td>
<td>

```markdown
  OFFLINE REFERENCE
  ─────────────────
  Save entire documentation sites,
  API references, and tutorials
  for offline access. Perfect for
  flights, commutes, or unreliable
  internet connections.
```

</td>
<td>

```markdown
  DESIGN RESEARCH
  ───────────────
  Study how production sites
  structure their HTML, CSS,
  and JavaScript by working
  directly with the real
  source code.
```

</td>
</tr>
<tr>
<td>

```markdown
  DIGITAL ARCHIVAL
  ────────────────
  Preserve a snapshot of a site
  before it changes, shuts down,
  or gets redesigned. Full
  offline copy with every asset.
```

</td>
<td>

```markdown
  LOST SOURCE RECOVERY
  ────────────────────
  Site is live but the original
  repo is gone? The developer
  left? Extract the full
  codebase from the deployed
  version.
```

</td>
<td>

```markdown
  RAPID PROTOTYPING
  ─────────────────
  Clone a landing page or
  component library as a
  starting point for your
  own project — modify
  and iterate fast.
```

</td>
</tr>
</table>

<br>

---

##   Keyboard Shortcuts

| Key | When | Action |
|:---:|:---|:---|
| `Enter` | URL field focused | Start clone |
| `Escape` | Cloning | Cancel clone |
| `Ctrl + V` | Anywhere | Paste URL from clipboard |
| `Ctrl + L` | Anywhere | Focus URL field |

<br>

---

##   Output Structure

```
cloned_site/
  │
  ├── index.html                  ← Main page (all URLs rewritten to relative paths)
  ├── about.html                  ← Additional crawled pages
  ├── pricing.html
  │
  ├── cloner_manifest.json        ← Full metadata: source URL, timestamps,
  │                                  asset map, byte counts, error log
  │
  └── assets/
        ├── img/                  ← hero.png, logo.svg, bg.jpg, favicon.ico ...
        ├── css/                  ← style.css, theme.css (url() refs rewritten)
        ├── js/                   ← app.js, vendor.js
        ├── fonts/                ← Inter.woff2, JetBrainsMono.ttf ...
        ├── videos/               ← intro.mp4
        ├── audio/                ← podcast.mp3
        ├── data/                 ← config.json, data.xml
        ├── other/                ← Everything that didn't match a known type
        └── docs/                 ← PDFs, documents
```

<br>

---

##   Architecture

```
cloner.py  (1,060 lines)
  │
  ├── C                      Design system constants (30+ colors, fonts)
  │
  ├── WebsiteCloner          Cloning engine
  │   ├── clone()            Orchestrator: crawl → collect → download → write
  │   ├── _collect()         Asset discovery from HTML attributes + CSS rules
  │   ├── _download_all()    ThreadPoolExecutor fan-out, progress tracking
  │   ├── _write_pages()     URL rewriting, CSS fixing, optional inline/minify
  │   ├── _manifest()        Export cloner_manifest.json with full metadata
  │   ├── _norm()            URL normalization & deduplication
  │   ├── _rewrite_css()     Replaces remote url() refs with local paths
  │   └── _css_urls()        Parse url() and @import from stylesheets
  │
  ├── RoundedFrame           Canvas-based card widget with rounded corners + shadow
  ├── ProgressBar            Animated progress with smooth value interpolation
  ├── Console                Color-coded scrollable log output
  ├── AssetTree              Live-updating treeview of downloaded files
  │
  └── ClonerApp              Full tkinter GUI
      ├── _build()           2-panel layout: sidebar + main content
      ├── _start() / _done() Clone lifecycle with button state toggling
      ├── _poll()            Thread-safe queue dispatch → UI updates (60ms tick)
      ├── _on_close()        Config serialization to disk
      ├── _bind_keys()       Keyboard shortcut registration
      └── _export()          ZIP packaging of cloned site
```

<br>

---

##   FAQ

<details open>
<summary><b>Is this legal?</b></summary>
<br>

Website Cloner is a tool, not an instruction. Respect copyright, terms of service, and robots.txt. Do not use it for phishing, impersonation, or passing off someone else's work as your own. It is intended for legitimate purposes: platform migration, offline reference, design research, and recovering your own lost source code.

</details>

<details>
<summary><b>Does it execute JavaScript?</b></summary>
<br>

No. Website Cloner downloads HTML and static assets. It does not run JavaScript, does not render SPAs, and does not use a headless browser. For JavaScript-heavy sites, the output will contain the raw HTML and scripts but dynamic content won't be pre-rendered.

</details>

<details>
<summary><b>Can it clone authenticated pages?</b></summary>
<br>

Not directly through the GUI, but the source code supports custom cookies. Pass them via the `cookies` option in the `opts` dict if using the engine programmatically.

</details>

<details>
<summary><b>What if a site blocks me?</b></summary>
<br>

Use the **Delay** setting to add cooldown between requests. Set a custom **User-Agent**. Use a **Proxy** to route through a different IP. Some sites use aggressive anti-bot measures (Cloudflare, Akamai) that may require additional tools.

</details>

<details>
<summary><b>Mac / Linux support?</b></summary>
<br>

The `.exe` is Windows-only, but the source code runs on **macOS and Linux** with Python 3.9+. Use Option B in the Quick Start guide.

</details>

<br>

---

##   Contributing

Pull requests are welcome. For major changes, open an issue first.

```bash
git clone https://github.com/JamesCowx/website-cloner.git
cd website-cloner
pip install -r requirements.txt

# Make your changes...
python cloner.py          # Test the GUI
python cloner.py https://example.com --headless   # Test CLI mode
```

> Keep the code simple. The entire project is a single file by design &mdash; `cloner.py`. No frameworks, no bundlers, no config files. Just Python + tkinter.

<br>

---

##   Star History

<p align="center">
  <a href="https://star-history.com/#JamesCowx/website-cloner&Date">
    <img src="https://api.star-history.com/svg?repos=JamesCowx/website-cloner&type=Date" width="500" alt="Star History Chart">
  </a>
</p>

<br>

---

<p align="center">
  <sub>
    <b>Website Cloner</b> &mdash; Built with Python + Tkinter<br>
    No API keys. No external services. No trackers.<br>
    <a href="https://github.com/JamesCowx/website-cloner/blob/master/LICENSE">MIT License</a>
  </sub>
</p>

<br>
