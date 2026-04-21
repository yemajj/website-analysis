#!/usr/bin/env python3
"""BFS crawler for static site analysis.

- Starts at --target, follows same-domain links up to --max-depth
- Saves HTML under <output>/original/ preserving URL paths
- Downloads referenced CSS/JS/images/fonts under <output>/original/assets/
- Logs discovered URLs to <output>/sitemap.txt
- Writes page + asset manifests (pages.csv, assets.csv) and a failures log
- Respects robots.txt and rate-limits with --delay (default 1.0s)
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import logging
import sys
import time
import urllib.robotparser
from collections import deque
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

USER_AGENT = "SiteAnalysisBot/1.0 (+https://github.com/yemajj/website-analysis)"
ASSET_TAG_ATTRS = [
    ("link", "href"),
    ("script", "src"),
    ("img", "src"),
    ("source", "src"),
    ("source", "srcset"),
    ("img", "srcset"),
]


def normalize_host(netloc: str) -> str:
    return netloc.lower().removeprefix("www.")


def same_domain(a: str, b: str) -> bool:
    return normalize_host(urlparse(a).netloc) == normalize_host(urlparse(b).netloc)


def safe_page_path(url: str) -> str:
    """Map a page URL to a local relative path under original/."""
    parsed = urlparse(url)
    path = parsed.path or "/"
    if path.endswith("/"):
        local = path.strip("/") + "/index.html" if path != "/" else "index.html"
    else:
        name = Path(path).name
        if "." not in name:
            local = path.strip("/") + "/index.html"
        else:
            local = path.strip("/")
    if parsed.query:
        # Disambiguate querystring pages
        qhash = hashlib.md5(parsed.query.encode()).hexdigest()[:8]
        p = Path(local)
        local = str(p.with_name(f"{p.stem}__{qhash}{p.suffix}"))
    return local


def asset_local_name(url: str) -> str:
    parsed = urlparse(url)
    original = Path(parsed.path).name or "asset"
    digest = hashlib.md5(url.encode()).hexdigest()[:10]
    return f"{digest}_{original}"


def extract_srcset_urls(value: str) -> list[str]:
    out = []
    for part in value.split(","):
        token = part.strip().split(" ", 1)[0]
        if token:
            out.append(token)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", required=True, help="Starting URL")
    ap.add_argument("--max-depth", type=int, default=3)
    ap.add_argument("--output", type=Path, default=Path("site-analysis"))
    ap.add_argument("--delay", type=float, default=1.0, help="Seconds between requests")
    ap.add_argument("--timeout", type=float, default=20.0)
    ap.add_argument("--max-pages", type=int, default=200, help="Hard cap on pages")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log = logging.getLogger("crawler")

    out = args.output
    orig = out / "original"
    assets_dir = orig / "assets"
    orig.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    target = args.target.rstrip("/")
    parsed_target = urlparse(target)
    robots_url = f"{parsed_target.scheme}://{parsed_target.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        log.info("Loaded robots.txt from %s", robots_url)
    except Exception as e:
        log.warning("Could not load robots.txt (%s) — allowing all", e)

    def allowed(url: str) -> bool:
        try:
            return rp.can_fetch(USER_AGENT, url)
        except Exception:
            return True

    seen_pages: set[str] = set()
    seen_assets: set[str] = set()
    queue: deque[tuple[str, int]] = deque([(target, 0)])
    pages_data: list[tuple[str, str, int, str]] = []
    assets_data: list[tuple[str, str, str]] = []  # url, local_path, content_type
    failures: list[tuple[str, str]] = []
    spa_hint = False

    def fetch_asset(url: str) -> None:
        if url in seen_assets:
            return
        seen_assets.add(url)
        if not allowed(url):
            failures.append((url, "asset disallowed by robots.txt"))
            return
        time.sleep(args.delay)
        try:
            r = session.get(url, timeout=args.timeout)
        except Exception as e:
            failures.append((url, f"asset error: {e}"))
            return
        if r.status_code != 200:
            failures.append((url, f"asset HTTP {r.status_code}"))
            return
        name = asset_local_name(url)
        (assets_dir / name).write_bytes(r.content)
        assets_data.append((url, f"assets/{name}", r.headers.get("content-type", "")))

    while queue and len(pages_data) < args.max_pages:
        url, depth = queue.popleft()
        url, _ = urldefrag(url)
        if url in seen_pages:
            continue
        seen_pages.add(url)

        if not allowed(url):
            log.info("SKIP robots: %s", url)
            failures.append((url, "disallowed by robots.txt"))
            continue

        log.info("GET [d=%d] %s", depth, url)
        try:
            resp = session.get(url, timeout=args.timeout, allow_redirects=True)
        except Exception as e:
            log.warning("  fail: %s", e)
            failures.append((url, str(e)))
            continue

        if resp.status_code != 200:
            log.warning("  status=%s", resp.status_code)
            failures.append((url, f"HTTP {resp.status_code}"))
            continue

        ctype = resp.headers.get("content-type", "").lower()
        if "html" not in ctype:
            failures.append((url, f"non-HTML ({ctype})"))
            continue

        html = resp.text
        soup = BeautifulSoup(html, "html.parser")

        # SPA heuristic: very little body text + a known mount point
        body = soup.body
        body_text = body.get_text(strip=True) if body else ""
        if len(body_text) < 200 and (
            soup.find(id="root") or soup.find(id="app") or soup.find(id="__next")
        ):
            spa_hint = True

        title_tag = soup.find("title")
        title = (title_tag.get_text().strip() if title_tag else "") or "(no title)"

        local_path = safe_page_path(url)
        dest = orig / local_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")
        pages_data.append((url, title, resp.status_code, local_path))

        # Internal link discovery
        for a in soup.find_all("a", href=True):
            absolute = urljoin(url, a["href"])
            absolute, _ = urldefrag(absolute)
            if absolute.startswith(("mailto:", "tel:", "javascript:", "data:")):
                continue
            if not absolute.startswith(("http://", "https://")):
                continue
            if not same_domain(target, absolute):
                continue
            if absolute in seen_pages:
                continue
            if depth + 1 > args.max_depth:
                continue
            queue.append((absolute, depth + 1))

        # Asset discovery
        for tag_name, attr in ASSET_TAG_ATTRS:
            for el in soup.find_all(tag_name):
                val = el.get(attr)
                if not val:
                    continue
                refs = extract_srcset_urls(val) if attr == "srcset" else [val]
                for ref in refs:
                    absolute = urljoin(url, ref)
                    absolute, _ = urldefrag(absolute)
                    if not absolute.startswith(("http://", "https://")):
                        continue
                    if absolute.startswith("data:"):
                        continue
                    fetch_asset(absolute)

        time.sleep(args.delay)

    # Outputs
    (out / "sitemap.txt").write_text(
        "\n".join(sorted(seen_pages)) + "\n", encoding="utf-8"
    )

    with (out / "pages.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "title", "status", "local_path"])
        w.writerows(pages_data)

    with (out / "assets.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "local_path", "content_type"])
        w.writerows(assets_data)

    with (out / "failures.txt").open("w", encoding="utf-8") as f:
        for url, reason in failures:
            f.write(f"{url}\t{reason}\n")

    print()
    print("=== CRAWL SUMMARY ===")
    print(f"Target:       {target}")
    print(f"Pages saved:  {len(pages_data)}")
    print(f"Assets saved: {len(assets_data)}")
    print(f"Failures:     {len(failures)}")
    if spa_hint:
        print()
        print("WARNING: Target looks JS-rendered (SPA).")
        print("  Body text is sparse and a root mount node is present.")
        print("  Re-run analysis with Playwright to capture rendered DOM.")
    print()
    print("Page titles:")
    for url, title, _, _ in pages_data:
        print(f"  - {title}  [{url}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
