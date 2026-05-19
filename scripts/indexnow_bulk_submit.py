"""
One-time bulk submission of all site URLs to IndexNow.
Run from repo root: python scripts/indexnow_bulk_submit.py
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

HOST = "mybourbontrailplan.com"
SITEMAP_PATH = "sitemap.xml"

# Key is read from the verification file so rotating the key only requires
# updating that one file.
KEY_FILE = "da490b19460947faa108b25aa64e3f19.txt"


def load_key():
    try:
        with open(KEY_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"ERROR: Key file '{KEY_FILE}' not found at repo root.")
        sys.exit(1)


def parse_sitemap(path):
    if not os.path.exists(path):
        print(f"ERROR: '{path}' not found. Run from repo root.")
        sys.exit(1)
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        print(f"ERROR: Could not parse '{path}': {e}")
        sys.exit(1)
    root = tree.getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [loc.text.strip() for loc in root.findall(".//sm:loc", ns) if loc.text]
    return urls


def submit(urls, key):
    key_location = f"https://{HOST}/{KEY_FILE}"
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

    print(f"Submitting {len(urls)} URLs to IndexNow...")
    for u in urls:
        print(f"  {u}")
    print()

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            code = resp.status
    except urllib.error.HTTPError as e:
        code = e.code
    except urllib.error.URLError as e:
        print(f"Could not reach IndexNow API — submission skipped. ({e.reason})")
        return

    print(f"Response: HTTP {code}")
    if code == 200:
        print("Success — URLs queued for recrawl.")
    elif code == 400:
        print("Bad request. Request body:")
        print(json.dumps(payload, indent=2))
    elif code == 403:
        print("Forbidden — key not found or invalid. Verify the key file is publicly accessible:")
        print(f"  https://{HOST}/{KEY_FILE}")
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
    urls = parse_sitemap(SITEMAP_PATH)
    if not urls:
        print("No URLs found in sitemap. Nothing to submit.")
        sys.exit(0)
    print(f"Parsed {len(urls)} URLs from {SITEMAP_PATH}")
    submit(urls, key)


if __name__ == "__main__":
    main()
