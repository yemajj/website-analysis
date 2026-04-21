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

# --- Token-shape patterns -------------------------------------------------
# Values that look like credentials regardless of surrounding HTML.
# hCaptcha secret keys have historically been 0x + 40 hex (Ethereum-address
# shaped); newer keys are ES_ prefixed. We go broader than strictly needed
# because our last run missed the template-embedded value — belt-and-braces.
TOKEN_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # 0x + 30-80 hex (covers hCaptcha classic, including any odd length)
    ("hex0x_token", re.compile(r"0[xX][0-9A-Fa-f]{30,80}")),
    # ES_ + base64-ish (hCaptcha new-style secret)
    ("es_prefixed_secret", re.compile(r"\bES_[A-Za-z0-9_\-]{20,80}\b")),
]

# --- Structural scrubbers -------------------------------------------------
# Targets the *structure* of HTML where secrets commonly land, independent
# of the token's exact shape. Not in TOKEN_PATTERNS because they mutate the
# surrounding markup rather than a raw substring.

# Any attribute whose NAME contains "secret" (case-insensitive).
# Matches attribute name, '=', quoted value. Captures name+opening-quote
# and closing-quote so we can replace just the value.
SECRET_ATTR_RE = re.compile(
    r"""
    (
        [A-Za-z_][A-Za-z0-9_:\-]*secret[A-Za-z0-9_:\-]*
        \s*=\s*
        ["']
    )
    [^"']*
    (["'])
    """,
    re.IGNORECASE | re.VERBOSE,
)

# <input type="hidden" ...> full open tag.
HIDDEN_INPUT_TAG_RE = re.compile(
    r"""<input\b[^>]*\btype\s*=\s*["']hidden["'][^>]*>""",
    re.IGNORECASE,
)

# value="..." or value='...' within a single tag.
VALUE_ATTR_RE = re.compile(
    r"""(\bvalue\s*=\s*)(?:"[^"]*"|'[^']*')""",
    re.IGNORECASE,
)


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


def _token_sub(findings: list[tuple[str, str]], name: str):
    def _sub(m: re.Match[str]) -> str:
        token = m.group(0)
        digest = hashlib.sha256(token.encode()).hexdigest()[:16]
        findings.append((name, digest))
        return f"[REDACTED:{name}:{digest}]"
    return _sub


def _secret_attr_sub(findings: list[tuple[str, str]]):
    def _sub(m: re.Match[str]) -> str:
        attr_prefix = m.group(1)  # 'name="' or similar
        close_quote = m.group(2)
        full = m.group(0)
        # Hash the full match (attribute + value) so each redaction is
        # distinguishable; we don't isolate the raw value because the
        # regex captures don't cleanly separate it from quotes.
        digest = hashlib.sha256(full.encode()).hexdigest()[:16]
        findings.append(("secret_attr", digest))
        return f"{attr_prefix}[REDACTED:secret_attr:{digest}]{close_quote}"
    return _sub


def _hidden_input_sub(findings: list[tuple[str, str]]):
    def _sub(m: re.Match[str]) -> str:
        tag = m.group(0)
        digest = hashlib.sha256(tag.encode()).hexdigest()[:16]

        # Replace the value="..." inside this tag; leave other attrs alone.
        def _val_sub(vm: re.Match[str]) -> str:
            return f'{vm.group(1)}"[REDACTED:hidden_input:{digest}]"'

        new_tag, n = VALUE_ATTR_RE.subn(_val_sub, tag)
        if n:
            findings.append(("hidden_input", digest))
        return new_tag
    return _sub


def redact_file(path: Path) -> list[tuple[str, str]]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    findings: list[tuple[str, str]] = []
    new_text = text

    for name, pat in TOKEN_PATTERNS:
        new_text = pat.sub(_token_sub(findings, name), new_text)

    new_text = SECRET_ATTR_RE.sub(_secret_attr_sub(findings), new_text)
    new_text = HIDDEN_INPUT_TAG_RE.sub(_hidden_input_sub(findings), new_text)

    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return findings


def verify_clean(root: Path) -> list[tuple[Path, str, int]]:
    """Return (path, pattern_name, count) for any residual matches.

    Only runs the token-shape patterns — structural scrubbers are
    idempotent and their absence-of-match isn't meaningful to check.
    """
    leaks: list[tuple[Path, str, int]] = []
    for p in iter_text_files(root):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for name, pat in TOKEN_PATTERNS:
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
            f.write("# Each line: path\\tpattern_name\\tsha256_prefix\n")
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

    print("Verification: no residual token-shape matches under", args.root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
