#!/usr/bin/env python3
"""
Regenerates sitemap.xml by scanning root-level HTML files.

Exclusion rules (applied in order):
  1. Filenames containing spaces — Google Drive sync duplicates
  2. Explicit blocklist — shuttered/non-public pages
  3. Files with <meta name="robots" content="noindex"> anywhere in <head>

Priority/changefreq is assigned from an explicit table. Distillery profiles
not listed there default to 0.7/monthly; any other unlisted page defaults to
0.8/monthly so new guide pages are indexed conservatively without manual edits.

To promote a high-traffic distillery to 0.8 priority, add it to
HIGH_PRIORITY_DISTILLERIES below.

Run from repo root: python scripts\generate_sitemap.py
"""

import os
import re
import sys

BASE_URL = "https://mybourbontrailplan.com"
SITEMAP_FILE = "sitemap.xml"

# Pages that must never appear in the sitemap regardless of file content.
BLOCKLIST = {
    "distillery-garrard-county.html",  # shuttered distillery
    "distillery-barton-1792.html",     # not open to the public
    "email-signup-cta.html",           # code fragment, not a standalone page
}

# Explicit (priority, changefreq) for all known pages.
# New pages not listed here fall through to pattern-based defaults below.
PAGE_CONFIG = {
    "index.html":                                (1.0, "weekly"),
    "distilleries.html":                         (0.9, "weekly"),
    "guides.html":                               (0.8, "weekly"),
    "3-day-bourbon-trail-itinerary.html":        (0.9, "monthly"),
    "trip-builder.html":                         (0.9, "monthly"),
    "bourbon-trail-booking-guide.html":          (0.9, "monthly"),
    "where-to-stay-bourbon-trail.html":          (0.9, "monthly"),
    "bourbon-trail-budget-guide.html":           (0.9, "monthly"),
    "bourbon-trail-transportation-guide.html":   (0.9, "monthly"),
    "bourbon-trail-bachelor-party-guide.html":   (0.9, "monthly"),
    "map.html":                                  (0.8, "monthly"),
    "eat-and-drink-bourbon-trail.html":          (0.8, "monthly"),
    "buffalo-trace-gift-shop-guide.html":        (0.8, "monthly"),
    "kentucky-bourbonfest.html":                 (0.8, "monthly"),
    "best-time-to-visit-bourbon-trail.html":     (0.8, "monthly"),
    "bourbon-trail-non-bourbon-drinkers.html":   (0.8, "monthly"),
    "louisville-whiskey-row-walking-guide.html": (0.8, "monthly"),
    "about.html":                                (0.5, "monthly"),
    "contact.html":                              (0.5, "monthly"),
}

# High-traffic distillery profiles that warrant 0.8 instead of the default 0.7.
# Add new profiles here once they establish meaningful search traffic.
HIGH_PRIORITY_DISTILLERIES = {
    "distillery-angels-envy.html",
    "distillery-buffalo-trace.html",
    "distillery-evan-williams.html",
    "distillery-four-roses.html",
    "distillery-heaven-hill.html",
    "distillery-jim-beam.html",
    "distillery-log-still.html",
    "distillery-makers-mark.html",
    "distillery-old-forester.html",
    "distillery-preservation.html",
    "distillery-wild-turkey.html",
    "distillery-woodford-reserve.html",
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


def get_config(filename):
    if filename in PAGE_CONFIG:
        return PAGE_CONFIG[filename]
    if filename in HIGH_PRIORITY_DISTILLERIES:
        return (0.8, "monthly")
    if filename.startswith("distillery-"):
        return (0.7, "monthly")
    return (0.8, "monthly")


def to_url(filename):
    return f"{BASE_URL}/" if filename == "index.html" else f"{BASE_URL}/{filename}"


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sitemap_path = os.path.join(repo_root, SITEMAP_FILE)

    included = []
    skipped = []

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

    # Sort: highest priority first; alpha within each priority tier
    included.sort(key=lambda n: (-get_config(n)[0], n))

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for name in included:
        priority, changefreq = get_config(name)
        lines.append(
            f'  <url>'
            f'<loc>{to_url(name)}</loc>'
            f'<changefreq>{changefreq}</changefreq>'
            f'<priority>{priority:.1f}</priority>'
            f'</url>'
        )
    lines.append("</urlset>")

    output = "\n".join(lines) + "\n"
    with open(sitemap_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(output)

    print(f"sitemap.xml written — {len(included)} URLs included, {len(skipped)} excluded")
    print()
    for name in included:
        priority, _ = get_config(name)
        print(f"  {priority:.1f}  {to_url(name)}")

    if skipped:
        print()
        print("Excluded:")
        for name, reason in skipped:
            print(f"  [{reason}]  {name}")


if __name__ == "__main__":
    main()
