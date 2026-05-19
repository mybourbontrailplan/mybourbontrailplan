"""
Per-deploy incremental IndexNow submission.
Detects HTML files changed in the latest git commit and submits their URLs.
Run from repo root after deploying: python scripts/indexnow_submit_changed.py
"""

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request

HOST = "mybourbontrailplan.com"
BASE_URL = f"https://{HOST}"

# Key is read from the verification file so rotating the key only requires
# updating that one file.
KEY_FILE = "da490b19460947faa108b25aa64e3f19.txt"

# Files that are never submitted even if they change
SKIP_FILES = {KEY_FILE, "sitemap.xml", "robots.txt", "CLAUDE.md"}


def load_key():
    try:
        with open(KEY_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"ERROR: Key file '{KEY_FILE}' not found at repo root.")
        sys.exit(1)


def get_changed_files():
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        # HEAD~1 doesn't exist (first commit on the branch)
        print(f"WARNING: Could not diff HEAD~1..HEAD: {e.stderr.strip()}")
        print("Skipping incremental submission — run indexnow_bulk_submit.py for a full seed.")
        return []


def to_url(filename):
    """Convert a repo filename to its canonical URL."""
    if filename == "index.html":
        return f"{BASE_URL}/"
    return f"{BASE_URL}/{filename}"


def submit(urls, key):
    key_location = f"{BASE_URL}/{KEY_FILE}"
    payload = {
        "host": HOST,
        "key": key,
        "keyLocation": key_location,
        "urlList": urls,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.indexnow.org/IndexNow",
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )

    print(f"Submitting {len(urls)} URL(s) to IndexNow:")
    for u in urls:
        print(f"  {u}")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            code = resp.status
    except urllib.error.HTTPError as e:
        code = e.code
    except urllib.error.URLError as e:
        print(f"Could not reach IndexNow API — submission skipped. ({e.reason})")
        return

    print(f"Response: HTTP {code}")
    if code in (200, 202):
        print("Success — URLs queued for recrawl.")
    elif code == 400:
        print("Bad request. Request body:")
        print(json.dumps(payload, indent=2))
    elif code == 403:
        print("Forbidden — key not found or invalid. Verify:")
        print(f"  {BASE_URL}/{KEY_FILE}")
    elif code == 422:
        print("Unprocessable — URLs don't match the host or key schema mismatch.")
    elif code == 429:
        print("Rate limited. Retrying in 30 seconds...")
        time.sleep(30)
        submit(urls, key)
    else:
        print(f"Unexpected response code: {code}")


def main():
    key = load_key()
    changed = get_changed_files()

    # TODO: handle deleted files (currently skipped; deleted URLs would 404 on recrawl)
    html_files = [
        f for f in changed
        if f.endswith(".html") and f not in SKIP_FILES
    ]

    if not html_files:
        print("No HTML changes to submit.")
        sys.exit(0)

    urls = [to_url(f) for f in html_files]
    submit(urls, key)


if __name__ == "__main__":
    main()
