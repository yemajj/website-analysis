#!/usr/bin/env python3
"""Redact known secret patterns from saved HTML before committing.

The target site may inadvertently expose credentials in page source. We
never want those to land in git — push protection would block them, and
even if it didn't, committing someone else's live secret creates a second
exposure point. This script replaces matches with a deterministic
placeholder and logs each hit (path + pattern name + short SHA-256 of the
token) to security-findings.txt for the analysis report.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

# hCaptcha secret keys are 0x followed by 40 hex chars.
# (Site keys use different formats and are safe to commit.)
PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("hcaptcha_siteverify_secret", re.compile(r"\b0x[0-9A-Fa-f]{40}\b")),
]


def redact_file(path: Path) -> list[tuple[str, str]]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    findings: list[tuple[str, str]] = []
    new_text = text

    for name, pat in PATTERNS:
        def _sub(m: re.Match[str], _name: str = name) -> str:
            token = m.group(0)
            digest = hashlib.sha256(token.encode()).hexdigest()[:16]
            findings.append((_name, digest))
            return f"[REDACTED:{_name}:{digest}]"

        new_text = pat.sub(_sub, new_text)

    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path("site-analysis/original"))
    ap.add_argument("--log", type=Path, default=Path("site-analysis/security-findings.txt"))
    args = ap.parse_args()

    if not args.root.exists():
        print(f"root does not exist: {args.root}", file=sys.stderr)
        return 0  # nothing to do; let the pipeline continue

    all_findings: list[tuple[Path, str, str]] = []
    for p in args.root.rglob("*.html"):
        for name, digest in redact_file(p):
            all_findings.append((p, name, digest))

    args.log.parent.mkdir(parents=True, exist_ok=True)
    with args.log.open("w", encoding="utf-8") as f:
        if all_findings:
            f.write("# Secrets redacted from crawled HTML\n")
            f.write("# Each line: path\\tpattern_name\\tsha256_prefix (of the original token)\n")
            f.write("# The placeholder in-file is [REDACTED:pattern_name:sha256_prefix].\n")
            for path, name, digest in all_findings:
                f.write(f"{path}\t{name}\t{digest}\n")
        else:
            f.write("# No secrets redacted.\n")

    print(f"Redacted {len(all_findings)} occurrences across HTML files.")
    if all_findings:
        print(f"See: {args.log}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
