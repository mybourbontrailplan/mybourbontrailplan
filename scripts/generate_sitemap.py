#!/usr/bin/env python3
r"""
Regenerates sitemap.xml by scanning root-level HTML files.

Exclusion rules (applied in order):
  1. Filenames containing spaces — Google Drive sync duplicates
  2. Explicit blocklist — shuttered/non-public pages
  3. Files with <meta name="robots" content="noindex"> anywhere in <head>

URLs are the extensionless clean form (https://mybourbontrailplan.com/map),
matching the canonical on every page. Never emit the .html form: those URLs
301 to the clean form, and a sitemap full of redirects slows re-crawling at
exactly the wrong moment.

Every entry carries <lastmod>, which is the whole point of the file. Google
did not re-read this sitemap between 3 April and 2 September 2026 because it
carried no lastmod at all, only changefreq and priority, both of which Google
ignores. Those two fields are deliberately absent now; do not add them back.
check_site.py fails if they reappear.

lastmod is the file's last git commit date, except for files with uncommitted
changes, which get today. That ordering matters: you regenerate before you
commit, so a page edited in the pending commit must not report the previous
commit's date.

Run from repo root: python scripts\generate_sitemap.py
"""

import os
import re
import subprocess
from datetime import date

BASE_URL = "https://mybourbontrailplan.com"
SITEMAP_FILE = "sitemap.xml"

# Pages that must never appear in the sitemap regardless of file content.
BLOCKLIST = {
    "distillery-garrard-county.html",  # shuttered distillery
    "distillery-barton-1792.html",     # not open to the public
    "email-signup-cta.html",           # code fragment, not a standalone page
}

_NOINDEX_RE = re.compile(
    r'<meta\b[^>]*\bname=["\']robots["\'][^>]*\bcontent=["\'][^"\']*noindex',
    re.IGNORECASE,
)


def has_noindex(path):
    """Return True if the file's <head> contains a noindex robots meta tag."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            head = fh.read(8192)
        return bool(_NOINDEX_RE.search(head))
    except OSError:
        return False


def to_url(filename):
    """Repo filename -> its canonical clean URL."""
    if filename == "index.html":
        return f"{BASE_URL}/"
    return f"{BASE_URL}/{filename[:-5]}"


def _git(args, cwd):
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True,
                          text=True).stdout


def build_lastmod(repo_root, names):
    """Map filename -> YYYY-MM-DD. Uncommitted edits report today."""
    today = date.today().isoformat()
    dirty = set()
    for line in _git(["status", "--porcelain", "--"] + names, repo_root).splitlines():
        dirty.add(os.path.basename(line[3:].strip().strip('"')))

    out = {}
    for name in names:
        if name in dirty:
            out[name] = today
            continue
        stamp = _git(["log", "-1", "--format=%cs", "--", name], repo_root).strip()
        out[name] = stamp or today
    return out


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sitemap_path = os.path.join(repo_root, SITEMAP_FILE)

    included, skipped = [], []
    for name in sorted(os.listdir(repo_root)):
        if not name.endswith(".html"):
            continue
        if " " in name:
            skipped.append((name, "Drive duplicate"))
            continue
        if name in BLOCKLIST:
            skipped.append((name, "blocklisted"))
            continue
        path = os.path.join(repo_root, name)
        if not os.path.isfile(path):
            continue
        if has_noindex(path):
            skipped.append((name, "noindex"))
            continue
        included.append(name)

    # Homepage first, then alphabetical. Ordering carries no ranking meaning;
    # it just keeps the file readable in a diff.
    included.sort(key=lambda n: (n != "index.html", n))

    lastmod = build_lastmod(repo_root, included)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for name in included:
        lines.append(
            f'  <url>'
            f'<loc>{to_url(name)}</loc>'
            f'<lastmod>{lastmod[name]}</lastmod>'
            f'</url>'
        )
    lines.append("</urlset>")

    with open(sitemap_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"sitemap.xml written - {len(included)} URLs included, {len(skipped)} excluded")
    print()
    for name in included:
        print(f"  {lastmod[name]}  {to_url(name)}")
    if skipped:
        print()
        print("Excluded:")
        for name, reason in skipped:
            print(f"  [{reason}]  {name}")


if __name__ == "__main__":
    main()
