#!/usr/bin/env python3
r"""
Regenerates the page-redirect block in _redirects.

Every root-level .html file gets a forced 301 to its clean URL, so each page
is served at exactly one indexable address.

Two details are load-bearing:

  * The trailing "!" (force) is REQUIRED. Netlify skips a redirect that
    shadows a file that exists on disk unless the rule is forced, and every
    one of these shadows a real .html file. Without the "!" the rules are
    silently ignored and both URLs keep returning 200.

  * Explicit per-page rules, not a wildcard. Netlify's splats match whole
    path segments, so a suffix pattern like /*.html does not reliably fire.
    A generated list is longer but behaves predictably.

The hand-written header above the marker (the /m/* QR short links) is
preserved verbatim. Those paths are printed on cards in guest binders and can
never be removed or renamed.

Run from repo root: python scripts\generate_redirects.py
"""

import os
import sys

REDIRECTS_FILE = "_redirects"
BEGIN = "# --- BEGIN GENERATED PAGE REDIRECTS (python scripts\\generate_redirects.py) ---"
END = "# --- END GENERATED PAGE REDIRECTS ---"

HEADER_NOTE = """
# Clean-URL migration, September 2026. Each page is served at its
# extensionless URL; the .html form 301s here so it cannot be indexed
# separately. Regenerate with the script above after adding or removing a
# page, then commit. check_site.py fails if this block is out of date.
"""


def rules_for(names):
    width = max(len(n) for n in names) + 6
    out = []
    for name in sorted(names):
        src = f"/{name}"
        dst = "/" if name == "index.html" else f"/{name[:-5]}"
        out.append(f"{src.ljust(width)}{dst.ljust(width)}301!")
    return out


def build(repo_root):
    names = sorted(n for n in os.listdir(repo_root)
                   if n.endswith(".html") and " " not in n
                   and os.path.isfile(os.path.join(repo_root, n)))
    body = "\n".join(rules_for(names))
    return names, f"{BEGIN}\n{HEADER_NOTE}\n{body}\n\n{END}\n"


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(repo_root, REDIRECTS_FILE)
    current = open(path, encoding="utf-8").read() if os.path.exists(path) else ""

    names, block = build(repo_root)

    if BEGIN in current:
        head = current.split(BEGIN)[0]
        tail = current.split(END)[1] if END in current else ""
    else:
        head, tail = current.rstrip() + "\n\n", ""

    out = head + block + tail
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)

    print(f"_redirects written - {len(names)} page rules (301, forced)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
