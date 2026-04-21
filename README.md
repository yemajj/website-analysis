# website-analysis

Tooling for analyzing a website and producing a redesigned version.

## Crawler

`scripts/crawl.py` performs a BFS crawl from a target URL, same-domain only,
with robots.txt compliance and a configurable per-request delay.

### Run locally

```bash
pip install requests beautifulsoup4
python scripts/crawl.py --target https://www.ruttyandmorris.com --max-depth 3 --output site-analysis
```

Outputs written under `site-analysis/`:

- `original/` — saved HTML preserving URL paths (`/` → `index.html`, `/about/` → `about/index.html`)
- `original/assets/` — downloaded CSS, JS, images, fonts (hashed filenames)
- `sitemap.txt` — every URL visited
- `pages.csv` — `url, title, status, local_path`
- `assets.csv` — `url, local_path, content_type`
- `failures.txt` — URL + reason for anything that didn't fetch

The crawler prints a summary at the end (page count, asset count, titles)
and flags the target as a likely SPA if pages are almost empty server-side.

### Run on GitHub Actions

The sandbox used for interactive Claude sessions may not have outbound
access to arbitrary hosts. The workflow at `.github/workflows/site-crawl.yml`
runs the crawler on a GitHub-hosted runner (which has unrestricted internet)
and commits the results back to the branch that dispatched it.

Trigger it from the Actions tab → **Site Crawl** → **Run workflow**,
choosing the branch. Inputs default to ruttyandmorris.com, depth 3, 200 pages.
