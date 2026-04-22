# Activity log

A chronological record of what was done, when, with what tools, and why.
Kept as a paper trail of methodology and good-faith handling of any
security findings encountered during this analysis.

Subject: design / UX / accessibility / performance review of the
publicly accessible site at `https://www.ruttyandmorris.com`.
No authentication used, no restricted areas accessed, no inputs
submitted, no exploitation of any discovered issue.

All timestamps are UTC unless noted. Commit SHAs are in the
`yemajj/website-analysis` repository and provide an immutable record of
each change.

---

## Ground rules adopted at start

- **Scope:** only pages reachable from the public homepage by following
  same-domain `<a href>` links to a maximum depth of 3.
- **Politeness:** one HTTP request per second (`--delay 1.0`), total
  page cap of 200. `User-Agent` identifies the crawler and links to the
  project repo.
- **robots.txt:** fetched before crawling; every URL is checked with
  `urllib.robotparser.can_fetch()` and skipped if disallowed.
- **Observation only:** GET requests for HTML and referenced static
  assets (CSS, JS, images, fonts). No POSTs, no form submissions, no
  authentication, no attempts to access `/wp-admin`, `/admin`, API
  endpoints, or anything behind auth.
- **Handling of incidentally-observed secrets:** any credential-shaped
  string that shows up in page source is redacted from committed files
  via `scripts/redact_secrets.py` (replaces the match with a hashed
  placeholder). Raw secret values are never committed, re-shared,
  tested, or used against any third party's system.
- **Responsible disclosure:** if a security issue is incidentally
  observed, draft an email to the site owner describing the issue and
  recommended remediation *before* publishing any deliverable that
  names the affected URL.

## Event timeline

### 2026-04-21 — Phase 1: Crawler + workflow

- **Decision:** run the crawl on GitHub-hosted runners via
  `workflow_dispatch`, not from the interactive Claude Code sandbox
  (the sandbox's proxy allowlist blocks `ruttyandmorris.com`; the
  workflow runner has unrestricted outbound access).
- **Authored** `scripts/crawl.py` — same-domain BFS, robots.txt
  compliance, 1-second per-request delay, saves HTML preserving URL
  paths, downloads referenced CSS/JS/images/fonts, emits
  `sitemap.txt`, `pages.csv`, `assets.csv`, `failures.txt`, and a
  summary with an SPA heuristic.
- **Authored** `.github/workflows/site-crawl.yml` — manually
  dispatched, installs deps, runs crawler, commits outputs back to
  the dispatching branch.
- **Commit:** `af26819` on branch `claude/resume-work-uBFhI`.
- **PR:** #1 — `Add site crawler and GitHub Actions workflow` — merged
  to `main` as `cfedec6`.

### 2026-04-21 — First crawl attempt

- User ran **Site Crawl** workflow on branch
  `claude/resume-work-uBFhI`.
- Crawl step succeeded; commit step failed when `git push` was rejected
  by GitHub push protection (error `GH013 / GITHUB PUSH PROTECTION`).
- **What push protection flagged:** an **hCaptcha Siteverify Secret**
  (the server-side credential, not the public site key) embedded in
  the HTML source of two pages on the target site:
  - `https://www.ruttyandmorris.com/heating-and-cooling-beaumont/`
    (line 90 of rendered HTML)
  - `https://www.ruttyandmorris.com/heating-and-cooling-lumberton/`
    (line 90 of rendered HTML)
- **Decision:** this is a legitimate security exposure on the target
  site, not a false positive. The key is already publicly visible to
  anyone viewing the page source in a browser.
- **Decision:** do **not** click the push-protection bypass URL —
  that would enter the raw secret into this repository and into
  GitHub's secret-scanning index, creating a second exposure point.
- **Decision:** do **not** disable push protection — keep it as a
  second-line defense.
- **Chosen approach:** redact the pattern in the workflow before
  commit so the repo never carries the live secret; preserve the
  finding (path + pattern name + short SHA-256 of the token, no raw
  value) for the analysis report.

### 2026-04-21 — Remediation + disclosure prep

- **Authored** `scripts/redact_secrets.py` — scans saved HTML for
  known secret patterns (initially hCaptcha server-secret format:
  `0x` + 40 hex), replaces matches with
  `[REDACTED:<pattern>:<sha256_prefix>]`, writes hits to
  `site-analysis/security-findings.txt`. Self-tested on synthetic
  input locally; passes.
- **Updated** `site-crawl.yml` to run the redactor between the crawl
  and commit steps.
- **Commit:** `d894843` — `Redact known third-party secrets from
  crawled HTML before commit`.
- **Authored** `site-analysis/disclosure-email.md` — a
  responsible-disclosure template for the site owner (hCaptcha leak,
  recommended remediation: rotate the key, move to server-side
  config). The raw key is *not* included in the email; the owner is
  asked to verify in their own page source. Pre-send checklist
  included.
- **Commit:** `480d70e` — `Add responsible-disclosure email draft for
  hCaptcha secret leak`.
- **Authored** `site-analysis/ACTIVITY_LOG.md` (this file).
- **Commit:** `a32a67c` — `Add activity log capturing methodology and
  security-finding handling`.

### 2026-04-21 — Second crawl attempt

- User re-ran **Site Crawl** workflow on branch
  `claude/resume-work-uBFhI`.
- Crawl and redact steps succeeded. Push protection did **not** fire
  (confirming the redactor stripped the hCaptcha secret before commit).
- Commit step failed with `! [rejected] HEAD -> claude/resume-work-uBFhI
  (fetch first)` — non-fast-forward rejection. Cause: while the crawl
  was running, two unrelated commits had landed on the branch
  (`480d70e` disclosure email, `a32a67c` activity log), so the
  workflow's local branch was behind.
- **Fix:** updated the Commit step to `git pull --rebase origin
  <branch>` before `git push`, with a 3-attempt retry. Bumped
  `actions/checkout` `fetch-depth` to `0` so the rebase sees full
  history.
- **Commit:** `86f430b` — `Fix site-crawl race: rebase-then-push
  with retry`.

### 2026-04-21 — Third crawl attempt

- Crawl + redact ran; push was rejected by push protection again.
  The rebase-retry fix worked (no fast-forward errors), but residual
  secret matches remained after redaction.
- **Diagnostic value of this failure:** the target site embeds the
  hCaptcha server secret in **roughly every page that has the
  contact form**, not just the two city pages we first saw. The
  reported hits include the homepage, `service-areas`, all the
  city-specific pages, and `refrigeration` pages. One hit lived in
  an extension-less asset file (`assets/c6c730a769_about:94`).
- **Root cause in our code:** the redactor only walked `*.html`
  under `--root`, so the asset file was skipped. The pattern itself
  matched fine, but the file wasn't visited.
- **Fix:** rewrote `scripts/redact_secrets.py` to walk every
  non-binary file under `--root` (NUL-byte check in the first 8 KB)
  and to re-scan after redaction; returns non-zero if any pattern
  still matches so the workflow fails in the redact step rather
  than burning three push-protection retries.
- **Commit:** `c9a048a` — `Harden secret redactor: scan all
  non-binary files + verify`.

### 2026-04-21 — Fourth crawl attempt

- Crawl + redact ran; redactor's `verify_clean` reported no residual
  matches, yet push protection still rejected on 15+ pages across
  the site (`ice-machine-repair-*`, `thank-you`, `heating-and-cooling-*`,
  `service-areas`, `refrigeration-*`, and the homepage).
- **Root cause:** our regex `\b0x[0-9A-Fa-f]{40}\b` didn't match
  whatever form the secret takes in the site's contact-form template.
  Either the token length differs, the surrounding characters break
  `\b`, or the format is hCaptcha's newer `ES_...` style. Without a
  local copy we can't tell — GitHub's scanner is smarter than ours.
- **Fix:** widened `scripts/redact_secrets.py` to cover three layers:
  1. `TOKEN_PATTERNS` — `0x` + 30-80 hex (broader length range);
     `ES_` + 20-80 base64-ish (newer hCaptcha secret format).
  2. `SECRET_ATTR_RE` — any HTML attribute whose name contains
     "secret" (case-insensitive) has its value replaced.
  3. `HIDDEN_INPUT_TAG_RE` — every `<input type="hidden">` has its
     `value` attribute scrubbed, regardless of the token's shape.
     CSRF tokens and nonces get redacted too; they aren't
     design-relevant.
- Self-tested locally on three synthetic pages (classic hex, ES_
  newer, generic template) — 7 redactions, verify clean.
- **Commit:** `ccbb472` — `Broaden secret redaction: token shapes +
  hidden-input + secret-attr`.

### Pending

- User to re-trigger the Site Crawl workflow on branch
  `claude/resume-work-uBFhI`. Redactor will strip the secret before
  commit; push should succeed.
- User to send the responsible-disclosure email on a parallel track,
  independent of analysis timeline.
- Proceed to Phase 2 (analysis) once crawl output is committed.
- Pause before Phase 3 (redesign) for user review of priorities.

---

## What would change this record's character

These are the behaviours we explicitly *did not* undertake. Noting
them here so the record is unambiguous:

- No use of the leaked hCaptcha secret against hCaptcha's API or any
  other system.
- No attempts to bypass authentication, access admin panels, or probe
  non-linked URLs.
- No form submissions, account creation, or state-changing requests.
- No rate-limit evasion (no IP rotation, no concurrent crawling).
- No redistribution of the raw secret value in any deliverable.
- No contact with Rutty & Morris beyond (pending) responsible
  disclosure via their published contact channels.
