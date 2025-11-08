#!/usr/bin/env python3
"""
Simple checker to prevent committing legacy brand tokens.

Usage:
  python scripts/check_no_legacy_brand.py [--staged]

If --staged is passed, the script scans staged files only (recommended as a pre-commit hook).
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in [r"market\s*wiz", r"marketwiz"]
]
# Relative paths (POSIX-style) to exclude from scanning (the checker and hook files themselves)
EXCLUDE_RELATIVE = {
    "scripts/check_no_legacy_brand.py",
    ".githooks/pre-commit",
    "README-dev.md",
}


def files_to_check(staged_only: bool):
    if staged_only:
        # get staged files
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], stdout=subprocess.PIPE, cwd=ROOT
        )
        paths = [p.strip() for p in out.stdout.decode().splitlines() if p.strip()]
    else:
        paths = [str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file()]
    # filter binary files (simple heuristic) and exclude hook/script paths
    result = []
    for p in paths:
        # normalize
        if p.endswith(
            (".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff2", ".woff", ".eot", ".pdf")
        ):
            continue
        # relative path normalized
        rel = p.replace("\\", "/")
        # skip files we intentionally exclude
        if rel in EXCLUDE_RELATIVE or any(
            rel.startswith(prefix) for prefix in ("scripts/", ".githooks/")
        ):
            continue
        # skip binary by suffix
        full = ROOT / p
        result.append(full)
    return result


def check_file(path: Path):
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return []
    matches = []
    for i, line in enumerate(text.splitlines(), start=1):
        for pat in LEGACY_PATTERNS:
            if pat.search(line):
                matches.append((i, line.strip()))
    return matches


def main():
    staged = "--staged" in sys.argv
    files = files_to_check(staged_only=staged)
    found = False
    for f in files:
        rel = f.relative_to(ROOT)
        matches = check_file(f)
        if matches:
            found = True
            print(f"Legacy token found in {rel}:")
            for lineno, line in matches:
                print(f"  {lineno}: {line}")
            print()
    if found:
        print(
            "Commit blocked: remove or update legacy brand tokens (e.g. 'marketwiz', 'Market Wiz'). Consider replacing with 'crosspostme'."
        )
        sys.exit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
