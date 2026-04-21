#!/usr/bin/env python3
"""Redact known secret patterns from crawled output before committing.

Walks all non-binary files under --root, applies redaction patterns,
logs hits to --log, and then re-scans to verify nothing remains. Exits
non-zero if any pattern still matches after redaction so the workflow
fails loudly before push protection rejects the commit.

Placeholder format in-file: [REDACTED:<pattern_name>:<sha256_prefix>].
The log stores the same mapping so findings are preserved for the
analysis report without the raw secret entering git.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

# hCaptcha server-side (Siteverify) secrets are 0x + 40 hex chars.
# Public site keys use a different format and are safe to commit.
PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("hcaptcha_siteverify_secret", re.compile(r"\b0x[0-9A-Fa-f]{40}\b")),
]


def is_binary(path: Path) -> bool:
    """Cheap binary check: presence of NUL in first 8 KB."""
    try:
        with path.open("rb") as f:
            chunk = f.read(8192)
    except Exception:
        return True
    return b"\x00" in chunk


def iter_text_files(root: Path):
    for p in root.rglob("*"):
        if p.is_file() and not is_binary(p):
            yield p


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


def verify_clean(root: Path) -> list[tuple[Path, str, int]]:
    """Return (path, pattern_name, count) for any residual matches."""
    leaks: list[tuple[Path, str, int]] = []
    for p in iter_text_files(root):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for name, pat in PATTERNS:
            n = len(pat.findall(text))
            if n:
                leaks.append((p, name, n))
    return leaks


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path("site-analysis/original"))
    ap.add_argument("--log", type=Path, default=Path("site-analysis/security-findings.txt"))
    args = ap.parse_args()

    if not args.root.exists():
        print(f"root does not exist: {args.root}", file=sys.stderr)
        return 0

    all_findings: list[tuple[Path, str, str]] = []
    for p in iter_text_files(args.root):
        for name, digest in redact_file(p):
            all_findings.append((p, name, digest))

    args.log.parent.mkdir(parents=True, exist_ok=True)
    with args.log.open("w", encoding="utf-8") as f:
        if all_findings:
            f.write("# Secrets redacted from crawled output\n")
            f.write("# Each line: path\\tpattern_name\\tsha256_prefix (of the original token)\n")
            f.write("# Placeholders in-file are [REDACTED:pattern_name:sha256_prefix].\n")
            for path, name, digest in all_findings:
                f.write(f"{path}\t{name}\t{digest}\n")
        else:
            f.write("# No secrets redacted.\n")

    print(f"Redacted {len(all_findings)} occurrences across non-binary files.")

    leaks = verify_clean(args.root)
    if leaks:
        print("FAILED: residual secret matches after redaction:", file=sys.stderr)
        for path, name, count in leaks:
            print(f"  {path}\t{name}\tcount={count}", file=sys.stderr)
        return 1

    print("Verification: no residual matches under", args.root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
