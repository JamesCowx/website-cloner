#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Website Cloner -- Production v3.0
=================================
Full-GUI desktop application for cloning websites locally.
Supports CLI: python cloner.py <url> [-o <dir>] [--depth N] [--headless]
"""

import os
import re
import sys
import json
import time
import shutil
import zipfile
import signal
import threading
import queue
import urllib.parse
import webbrowser
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    import requests
except ImportError:
    requests = None
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

# ── Design System ──────────────────────────────────────────────
C = {
    "bg": "#0a0a0f", "bg2": "#111118", "surf": "#191a23",
    "surf2": "#1f2130", "over": "#252838", "bdr": "#2a2d3d",
    "bdra": "#6366f1", "fg": "#c8ccd8", "fgd": "#6b7084",
    "fgb": "#e4e6f0", "acc": "#6366f1", "acc2": "#818cf8",
    "green": "#22c55e", "greenbg": "#0f2a1a", "red": "#ef4444",
    "redbg": "#2a1015", "orange": "#f59e0b", "orangebg": "#2a1f0a",
    "blue": "#6366f1", "cyan": "#06b6d4",
    "ibg": "#0e0f18", "ibb": "#2a2d3d", "ibbf": "#6366f1",
    "btn": "#1f2130", "btnh": "#2a2d3d", "btnf": "#c8ccd8",
    "btnpb": "#6366f1", "btnpf": "#ffffff", "btnph": "#4f46e5",
    "btndb": "#dc2626", "btndf": "#ffffff", "btndh": "#b91c1c",
    "tb": "#111118", "tf": "#c8ccd8", "ts": "#1a1f3a",
    "progbg": "#1f2130",
    "tabbg": "#13141e", "tababg": "#191a23",
    "tabfg": "#6b7084", "tabafg": "#e4e6f0",
    "card": "#191a23", "card2": "#13141e",
    "headerbg": "#0e0f16", "sep": "#1f2130",
}
FONT = "Segoe UI"
FMONO = "Consolas"
CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "WebsiteCloner")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Regexes
RE_CSS_URL = re.compile(r"""url\s*\(\s*["']?([^"'()\s]+)["']?\s*\)""")
RE_CSS_IMPORT = re.compile(r"""@import\s+["']([^"']+)["']""")
RE_CSS_URL_FULL = re.compile(r"""(url\s*\()\s*(["']?)([^"'()\s]+)\2\s*\)""")
RE_INVALID_FILECHARS = re.compile(r'[<>:"/\\|?*]')
RE_WHITESPACE = re.compile(r">\s+<")
RE_BLANK = re.compile(r"\n\s*\n")
RE_URL = re.compile(r"^https?://[^\s]+$")


# ═══════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════

def fmt_bytes(b):
    if b < 1024:
        return str(b) + " B"
    if b < 1024 * 1024:
        return format(b / 1024, ".1f") + " KB"
    if b < 1024 * 1024 * 1024:
        return format(b / (1024 * 1024), ".1f") + " MB"
    return format(b / (1024 * 1024 * 1024), ".2f") + " GB"


def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_config(cfg):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass


def parse_cli():
    args = {"url": None, "out": None, "depth": 1, "headless": False}
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("-o", "--output") and i + 1 < len(argv):
            i += 1; args["out"] = argv[i]
        elif a in ("-d", "--depth") and i + 1 < len(argv):
            i += 1
            try:
                args["depth"] = int(argv[i])
            except ValueError:
                pass
        elif a in ("-h", "--headless"):
            args["headless"] = True
        elif a.startswith("http"):
            args["url"] = a
        i += 1
    return args


# ═══════════════════════════════════════════════════════════════
# CLONING ENGINE
# ═══════════════════════════════════════════════════════════════

class WebsiteCloner:
    UA_DEFAULT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )

    def __init__(self, log_cb=None, prog_cb=None, asset_cb=None, speed_cb=None):
        if requests is None:
            raise RuntimeError("requests library not installed. Run: pip install requests")
        if BeautifulSoup is None:
            raise RuntimeError("beautifulsoup4 not installed. Run: pip install beautifulsoup4")
        self._init_session()
        self.base = ""
        self.out = ""
        self.dl = {}
        self.total = 0
        self.done = 0
        self.errs = []
        self.amap = {}
        self.stop = False
        self.opts = {}
        self.t0 = 0
        self.bytes = 0
        self._lock = threading.Lock()
        self.pages = 0
        self.soups = {}
        self.log_cb = log_cb
        self.prog_cb = prog_cb
        self.asset_cb = asset_cb
        self.speed_cb = speed_cb

    def _init_session(self):
        self.s = requests.Session()
        self.s.headers.update({
            "User-Agent": self.UA_DEFAULT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
        })

    def log(self, msg, tag="info"):
        if self.log_cb:
            self.log_cb(msg, tag)

    def upd(self):
        if self.prog_cb:
            self.prog_cb(self.done, self.total)
        if self.speed_cb and self.t0:
            e = max(time.time() - self.t0, 0.001)
            mb = self.bytes / (1024 * 1024)
            self.speed_cb(mb, e, self.done, self.total)

    def cancel(self):
        self.stop = True

    @staticmethod
    def _is_http(u):
        return u.startswith(("http://", "https://"))

    def _norm(self, url, base=None):
        if not url:
            return ""
        base = base or self.base
        skip = ("data:", "javascript:", "mailto:", "tel:", "#")
        if url.startswith(skip):
            return url
        if url.startswith("//"):
            url = "https:" + url
        elif url.startswith("/"):
            url = urllib.parse.urljoin(base, url)
        elif not self._is_http(url):
            url = urllib.parse.urljoin(base + "/", url)
        clean = url.split("#")[0]
        if self.opts.get("strip_query", True):
            clean = clean.split("?")[0]
        return clean

    def _same_domain(self, url):
        if not url or not self._is_http(url):
            return False
        bd = urllib.parse.urlparse(self.base).netloc
        ud = urllib.parse.urlparse(url).netloc
        if not ud:
            return False
        if self.opts.get("same_domain_only", True):
            return bd == ud
        return (bd == ud or
                (bd.startswith("www.") and ud == bd[4:]) or
                (ud.startswith("www.") and bd == ud[4:]))

    def _fname(self, url):
        parsed = urllib.parse.urlparse(url)
        path = parsed.path.strip("/") or "index.html"
        parts = path.split("/")
        if not parts[-1] or "." not in parts[-1]:
            parts.append("index.html")
        return "/".join(RE_INVALID_FILECHARS.sub("_", p)[:200] for p in parts)

    @staticmethod
    def _atype(url):
        p = url.lower().split("?")[0]
        kinds = {
            "png": "img", "jpg": "img", "jpeg": "img", "gif": "img",
            "svg": "img", "webp": "img", "ico": "img", "bmp": "img",
            "css": "css", "scss": "css", "less": "css",
            "js": "js", "mjs": "js",
            "woff": "fonts", "woff2": "fonts", "ttf": "fonts",
            "eot": "fonts", "otf": "fonts",
            "mp4": "videos", "webm": "videos",
            "mp3": "audio", "wav": "audio",
            "json": "data", "xml": "data", "pdf": "docs", "zip": "archives",
        }
        for ext, cat in kinds.items():
            if p.endswith("." + ext):
                return cat
        return "other"

    def _download(self, url, path):
        if self.stop:
            return None
        try:
            d = self.opts.get("delay", 0)
            if d > 0:
                time.sleep(d)
            r = self.s.get(url, timeout=self.opts.get("timeout", 30), stream=True)
            r.raise_for_status()
            ct = r.headers.get("content-type", "").lower()
            if "text/html" in ct and not path.endswith((".html", ".htm")):
                text = r.text
                with self._lock:
                    self.bytes += len(text.encode("utf-8"))
                return text
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "wb") as f:
                for chunk in r.iter_content(65536):
                    if self.stop:
                        return None
                    f.write(chunk)
                    with self._lock:
                        self.bytes += len(chunk)
            return path
        except Exception:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
            return None

    def _css_urls(self, css, base_url):
        results = []
        for m in RE_CSS_URL.finditer(css):
            u = self._norm(m.group(1), base_url)
            if u and not u.startswith("data:"):
                results.append(u)
        for m in RE_CSS_IMPORT.finditer(css):
            u = self._norm(m.group(1), base_url)
            if u and not u.startswith("data:"):
                results.append(u)
        return results

    def _rewrite_css(self, css, base_url):
        def repl(m):
            url = m.group(3)
            if url.startswith("data:"):
                return m.group(0)
            full = self._norm(url, base_url)
            local = self.amap.get(full)
            if local:
                rel = os.path.relpath(local, self.out).replace("\\", "/")
                return m.group(1) + '("' + rel + '")'
            return m.group(0)
        return RE_CSS_URL_FULL.sub(repl, css)

    # ── Main ──

    def clone(self, url, out_dir, options=None):
        self.base = url
        self.out = os.path.abspath(out_dir)
        self.opts = options or {}
        self.stop = False
        self.dl = {}
        self.errs = []
        self.amap = {}
        self.done = 0
        self.total = 0
        self.bytes = 0
        self.t0 = time.time()
        self.pages = 0
        self.soups = {}
        os.makedirs(self.out, exist_ok=True)

        if self.opts.get("custom_ua"):
            self.s.headers["User-Agent"] = self.opts["custom_ua"]
        if self.opts.get("proxy"):
            self.s.proxies = {"http": self.opts["proxy"], "https": self.opts["proxy"]}
        if "cookies" in self.opts:
            self.s.cookies.update(self.opts["cookies"])

        try:
            depth = self.opts.get("depth", 1)
            seen = set()
            q = [(url, 0)]

            while q and not self.stop:
                cur, cd = q.pop(0)
                if cur in seen or cd > depth:
                    continue
                if not self._is_http(cur) or not self._same_domain(cur):
                    continue
                seen.add(cur)

                self.log("Crawling [d=" + str(cd) + "]: " + cur)
                try:
                    r = self.s.get(cur, timeout=self.opts.get("timeout", 30))
                    r.raise_for_status()
                except Exception as e:
                    self.log("Skip " + cur + ": " + str(e)[:80], "warn")
                    continue

                if not self.base:
                    self.base = r.url
                soup = BeautifulSoup(r.text, "html.parser")
                self.soups[cur] = soup
                self.pages += 1
                self._collect(soup, cur)

                if cd < depth:
                    for a in soup.find_all("a", href=True):
                        href = self._norm(a["href"], cur)
                        if (href and self._is_http(href) and
                                href not in seen and self._same_domain(href) and
                                not any(href == v[0] for v in q)):
                            q.append((href, cd + 1))

            self.total = len(self.dl)
            self.log("Found " + str(self.total) + " assets in " + str(self.pages) + " page(s)")

            if not self.soups:
                self.log("No pages were fetched successfully", "err")
                return False

            self._download_all()
            self._write_pages()
            self._manifest()

            elapsed = time.time() - self.t0
            self.log("Done! " + fmt_bytes(self.bytes) + " in " +
                     format(elapsed, ".1f") + "s", "ok")
            return True

        except Exception as e:
            import traceback
            self.log("FATAL: " + str(e), "err")
            traceback.print_exc()
            return False
        finally:
            self._init_session()

    def _collect(self, soup, page_url):
        rules = [
            ("img", "src"), ("img", "srcset"),
            ("link[rel=stylesheet]", "href"),
            ("link[rel=icon]", "href"),
            ("link[rel='shortcut icon']", "href"),
            ("link[rel='apple-touch-icon']", "href"),
            ("script", "src"), ("source", "src"), ("source", "srcset"),
            ("video", "src"), ("video", "poster"), ("audio", "src"),
            ("iframe", "src"), ("embed", "src"), ("object", "data"),
            ("link[rel=preload]", "href"), ("use", "href"),
            ("image", "href"),
        ]
        excl = {
            "img": not self.opts.get("clone_images", True),
            "css": not self.opts.get("clone_css", True),
            "js": not self.opts.get("clone_js", True),
            "fonts": not self.opts.get("clone_fonts", True),
        }
        for sel, attr in rules:
            for el in soup.select(sel):
                src = el.get(attr, "")
                if not src or src.startswith(("data:", "#")):
                    continue
                full = self._norm(src, page_url)
                if not full or full in self.dl:
                    continue
                at = self._atype(full)
                if excl.get(at, False):
                    continue
                fn = self._fname(full)
                local = os.path.join(self.out, "assets", at, os.path.basename(fn))
                self.dl[full] = local

        if self.opts.get("clone_css", True):
            for el in soup.select("link[rel=stylesheet]"):
                href = self._norm(el.get("href", ""), page_url)
                if href in self.dl:
                    try:
                        r = self.s.get(href, timeout=15)
                        for au in self._css_urls(r.text, href):
                            if au not in self.dl:
                                at = self._atype(au)
                                fn = self._fname(au)
                                self.dl[au] = os.path.join(
                                    self.out, "assets", at, os.path.basename(fn))
                    except Exception:
                        pass

    def _download_all(self):
        items = list(self.dl.items())
        workers = self.opts.get("workers", 8)
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = {}
            for au, lp in items:
                if self.stop:
                    break
                futures[ex.submit(self._download, au, lp)] = (au, lp)
            for future in as_completed(futures):
                if self.stop:
                    break
                au, lp = futures[future]
                try:
                    result = future.result()
                    if result:
                        self.amap[au] = lp
                    if self.asset_cb:
                        self.asset_cb(au, "ok" if result else "fail", lp)
                except Exception:
                    if self.asset_cb:
                        self.asset_cb(au, "fail", lp)
                with self._lock:
                    self.done += 1
                self.upd()

    def _write_pages(self):
        attr_map = {
            "img": ["src", "srcset"],
            "link[rel=stylesheet]": ["href"],
            "link[rel=icon]": ["href"],
            "link[rel='shortcut icon']": ["href"],
            "link[rel='apple-touch-icon']": ["href"],
            "script": ["src"],
            "source": ["src", "srcset"],
            "video": ["src", "poster"],
            "audio": ["src"],
            "iframe": ["src"], "embed": ["src"], "object": ["data"],
            "use": ["href"], "image": ["href"],
        }
        for pu, sp in self.soups.items():
            for sel, attrs in attr_map.items():
                for el in sp.select(sel):
                    for attr in attrs:
                        src = el.get(attr, "")
                        if not src:
                            continue
                        full = self._norm(src, pu)
                        local = self.amap.get(full)
                        if local:
                            el[attr] = os.path.relpath(
                                local, self.out).replace("\\", "/")

            if self.opts.get("rewrite_css_urls", True):
                for el in sp.select("link[rel=stylesheet]"):
                    href = el.get("href", "")
                    full = self._norm(href, pu)
                    local = self.amap.get(full)
                    if local and os.path.exists(local):
                        try:
                            with open(local, "r", encoding="utf-8") as f:
                                css = f.read()
                            css = self._rewrite_css(css, full)
                            with open(local, "w", encoding="utf-8") as f:
                                f.write(css)
                        except Exception:
                            pass

            for tag_sel, tag_name, opt_key in [
                ("link[rel=stylesheet]", "style", "inline_css"),
                ("script[src]", "script", "inline_js"),
            ]:
                if self.opts.get(opt_key, False):
                    for el in sp.select(tag_sel):
                        src = el.get("href", "") if tag_sel.startswith("link") else el.get("src", "")
                        full = self._norm(src, pu)
                        local = self.amap.get(full)
                        if local and os.path.exists(local):
                            try:
                                with open(local, "r", encoding="utf-8") as f:
                                    content = f.read()
                                st = sp.new_tag(tag_name)
                                st.string = content
                                el.replace_with(st)
                                os.remove(local)
                            except Exception:
                                pass

            if self.opts.get("minify_html", False):
                html = str(sp)
                html = RE_BLANK.sub("\n", html)
                html = RE_WHITESPACE.sub("><", html)

            rp = self._page_path(pu)
            fp = os.path.join(self.out, rp)
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            html = str(sp)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(html)

    def _page_path(self, url):
        parsed = urllib.parse.urlparse(url)
        path = parsed.path.strip("/") or "index.html"
        parts = path.split("/")
        if not parts[-1] or "." not in parts[-1]:
            parts.append("index.html")
        return "/".join(RE_INVALID_FILECHARS.sub("_", p)[:200] for p in parts)

    def _manifest(self):
        mf = {
            "source_url": self.base,
            "cloned_at": datetime.now().isoformat(),
            "output_directory": self.out,
            "pages": self.pages,
            "total_assets": len(self.amap),
            "total_bytes": self.bytes,
            "total_size": fmt_bytes(self.bytes),
            "errors": self.errs[:100],
            "assets": {u: p for u, p in self.amap.items()},
        }
        with open(os.path.join(self.out, "cloner_manifest.json"), "w", encoding="utf-8") as f:
            json.dump(mf, f, indent=2)


# ═══════════════════════════════════════════════════════════════
# CUSTOM WIDGETS
# ═══════════════════════════════════════════════════════════════

class RoundedFrame(tk.Canvas):
    """Card with rounded corners and optional shadow."""
    def __init__(self, parent, bg=None, radius=10, shadow=False, **kw):
        bg = bg or C["card"]
        kw.setdefault("highlightthickness", 0)
        super().__init__(parent, bg=C["bg"], **kw)
        self._r = radius
        self._shadow = shadow
        self._fill = bg
        self.inner = tk.Frame(self, bg=bg)
        self.bind("<Configure>", self._draw)

    def _draw(self, event=None):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        r = self._r
        if w < 4 or h < 4:
            return
        if self._shadow:
            self._round_rect(3, 4, w - 3, h - 3, r, fill="#000000", stipple="gray25")
        self._round_rect(0, 0, w, h, r, fill=self._fill, outline=self._fill)
        self.create_window(r + 2, r + 2, anchor="nw", window=self.inner)

    def _round_rect(self, x1, y1, x2, y2, r, **kw):
        d = 2 * r
        fill = kw.get("fill", "")
        stipple = kw.get("stipple", "")
        for ax, ay, sx, sy, sa in [
            (x1, y1, x1 + d, y1 + d, 90),
            (x2 - d, y1, x2, y1 + d, 0),
            (x1, y2 - d, x1 + d, y2, 180),
            (x2 - d, y2 - d, x2, y2, 270),
        ]:
            self.create_arc(ax, ay, sx, sy, start=sa, extent=90,
                            style="pieslice", fill=fill, outline="", stipple=stipple)
        self.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill, outline="", stipple=stipple)
        self.create_rectangle(x1, y1 + r, x2, y2 - r, fill=fill, outline="", stipple=stipple)


class ProgressBar(tk.Canvas):
    """Animated progress bar with gradient fill and percentage label."""
    def __init__(self, parent, **kw):
        kw.setdefault("height", 26)
        kw.setdefault("highlightthickness", 0)
        super().__init__(parent, bg=C["bg"], **kw)
        self._val = 0.0
        self._tgt = 0.0
        self._anim = None
        self.bind("<Configure>", self._draw)
        self.bind("<Destroy>", self._on_destroy)

    def _on_destroy(self, event=None):
        if self._anim:
            self.after_cancel(self._anim)

    def set_value(self, pct):
        self._tgt = max(0.0, min(100.0, pct))

    def _draw(self, event=None):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 10 or h < 4:
            return
        m = 1
        r = (h - 2 * m) // 2
        # Track
        self._bar(0, h, m, r, C["progbg"])
        # Animation
        self._val += (self._tgt - self._val) * 0.25
        if abs(self._val - self._tgt) < 0.2:
            self._val = self._tgt
        if self._val > 0.5:
            fw = max(r * 2, int(w * self._val / 100.0))
            self._bar(fw, h, m, r, C["acc"])
        if self._val > 5:
            self.create_text(w // 2, h // 2, text=format(self._val, ".0f") + "%",
                             fill="#ffffff", font=(FONT, 9, "bold"))
        if self._tgt > 0 or abs(self._val - self._tgt) > 0.1:
            if self._anim:
                self.after_cancel(self._anim)
            self._anim = self.after(35, self._draw)

    def _bar(self, bw, h, m, r, color):
        x1, y1 = m, m
        x2, y2 = bw - m, h - m
        d = 2 * r
        self.create_arc(x1, y1, x1 + d, y1 + d, start=90, extent=90,
                        style="pieslice", fill=color, outline="")
        self.create_arc(x2 - d, y1, x2, y1 + d, start=0, extent=90,
                        style="pieslice", fill=color, outline="")
        self.create_arc(x1, y2 - d, x1 + d, y2, start=180, extent=90,
                        style="pieslice", fill=color, outline="")
        self.create_arc(x2 - d, y2 - d, x2, y2, start=270, extent=90,
                        style="pieslice", fill=color, outline="")
        self.create_rectangle(x1 + r, y1, x2 - r, y2, fill=color, outline="")
        self.create_rectangle(x1, y1 + r, x2, y2 - r, fill=color, outline="")


class Console(tk.Frame):
    """Color-coded scrollable log output."""
    def __init__(self, parent):
        super().__init__(parent, bg=C["tb"])
        self.text = tk.Text(
            self, bg=C["tb"], fg=C["tf"], insertbackground=C["tf"],
            font=(FMONO, 9), wrap="word", state="disabled",
            borderwidth=0, padx=12, pady=8, relief="flat",
            selectbackground=C["ts"], selectforeground=C["fgb"])
        sb = tk.Scrollbar(self, bg=C["tb"], troughcolor=C["tb"],
                          activebackground=C["over"])
        self.text.configure(yscrollcommand=sb.set)
        sb.configure(command=self.text.yview)
        self.text.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        for tn, tc in [
            ("info", C["acc"]), ("ok", C["green"]),
            ("err", C["red"]), ("warn", C["orange"]),
            ("ts", C["fgd"]), ("dim", C["fgd"]),
        ]:
            self.text.tag_config(tn, foreground=tc)

    def write(self, msg, tag="info"):
        try:
            self.text.configure(state="normal")
            ts = datetime.now().strftime("%H:%M:%S")
            self.text.insert("end", "[" + ts + "] ", "ts")
            self.text.insert("end", msg + "\n", tag)
            self.text.see("end")
            self.text.configure(state="disabled")
        except tk.TclError:
            pass

    def clear(self):
        try:
            self.text.configure(state="normal")
            self.text.delete("1.0", "end")
            self.text.configure(state="disabled")
        except tk.TclError:
            pass


class AssetTree(tk.Frame):
    """Live-updating tree view of downloaded assets."""
    def __init__(self, parent):
        super().__init__(parent, bg=C["tb"])
        sty = ttk.Style()
        sty.configure("At.Treeview", background=C["tb"], foreground=C["tf"],
                      fieldbackground=C["tb"], borderwidth=0, rowheight=24)
        sty.configure("At.Treeview.Heading", background=C["card2"],
                      foreground=C["fgd"], font=(FONT, 9, "bold"),
                      borderwidth=0, padding=6)
        sty.map("At.Treeview", background=[("selected", C["ts"])],
                foreground=[("selected", C["fgb"])])
        sty.layout("At.Treeview", [("At.Treeview.treearea", {"sticky": "nswe"})])

        self.tree = ttk.Treeview(self, columns=("st", "pa"), show="headings",
                                 height=10, style="At.Treeview")
        self.tree.heading("st", text="Status", anchor="w")
        self.tree.heading("pa", text="Asset URL", anchor="w")
        self.tree.column("st", width=52, minwidth=50, stretch=False)
        self.tree.column("pa", width=500, minwidth=200)
        sb = ttk.Scrollbar(self, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._colors = {"ok": C["green"], "fail": C["red"], "pending": C["orange"]}

    def add(self, url, status, path=""):
        lbl = {"ok": "OK", "fail": "FAIL", "pending": "..."}.get(status, "?")
        dsp = path if path else (url[:110] + "..." if len(url) > 110 else url)
        try:
            iid = self.tree.insert("", "end", values=(lbl, dsp))
            clr = self._colors.get(status, C["fgd"])
            self.tree.tag_configure("r_" + iid, foreground=clr)
            self.tree.item(iid, tags=("r_" + iid,))
            kids = self.tree.get_children()
            if kids:
                self.tree.see(kids[-1])
        except tk.TclError:
            pass

    def clear(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
        except tk.TclError:
            pass


# ═══════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════

class ClonerApp:
    def __init__(self, cli_args=None):
        self.root = tk.Tk()
        self.root.title("Website Cloner")
        self.root.geometry("1160x790")
        self.root.minsize(1020, 680)
        self.root.configure(bg=C["bg"])
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        self.cli = cli_args or {}
        self.cloner = WebsiteCloner(
            log_cb=self._on_log, prog_cb=self._on_prog,
            asset_cb=self._on_asset, speed_cb=self._on_speed)
        self.running = False
        self.anim_id = None

        self._cfg = load_config()
        self.history = self._cfg.get("history", [])
        default_out = os.path.join(os.path.expanduser("~"), "Desktop", "cloned_site")

        # State vars
        self.out_dir = tk.StringVar(value=self._cfg.get("out_dir", default_out))
        self.url_var = tk.StringVar()
        self.depth_var = tk.IntVar(value=self._cfg.get("depth", 1))
        self.workers_var = tk.IntVar(value=self._cfg.get("workers", 8))
        self.delay_var = tk.DoubleVar(value=self._cfg.get("delay", 0.1))
        self.timeout_var = tk.IntVar(value=self._cfg.get("timeout", 30))
        self.ua_var = tk.StringVar(value=self._cfg.get("ua", ""))
        self.proxy_var = tk.StringVar(value=self._cfg.get("proxy", ""))

        self.sp = tk.StringVar(value="0")
        self.sa = tk.StringVar(value="0")
        self.ss = tk.StringVar(value="0 B")
        self.sv = tk.StringVar(value="0 MB/s")

        self.o_img = tk.BooleanVar(value=self._cfg.get("o_img", True))
        self.o_css = tk.BooleanVar(value=self._cfg.get("o_css", True))
        self.o_js = tk.BooleanVar(value=self._cfg.get("o_js", True))
        self.o_font = tk.BooleanVar(value=self._cfg.get("o_font", True))
        self.o_icss = tk.BooleanVar(value=self._cfg.get("o_icss", False))
        self.o_ijs = tk.BooleanVar(value=self._cfg.get("o_ijs", False))
        self.o_sq = tk.BooleanVar(value=self._cfg.get("o_sq", True))
        self.o_sd = tk.BooleanVar(value=self._cfg.get("o_sd", True))
        self.o_min = tk.BooleanVar(value=self._cfg.get("o_min", False))
        self.o_rcss = tk.BooleanVar(value=self._cfg.get("o_rcss", True))
        self.adv_open = self._cfg.get("adv_open", False)

        self.lq = queue.Queue()
        self.aq = queue.Queue()
        self.pq = queue.Queue()
        self.sq = queue.Queue()

        self._build()
        self._bind_keys()
        self._restore_window()
        self._poll()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        if self.cli.get("headless") and self.cli.get("url"):
            self.url_var.set(self.cli["url"])
            if self.cli.get("out"):
                self.out_dir.set(self.cli["out"])
            if self.cli.get("depth"):
                self.depth_var.set(self.cli["depth"])
            self.root.after(300, self._start)

    # ── Callbacks ──
    def _on_log(self, msg, tag="info"):
        self.lq.put((msg, tag))

    def _on_prog(self, done, total):
        self.pq.put((done, total))

    def _on_asset(self, url, status, path=""):
        self.aq.put((url, status, path))

    def _on_speed(self, mb, elapsed, done, total):
        self.sq.put((mb, elapsed, done, total))

    def _poll(self):
        try:
            while True:
                msg, tag = self.lq.get_nowait()
                self.console.write(msg, tag)
        except queue.Empty:
            pass
        try:
            while True:
                url, status, path = self.aq.get_nowait()
                self.asset_tree.add(url, status, path)
        except queue.Empty:
            pass
        try:
            while True:
                done, total = self.pq.get_nowait()
                if total > 0:
                    self.bar.set_value(min(int(done / total * 100), 100))
                    self.prog_lbl.configure(text=str(done) + " / " + str(total) + " assets")
                    self.sa.set(str(done))
        except queue.Empty:
            pass
        try:
            while True:
                mb, elapsed, done, total = self.sq.get_nowait()
                speed = mb / elapsed if elapsed > 0 else 0
                self.ss.set(fmt_bytes(int(mb * 1024 * 1024)))
                self.sv.set(format(speed, ".1f") + " MB/s")
        except queue.Empty:
            pass
        self.anim_id = self.root.after(60, self._poll)

    # ── Keyboard Shortcuts ──
    def _bind_keys(self):
        self.root.bind("<Return>", lambda e: self._start() if not self.running else None)
        self.root.bind("<Escape>", lambda e: self._stop() if self.running else None)
        self.root.bind("<Control-v>", self._paste_url)
        self.root.bind("<Control-l>", lambda e: self.url_entry.focus_set())

    def _paste_url(self, event=None):
        try:
            clip = self.root.clipboard_get()
            if RE_URL.match(clip.strip()):
                self.url_var.set(clip.strip())
            elif clip.strip():
                self.url_var.set(clip.strip())
        except tk.TclError:
            pass

    # ── Window Management ──
    def _restore_window(self):
        geo = self._cfg.get("geometry")
        if geo:
            try:
                self.root.geometry(geo)
            except tk.TclError:
                pass

    def _on_close(self):
        try:
            self._cfg["geometry"] = self.root.geometry()
            self._cfg["out_dir"] = self.out_dir.get()
            self._cfg["depth"] = self.depth_var.get()
            self._cfg["workers"] = self.workers_var.get()
            self._cfg["delay"] = self.delay_var.get()
            self._cfg["timeout"] = self.timeout_var.get()
            self._cfg["ua"] = self.ua_var.get()
            self._cfg["proxy"] = self.proxy_var.get()
            self._cfg["o_img"] = self.o_img.get()
            self._cfg["o_css"] = self.o_css.get()
            self._cfg["o_js"] = self.o_js.get()
            self._cfg["o_font"] = self.o_font.get()
            self._cfg["o_icss"] = self.o_icss.get()
            self._cfg["o_ijs"] = self.o_ijs.get()
            self._cfg["o_sq"] = self.o_sq.get()
            self._cfg["o_sd"] = self.o_sd.get()
            self._cfg["o_min"] = self.o_min.get()
            self._cfg["o_rcss"] = self.o_rcss.get()
            self._cfg["adv_open"] = self.adv_open
            self._cfg["history"] = self.history[-20:]
            save_config(self._cfg)
        except Exception:
            pass
        if self.running:
            self.cloner.cancel()
        if self.anim_id:
            self.root.after_cancel(self.anim_id)
        self.root.destroy()

    # ── BUILD UI ──
    def _build(self):
        # Header
        hdr = tk.Frame(self.root, bg=C["headerbg"], height=48)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        lf = tk.Frame(hdr, bg=C["headerbg"])
        lf.pack(side="left", padx=18, pady=12)
        tk.Label(lf, text="[", font=(FMONO, 14, "bold"),
                 bg=C["headerbg"], fg=C["fgd"]).pack(side="left")
        tk.Label(lf, text="Cloner", font=(FMONO, 14, "bold"),
                 bg=C["headerbg"], fg=C["acc"]).pack(side="left")
        tk.Label(lf, text="]", font=(FMONO, 14, "bold"),
                 bg=C["headerbg"], fg=C["fgd"]).pack(side="left")
        tk.Label(lf, text=" v3", font=(FONT, 8),
                 bg=C["headerbg"], fg=C["fgd"]).pack(side="left", padx=(4, 0))

        af = tk.Frame(hdr, bg=C["headerbg"])
        af.pack(side="right", padx=12, pady=10)
        for lbl, cmd in [("Open Site", self._open), ("Export ZIP", self._export)]:
            b = tk.Label(af, text=lbl, bg=C["headerbg"], fg=C["fgd"],
                         font=(FONT, 9), padx=12, pady=4, cursor="hand2")
            b.pack(side="left", padx=2)
            b.bind("<Button-1>", lambda e, c=cmd: c())
            b.bind("<Enter>", lambda e, b=b: b.configure(fg=C["fgb"]))
            b.bind("<Leave>", lambda e, b=b: b.configure(fg=C["fgd"]))

        tk.Frame(self.root, bg=C["sep"], height=1).pack(fill="x")

        # Main
        main = tk.Frame(self.root, bg=C["bg"])
        main.pack(fill="both", expand=True, padx=12, pady=10)

        # LEFT
        left = tk.Frame(main, bg=C["bg"], width=350)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        # URL
        uc = RoundedFrame(left, bg=C["card"], shadow=True)
        uc.pack(fill="x", pady=(0, 8))
        ci = uc.inner
        tk.Label(ci, text="Target URL", font=(FONT, 11, "bold"),
                 bg=C["card"], fg=C["fgb"]).pack(anchor="w")

        url_row = tk.Frame(ci, bg=C["card"])
        url_row.pack(fill="x", pady=(8, 8))
        self.url_entry = tk.Entry(url_row, textvariable=self.url_var, font=(FONT, 11),
                                  bg=C["ibg"], fg=C["fgb"], insertbackground=C["fgb"],
                                  insertwidth=1, relief="flat", bd=1)
        self.url_entry.pack(side="left", fill="x", expand=True, ipady=6)
        past_btn = tk.Label(url_row, text="Paste", bg=C["card"], fg=C["fgd"],
                            font=(FONT, 8), cursor="hand2", padx=8, pady=4)
        past_btn.pack(side="left", padx=(8, 0))
        past_btn.bind("<Button-1>", lambda e: self._paste_url())
        past_btn.bind("<Enter>", lambda e, b=past_btn: b.configure(fg=C["acc"]))
        past_btn.bind("<Leave>", lambda e, b=past_btn: b.configure(fg=C["fgd"]))

        br = tk.Frame(ci, bg=C["card"])
        br.pack(fill="x")
        self.start_btn = self._btn(br, "CLONE", self._start, C["btnpb"], C["btnpf"], True)
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.stop_btn = self._btn(br, "STOP", self._stop, C["btndb"], C["btndf"], True)
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=(4, 0))
        self._disable_btn(self.stop_btn)

        # Output
        oc = RoundedFrame(left, bg=C["card"])
        oc.pack(fill="x", pady=(0, 8))
        oi = oc.inner
        tk.Label(oi, text="Output", font=(FONT, 10, "bold"),
                 bg=C["card"], fg=C["fgb"]).pack(anchor="w")
        or2 = tk.Frame(oi, bg=C["card"])
        or2.pack(fill="x", pady=(6, 0))
        self.out_entry = tk.Entry(or2, textvariable=self.out_dir, font=(FONT, 9),
                                  bg=C["ibg"], fg=C["fgb"], insertbackground=C["fgb"],
                                  insertwidth=1, relief="flat", bd=1)
        self.out_entry.pack(side="left", fill="x", expand=True, ipady=4)
        self._btn(or2, "...", self._browse, C["btn"], C["btnf"]).pack(side="left", padx=(6, 0))

        # Settings
        sc = RoundedFrame(left, bg=C["card"])
        sc.pack(fill="x", pady=(0, 8))
        si = sc.inner
        tk.Label(si, text="Settings", font=(FONT, 10, "bold"),
                 bg=C["card"], fg=C["fgb"]).pack(anchor="w", pady=(0, 6))
        for g in [
            [("Images", self.o_img), ("CSS", self.o_css)],
            [("JavaScript", self.o_js), ("Fonts", self.o_font)],
            [("Same domain", self.o_sd), ("Strip params", self.o_sq)],
            [("Rewrite CSS", self.o_rcss), ("Minify HTML", self.o_min)],
            [("Inline CSS", self.o_icss), ("Inline JS", self.o_ijs)],
        ]:
            r = tk.Frame(si, bg=C["card"])
            r.pack(fill="x", pady=1)
            for lbl, var in g:
                cb = tk.Checkbutton(r, text=lbl, variable=var, bg=C["card"], fg=C["fg"],
                                    selectcolor=C["card"], activebackground=C["card"],
                                    activeforeground=C["fgb"], font=(FONT, 9))
                cb.pack(side="left", padx=(0, 16))

        # Advanced
        ac = RoundedFrame(left, bg=C["card"])
        ac.pack(fill="x", pady=(0, 8))
        ai = ac.inner
        ah = tk.Frame(ai, bg=C["card"])
        ah.pack(fill="x")
        self.adv_arrow = tk.Label(ah, text="+" if not self.adv_open else "-",
                                  font=(FONT, 12, "bold"), bg=C["card"],
                                  fg=C["acc"], cursor="hand2")
        self.adv_arrow.pack(side="left", padx=(0, 6))
        self.adv_arrow.bind("<Button-1>", lambda e: self._toggle_adv())
        tk.Label(ah, text="Advanced", font=(FONT, 10, "bold"),
                 bg=C["card"], fg=C["fgb"]).pack(side="left")

        self.adv_inner = tk.Frame(ai, bg=C["card"])
        if self.adv_open:
            self.adv_inner.pack(fill="x", pady=(6, 0))

        for lbl, var in [("Depth", self.depth_var), ("Workers", self.workers_var),
                         ("Delay (s)", self.delay_var), ("Timeout (s)", self.timeout_var)]:
            r = tk.Frame(self.adv_inner, bg=C["card"])
            r.pack(fill="x", pady=2)
            tk.Label(r, text=lbl, bg=C["card"], fg=C["fg"], font=(FONT, 9)).pack(side="left")
            e = tk.Entry(r, textvariable=var, font=(FONT, 9), width=7,
                         bg=C["ibg"], fg=C["fgb"], insertbackground=C["fgb"],
                         insertwidth=1, relief="flat", bd=1, justify="center")
            e.pack(side="right", ipady=2)

        for lbl, var in [("User-Agent", self.ua_var), ("Proxy", self.proxy_var)]:
            rf = tk.Frame(self.adv_inner, bg=C["card"])
            rf.pack(fill="x", pady=2)
            tk.Label(rf, text=lbl, bg=C["card"], fg=C["fgd"], font=(FONT, 8)).pack(anchor="w")
            tk.Entry(rf, textvariable=var, font=(FONT, 8),
                     bg=C["ibg"], fg=C["fgd"], insertbackground=C["fgd"],
                     insertwidth=1, relief="flat", bd=1).pack(
                         fill="x", ipady=1, pady=(2, 0))

        # History
        if self.history:
            hc = RoundedFrame(left, bg=C["card"])
            hc.pack(fill="x", pady=(0, 8))
            hi = hc.inner
            tk.Label(hi, text="Recent", font=(FONT, 10, "bold"),
                     bg=C["card"], fg=C["fgb"]).pack(anchor="w", pady=(0, 4))
            for h in self.history[-5:]:
                if not isinstance(h, dict) or "url" not in h:
                    continue
                hr = tk.Frame(hi, bg=C["card"])
                hr.pack(fill="x", pady=1)
                url_text = h["url"][:50]
                if len(h["url"]) > 50:
                    url_text += "..."
                lbl = tk.Label(hr, text=url_text, bg=C["card"], fg=C["fgd"],
                               font=(FONT, 8), cursor="hand2", anchor="w")
                lbl.pack(side="left", fill="x", expand=True)
                lbl.bind("<Button-1>", lambda e, u=h["url"]: self.url_var.set(u))
                lbl.bind("<Enter>", lambda e, l=lbl: l.configure(fg=C["acc"]))
                lbl.bind("<Leave>", lambda e, l=lbl: l.configure(fg=C["fgd"]))

        # RIGHT PANEL
        right = tk.Frame(main, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))

        # Stats
        stf = tk.Frame(right, bg=C["bg"])
        stf.pack(fill="x", pady=(0, 8))
        for lbl, var, clr in [
            ("PAGES", self.sp, C["acc"]), ("ASSETS", self.sa, C["green"]),
            ("SIZE", self.ss, C["orange"]), ("SPEED", self.sv, C["cyan"]),
        ]:
            c = RoundedFrame(stf, bg=C["card2"], radius=10)
            c.pack(side="left", padx=(0, 6), ipady=4)
            t = c.inner
            tk.Label(t, text=lbl, font=(FONT, 7, "bold"),
                     bg=C["card2"], fg=C["fgd"]).pack(anchor="w")
            tk.Label(t, textvariable=var, font=(FONT, 13, "bold"),
                     bg=C["card2"], fg=clr).pack(anchor="w")

        # Progress
        pc = RoundedFrame(right, bg=C["card"])
        pc.pack(fill="x", pady=(0, 8))
        pi = pc.inner
        self.bar = ProgressBar(pi, height=26)
        self.bar.pack(fill="x", pady=(0, 5))
        self.prog_lbl = tk.Label(pi, text="Ready  (Enter to start, Esc to cancel)",
                                 font=(FONT, 8), bg=C["card"], fg=C["fgd"])
        self.prog_lbl.pack(anchor="w")

        # Notebook
        self.notebook = ttk.Notebook(right)
        self.notebook.pack(fill="both", expand=True)

        sty = ttk.Style()
        sty.theme_use("default")
        sty.configure("TNotebook", background=C["bg"], borderwidth=0)
        sty.configure("TNotebook.Tab", background=C["tabbg"], foreground=C["tabfg"],
                      padding=[20, 7], font=(FONT, 10), borderwidth=0)
        sty.map("TNotebook.Tab", background=[("selected", C["tababg"])],
                foreground=[("selected", C["tabafg"])])

        self.console = Console(self.notebook)
        self.notebook.add(self.console, text="  Console  ")
        self.asset_tree = AssetTree(self.notebook)
        self.notebook.add(self.asset_tree, text="  Assets  ")

    # ── Helpers ──
    def _btn(self, parent, text, cmd, bg, fg, bold=False):
        fnt = (FONT, 10, "bold") if bold else (FONT, 10)
        b = tk.Label(parent, text=text, bg=bg, fg=fg, font=fnt, padx=16, pady=7,
                     cursor="hand2", anchor="center")
        b.bind("<Button-1>", lambda e, c=cmd: c())
        if bg == C["btnpb"]:
            hov = C["btnph"]
        elif bg == C["btndb"]:
            hov = C["btndh"]
        else:
            hov = C["btnh"]
        b.bind("<Enter>", lambda e, b=b, h=hov: b.configure(bg=h))
        b.bind("<Leave>", lambda e, b=b, bg=bg: b.configure(bg=bg))
        return b

    def _disable_btn(self, b):
        b.configure(bg=C["bdr"], fg=C["fgd"], cursor="")
        b.unbind("<Button-1>"); b.unbind("<Enter>"); b.unbind("<Leave>")

    def _enable_btn(self, b, bg, fg, cmd):
        b.configure(bg=bg, fg=fg, cursor="hand2")
        b.bind("<Button-1>", lambda e, c=cmd: c())
        if bg == C["btnpb"]:
            hov = C["btnph"]
        elif bg == C["btndb"]:
            hov = C["btndh"]
        else:
            hov = C["btnh"]
        b.bind("<Enter>", lambda e, b=b, h=hov: b.configure(bg=h))
        b.bind("<Leave>", lambda e, b=b, bg=bg: b.configure(bg=bg))

    def _toggle_adv(self):
        if self.adv_open:
            self.adv_inner.pack_forget()
            self.adv_arrow.configure(text="+")
        else:
            self.adv_inner.pack(fill="x", pady=(6, 0))
            self.adv_arrow.configure(text="-")
        self.adv_open = not self.adv_open

    def _browse(self):
        d = filedialog.askdirectory(title="Select Output Directory")
        if d:
            self.out_dir.set(d)

    # ── Actions ──
    def _start(self):
        if self.running:
            return
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Enter a URL to clone.")
            return
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
            self.url_var.set(url)
        if not RE_URL.match(url):
            messagebox.showwarning("Invalid URL", "Please enter a valid URL.")
            return

        out = self.out_dir.get()
        if os.path.exists(out) and os.listdir(out):
            if not messagebox.askyesno("Directory Not Empty",
                                       "Output has " + str(len(os.listdir(out))) +
                                       " item(s). Continue?"):
                return

        self.running = True
        self._disable_btn(self.start_btn)
        self._enable_btn(self.stop_btn, C["btndb"], C["btndf"], self._stop)
        self.url_entry.configure(state="readonly")
        self.bar.set_value(0)
        self.prog_lbl.configure(text="Crawling...")
        self.sp.set("0"); self.sa.set("0")
        self.ss.set("0 B"); self.sv.set("0 MB/s")
        self.console.clear(); self.asset_tree.clear()

        opts = {
            "depth": self.depth_var.get(), "workers": self.workers_var.get(),
            "delay": self.delay_var.get(), "timeout": self.timeout_var.get(),
            "clone_images": self.o_img.get(), "clone_css": self.o_css.get(),
            "clone_js": self.o_js.get(), "clone_fonts": self.o_font.get(),
            "inline_css": self.o_icss.get(), "inline_js": self.o_ijs.get(),
            "strip_query": self.o_sq.get(), "same_domain_only": self.o_sd.get(),
            "minify_html": self.o_min.get(), "rewrite_css_urls": self.o_rcss.get(),
        }
        if self.ua_var.get().strip():
            opts["custom_ua"] = self.ua_var.get().strip()
        if self.proxy_var.get().strip():
            opts["proxy"] = self.proxy_var.get().strip()

        # Record history
        entry = {"url": url, "when": datetime.now().isoformat()}
        self.history = [h for h in self.history if isinstance(h, dict) and h.get("url") != url]
        self.history.insert(0, entry)
        self.history = self.history[:20]

        self.console.write("Starting: " + url)
        threading.Thread(target=self._run, args=(url, out, opts), daemon=True).start()

    def _run(self, url, out, opts):
        ok = self.cloner.clone(url, out, opts)
        self.root.after(0, self._done, ok)

    def _done(self, ok):
        self.running = False
        self.url_entry.configure(state="normal")
        self._disable_btn(self.stop_btn)
        self._enable_btn(self.start_btn, C["btnpb"], C["btnpf"], self._start)
        if ok:
            self.bar.set_value(100)
            self.prog_lbl.configure(text="Completed  -  " +
                                    str(len(self.cloner.amap)) + " assets downloaded")
            self.console.write("Clone completed successfully!", "ok")
        else:
            self.prog_lbl.configure(text="Failed / Cancelled")
            self.console.write("Clone failed or was cancelled.", "err")

    def _stop(self):
        self.cloner.cancel()
        self.console.write("Stopping...", "warn")
        self._disable_btn(self.stop_btn)
        self._enable_btn(self.start_btn, C["btnpb"], C["btnpf"], self._start)
        self.running = False
        self.url_entry.configure(state="normal")
        self.prog_lbl.configure(text="Cancelled")

    def _open(self):
        p = self.out_dir.get()
        if os.path.isdir(p):
            idx = os.path.join(p, "index.html")
            os.startfile(idx if os.path.isfile(idx) else p)
        else:
            messagebox.showwarning("Not Found", "Output directory does not exist.")

    def _export(self):
        src = self.out_dir.get()
        if not os.path.isdir(src) or not os.path.isfile(os.path.join(src, "index.html")):
            messagebox.showwarning("Nothing to Export", "Clone a site first.")
            return
        zp = filedialog.asksaveasfilename(
            defaultextension=".zip", filetypes=[("ZIP files", "*.zip")],
            initialfile="cloned_site.zip")
        if not zp:
            return
        try:
            with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(src):
                    for f in files:
                        fp = os.path.join(root, f)
                        zf.write(fp, os.path.relpath(fp, os.path.dirname(src)))
            self.console.write("Exported: " + zp, "ok")
            messagebox.showinfo("Export Complete", "Site exported to:\n" + zp)
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    def run(self):
        self.root.mainloop()


# ═══════════════════════════════════════════════════════════════
# ENTRY POINTS
# ═══════════════════════════════════════════════════════════════

def check_deps():
    missing = [d for d, m in [("requests", requests), ("beautifulsoup4", BeautifulSoup)]
               if m is None]
    if missing:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Missing Dependencies",
                             "Required packages:\n  " + "\n  ".join(missing) +
                             "\n\nInstall: pip install " + " ".join(missing))
        root.destroy()
        sys.exit(1)


def run_headless(url, out, opts):
    cloner = WebsiteCloner(
        log_cb=lambda msg, tag="info": print(
            "[" + datetime.now().strftime("%H:%M:%S") + "] " + msg))
    ok = cloner.clone(url, out, opts)
    if ok:
        print("\nDone! Output: " + out)
    else:
        print("\nFailed.")
    sys.exit(0 if ok else 1)


def main():
    cli = parse_cli()
    if cli["headless"] and cli["url"]:
        check_deps()
        out = cli["out"] or os.path.join(os.getcwd(), "cloned_site")
        opts = {"depth": cli["depth"], "workers": 8, "delay": 0.1, "timeout": 30,
                "clone_images": True, "clone_css": True, "clone_js": True,
                "clone_fonts": True, "strip_query": True, "same_domain_only": True,
                "rewrite_css_urls": True, "inline_css": False, "inline_js": False,
                "minify_html": False}
        run_headless(cli["url"], out, opts)
    else:
        check_deps()
        app = ClonerApp(cli_args=cli)
        app.run()


if __name__ == "__main__":
    main()
