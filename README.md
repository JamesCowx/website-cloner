<div align="center">

<img src="https://img.shields.io/github/stars/JamesCowx/website-cloner?style=for-the-badge&logo=github&color=6366f1&logoColor=white" alt="Stars">
<img src="https://img.shields.io/github/license/JamesCowx/website-cloner?style=for-the-badge&color=22c55e" alt="MIT">
<img src="https://img.shields.io/badge/python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/windows-10%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
<img src="https://img.shields.io/badge/macOS%20%7C%20Linux-source-lightgrey?style=for-the-badge" alt="macOS/Linux">
<br>
<img src="https://img.shields.io/github/v/release/JamesCowx/website-cloner?color=22c55e&style=flat-square" alt="Release">
<a href="https://github.com/JamesCowx/website-cloner/releases/latest/download/WebsiteCloner.exe"><img src="https://img.shields.io/badge/Download-.exe-4f46e5?style=flat-square&logo=windows&logoColor=white" alt="Download"></a>
<img src="https://img.shields.io/github/repo-size/JamesCowx/website-cloner?color=f59e0b&style=flat-square" alt="Size">
<img src="https://img.shields.io/github/languages/code-size/JamesCowx/website-cloner?color=06b6d4&style=flat-square" alt="Code size">

</div>

<br>

<pre align="center">
  ██╗    ██╗███████╗██████╗ ███████╗██╗████████╗███████╗     ██████╗██╗      ██████╗ ███╗   ██╗███████╗██████╗  
  ██║    ██║██╔════╝██╔══██╗██╔════╝██║╚══██╔══╝██╔════╝    ██╔════╝██║     ██╔═══██╗████╗  ██║██╔════╝██╔══██╗ 
  ██║ █╗ ██║█████╗  ██████╔╝███████╗██║   ██║   █████╗      ██║     ██║     ██║   ██║██╔██╗ ██║█████╗  ██████╔╝ 
  ██║███╗██║██╔══╝  ██╔══██╗╚════██║██║   ██║   ██╔══╝      ██║     ██║     ██║   ██║██║╚██╗██║██╔══╝  ██╔══██╗ 
  ╚███╔███╔╝███████╗██████╔╝███████║██║   ██║   ███████╗    ╚██████╗███████╗╚██████╔╝██║ ╚████║███████╗██║  ██║ 
   ╚══╝╚══╝ ╚══════╝╚═════╝ ╚══════╝╚═╝   ╚═╝   ╚══════╝     ╚═════╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ 
</pre>

<p align="center">
  <b>Paste a URL. Press Clone. Own the output.</b><br>
  <sub>A single-file Python desktop app that downloads entire websites into static HTML.<br>Zero config. No API keys. No external services. Just your machine and a URL.</sub>
</p>

---

<br>

##   What Is This?

**Website Cloner** is a desktop application that turns any live website into a fully offline, self-contained folder of HTML + assets. Install it, paste a URL, and get a local copy that works without internet.

> &#x1F4A1; Think of it like `wget --mirror`, but with a beautiful GUI, parallel downloads, CSS rewriting, and ZIP export.

<br>

<table>
<tr>
<td width="50%" align="center">
  <h3>  Before</h3>
  <sub>The live site you want to archive, study, or migrate</sub>
  <br><br>
  <code>https://example.com</code>
  <br>
  <sup>&#x1F310; Online only &middot; Depends on server &middot; Can change or disappear</sup>
</td>
<td width="50%" align="center">
  <h3>  After</h3>
  <sub>A local folder you own completely</sub>
  <br><br>
  <code>cloned_site/index.html</code>
  <br>
  <sup>&#x1F4C1; Fully offline &middot; All assets local &middot; Yours forever</sup>
</td>
</tr>
</table>

---

<br>

##   Pick Your Path

<table>
<tr>
<td width="50%">

### &#x1F4E6; Download .exe (Windows)

<a href="https://github.com/JamesCowx/website-cloner/releases/latest/download/WebsiteCloner.exe">
  <img src="https://img.shields.io/badge/Download-WebsiteCloner.exe-6366f1?style=for-the-badge&logo=windows&logoColor=white" alt="Download">
</a>

- Double-click to run
- No Python install needed
- 12.8 MB &middot; Windows 10/11

</td>
<td width="50%">

### &#x1F4BB; Run from Source

```bash
git clone https://github.com/JamesCowx/website-cloner.git
cd website-cloner
pip install -r requirements.txt
python cloner.py
```

- Python 3.9+ required
- Works on Windows, macOS, Linux
- 1,060 lines &middot; single file

</td>
</tr>
</table>

---

<br>

##   The Pipeline

Four phases turn a URL into a folder:

```
 ┌──────────────────────────────────────────────────────────────────┐
 │                                                                   │
 │   1    Crawl                   2    Collect                       │
 │   ──────────                   ──────────                        │
 │   Fetch target page            Parse HTML & CSS                  │
 │   Follow same-domain links     Find every asset reference:       │
 │   Configurable depth (1-10)    <img> <script> <link> <video>    │
 │                                url() @import srcset               │
 │                                                                   │
 │   3    Download                 4    Rewrite                      │
 │   ──────────                   ──────────                        │
 │   ThreadPoolExecutor           Replace remote URLs               │
 │   Fan-out 8 workers            with local relative paths         │
 │   Real-time speed + progress   Fix CSS references                │
 │   Per-file status tracking     Optional: inline, minify           │
 │                                                                   │
 └──────────────────────────────────────────────────────────────────┘
```

<br>

### Visual Walkthrough

```
  https://stripe.com/pricing
       │
       ▼
 ┌──────────────────────────────────┐
 │ 1. CRAWL                          │
 │    GET /pricing → 200 OK          │
 │    Discover: /about, /docs, /api  │
 └──────────┬───────────────────────┘
            ▼
 ┌──────────────────────────────────┐
 │ 2. COLLECT                        │
 │    Found 247 assets:              │
 │     hero-bg.png                   │
 │     pricing.css                   │
 │     app.js                        │
 │     StripeSans.woff2              │
 │     logo.svg                      │
 │     ... and 242 more               │
 └──────────┬───────────────────────┘
            ▼
 ┌──────────────────────────────────┐
 │ 3. DOWNLOAD                       │
 │    Thread 1 ██░░  hero-bg.png    │
 │    Thread 2 ████  pricing.css    │
 │    Thread 3 ██░░  app.js         │
 │    ...8 threads hammering away...  │
 │    4.8 MB in 3.2s (1.5 MB/s)     │
 └──────────┬───────────────────────┘
            ▼
 ┌──────────────────────────────────┐
 │ 4. REWRITE                        │
 │    ../css/pricing.css → assets/   │
 │    /img/hero.png → assets/img/    │
 │    CSS url() refs → local paths   │
 └──────────────────────────────────┘
            │
            ▼
     cloned_site/
     ├── pricing.html     ← works offline
     ├── about.html
     ├── manifest.json    ← full metadata
     └── assets/
           ├── img/
           ├── css/
           ├── js/
           └── fonts/
```

---

<br>

##   Features

| Category | What You Get |
|---|---|
| &#x1F3A8; **GUI** | Dark-themed custom interface with rounded cards, Canvas-drawn shadows, animated progress bar, live stats dashboard |
| &#x26A1; **Speed** | ThreadPoolExecutor with configurable 1-20 workers, parallel asset downloading, real-time MB/s display |
| &#x1F310; **Crawl** | Same-domain link following up to configurable depth, filters `javascript:`, `mailto:`, `#` links automatically |
| &#x1F4DD; **CSS** | Parses `url()` and `@import` rules to discover nested assets, then rewrites them to local paths |
| &#x1F504; **Rewrite** | Converts every `src`, `href`, `srcset`, `poster`, and `data` attribute to relative paths |
| &#x1F4E6; **Export** | One-click ZIP packaging of the entire cloned site for sharing or archival |
| &#x2328; **CLI** | Full headless mode: `python cloner.py https://site.com --headless -o ./out -d 2` |
| &#x1F6E1; **Safety** | Configurable request delay, custom User-Agent, HTTP proxy support |
| &#x1F4BE; **Memory** | Saves settings, window geometry, and recent-URL history between sessions |
| &#x1F4CB; **Manifest** | `cloner_manifest.json` with source URL, byte counts, full asset map, and error log |

---

<br>

##   All Options

<details open>
<summary><b>  Content Filters</b></summary>

| Option | Default | Extensions Covered |
|---|---|---|
| **Images** | `ON` | `png` `jpg` `jpeg` `gif` `svg` `webp` `ico` `bmp` `tiff` |
| **CSS** | `ON` | `css` `scss` `less` `sass` |
| **JavaScript** | `ON` | `js` `mjs` `ts` `jsx` |
| **Fonts** | `ON` | `woff` `woff2` `ttf` `eot` `otf` |

</details>

<details>
<summary><b>  Processing</b></summary>

| Option | Default | Behavior |
|---|---|---|
| **Same domain** | `ON` | Restrict downloads to the target domain |
| **Strip params** | `ON` | Remove `?v=1.2.3` from filenames |
| **Rewrite CSS** | `ON` | Convert CSS `url()` paths to local |
| **Inline CSS** | `OFF` | Embed stylesheets as `<style>` tags |
| **Inline JS** | `OFF` | Embed scripts as `<script>` tags |
| **Minify HTML** | `OFF` | Collapse whitespace in output |

</details>

<details>
<summary><b>  Advanced</b></summary>

| Setting | Default | Range | Purpose |
|---|---|---|---|
| **Depth** | `1` | 1-10 | Link-following depth |
| **Workers** | `8` | 1-20 | Parallel download threads |
| **Delay** | `0.1s` | 0-5s | Cooldown between requests |
| **Timeout** | `30s` | 5-120s | Per-request max wait |
| **User-Agent** | `Chrome 125` | Any | Custom browser header |
| **Proxy** | _(none)_ | `host:port` | HTTP/HTTPS proxy |

</details>

---

<br>

##   CLI Mode

```bash
# One-liner: clone a page
python cloner.py https://example.com --headless

# Deep crawl, custom output
python cloner.py https://docs.python.org/3/ --headless -o ./python-docs -d 3

# Flags
python cloner.py <url> [--headless|-h] [--output|-o <dir>] [--depth|-d <n>]
```

---

<br>

##   Use Cases

<table>
<tr>
  <td width="50%">

### &#x1F3D7; Platform Migration
Moving from WordPress, Webflow, or Squarespace? Clone your live site as static HTML. Deploy anywhere &mdash; Netlify, Vercel, S3, GitHub Pages.

  </td>
  <td width="50%">

### &#x1F4DA; Offline Reference
Save entire documentation sites, API references, and tutorials for flights, commutes, or unreliable internet.

  </td>
</tr>
<tr>
  <td width="50%">

### &#x1F52C; Design Research
Study how production sites structure their HTML, CSS, and assets by working with the real source code directly.

  </td>
  <td width="50%">

### &#x1F4E4; Digital Archival
Preserve a snapshot of a site before it changes, shuts down, or gets redesigned. Complete offline copy with every asset intact.

  </td>
</tr>
<tr>
  <td width="50%">

### &#x26D3; Lost Source Recovery
Site is live but the repo is gone? Developer left? Stack is legacy? Extract the full codebase from the deployed version.

  </td>
  <td width="50%">

### &#x1F3C3; Rapid Prototyping
Clone a landing page or component library as a starting point &mdash; modify, iterate, ship.

  </td>
</tr>
</table>

---

<br>

##   Shortcuts

| Key | Action |
|:---:|:---|
| `Enter` | Start cloning |
| `Escape` | Cancel clone |
| `Ctrl + V` | Paste URL from clipboard |
| `Ctrl + L` | Focus URL field |

---

<br>

##   Output

```
cloned_site/
├── index.html              ← main page, all paths rewritten
├── about.html              ← crawled sub-pages
├── pricing.html
├── cloner_manifest.json    ← metadata: source, bytes, asset map, errors
└── assets/
      ├── img/              ← hero.png, logo.svg, favicon.ico, bg.jpg...
      ├── css/              ← style.css, theme.css (url() refs rewritten)
      ├── js/               ← app.js, vendor.js
      ├── fonts/            ← Inter.woff2, JetBrainsMono.ttf...
      ├── videos/           ← intro.mp4
      ├── audio/            ← podcast.mp3
      ├── data/             ← config.json, en.xml
      ├── docs/             ← whitepaper.pdf
      └── other/            ← uncategorized assets
```

---

<br>

##   Architecture

```
cloner.py  (single file, 1,060 lines, zero dependencies beyond stdlib + requests + bs4)

  ├── C                    30-color design system
  │
  ├── WebsiteCloner        Cloning engine
  │   ├── clone()          Orchestrator: crawl → collect → download → write
  │   ├── _collect()       Asset discovery (HTML attributes + CSS rules)
  │   ├── _download_all()  ThreadPoolExecutor fan-out with progress
  │   ├── _write_pages()   URL replacement, CSS fixing, inline/minify
  │   └── _manifest()      JSON metadata export
  │
  ├── RoundedFrame         Canvas-drawn cards with shadows
  ├── ProgressBar          Animated progress with value interpolation
  ├── Console              Color-coded log (info / ok / err / warn)
  ├── AssetTree            Live-updating treeview of downloads
  │
  └── ClonerApp            Full tkinter GUI
      ├── _build()         Two-panel layout
      ├── _poll()          Thread-safe queue dispatch (60ms tick)
      ├── _start/_done     Clone lifecycle
      └── _on_close()      Config serialization
```

---

<br>

##   FAQ

<details>
<summary><b>Is this legal?</b></summary>
<br>

Website Cloner is a tool. Respect copyright, terms of service, and robots.txt. Don't use it for phishing, impersonation, or passing off others' work as your own. Intended for legitimate use: platform migration, offline reference, design research, recovering your own lost code.

</details>

<details>
<summary><b>Does it run JavaScript?</b></summary>
<br>

No. It downloads static HTML and assets. JavaScript is not executed, SPAs are not pre-rendered, and there's no headless browser. For JS-heavy sites, the raw scripts will be present but dynamic content won't be pre-rendered.

</details>

<details>
<summary><b>Will I get blocked?</b></summary>
<br>

If a site has aggressive rate limiting, use the **Delay** setting (0.5s-2s), set a custom **User-Agent**, or route through a **Proxy**. Sites behind Cloudflare/Akamai may require additional tools.

</details>

<details>
<summary><b>Mac / Linux support?</b></summary>
<br>

The `.exe` is Windows-only, but the Python source runs on macOS and Linux with Python 3.9+. Use the "Run from Source" path above.

</details>

---

<br>

##   Star History

<p align="center">
  <a href="https://star-history.com/#JamesCowx/website-cloner&Date">
    <img src="https://api.star-history.com/svg?repos=JamesCowx/website-cloner&type=Date" width="500" alt="Star History Chart">
  </a>
</p>

---

<br>

<p align="center">
  <sub><b>Website Cloner</b> — 1 file, 3 dependencies, infinite offline websites.<br>
  <a href="https://github.com/JamesCowx/website-cloner/blob/master/LICENSE">MIT</a> ·
  <a href="https://github.com/JamesCowx/website-cloner/releases">Releases</a> ·
  <a href="https://jamescowx.github.io/website-cloner/">Landing Page</a></sub>
</p>

<br>
