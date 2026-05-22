#!/usr/bin/env python3
"""
Three schema fixes:
1. Remove review block from all TouristAttraction schemas
2. Convert bare dates to ISO 8601 with Eastern offset
3. Standardize author/publisher to Organization "Bourbon Trail Planner"
"""

import os, re, json, glob

BASE_DIR = r"C:\Users\cowde\Desktop\mybourbontrailplan"

ORG = {"@type": "Organization", "name": "Bourbon Trail Planner"}

DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')

def fix_block(data):
    """Apply all three fixes to a parsed JSON-LD object. Returns (data, changed)."""
    changed = False

    # Fix 1: Remove review from TouristAttraction
    if data.get('@type') == 'TouristAttraction' and 'review' in data:
        del data['review']
        changed = True

    # Fix 2: Convert bare dates to ISO 8601
    for field in ('datePublished', 'dateModified'):
        val = data.get(field)
        if isinstance(val, str) and DATE_RE.match(val):
            data[field] = f"{val}T00:00:00-05:00"
            changed = True

    # Fix 3: Normalize author and publisher to Organization
    if 'author' in data and data['author'] != ORG:
        data['author'] = ORG
        changed = True

    if 'publisher' in data and data['publisher'] != ORG:
        data['publisher'] = ORG
        changed = True

    return data, changed

BLOCK_RE = re.compile(
    r'(<script type="application/ld\+json">)\s*(.*?)\s*(</script>)',
    re.DOTALL
)

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    file_changed = False

    def replacer(m):
        nonlocal file_changed
        prefix, json_str, suffix = m.group(1), m.group(2), m.group(3)
        try:
            data = json.loads(json_str.strip())
        except json.JSONDecodeError as e:
            print(f"  JSON error in {os.path.basename(filepath)}: {e}")
            return m.group(0)

        data, changed = fix_block(data)
        if changed:
            file_changed = True
            new_json = json.dumps(data, indent=2, ensure_ascii=False)
            return f"{prefix}\n{new_json}\n{suffix}"
        return m.group(0)

    new_content = BLOCK_RE.sub(replacer, content)

    if file_changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
    return file_changed

def main():
    html_files = [
        f for f in glob.glob(os.path.join(BASE_DIR, '*.html'))
        if ' ' not in os.path.basename(f)
    ]

    updated = 0
    for filepath in sorted(html_files):
        if process_file(filepath):
            print(f"  Fixed: {os.path.basename(filepath)}")
            updated += 1

    print(f"\n{updated} files updated.")

    # Validate all blocks still parse
    errors = 0
    for filepath in sorted(html_files):
        content = open(filepath, encoding='utf-8').read()
        for m in BLOCK_RE.finditer(content):
            try:
                json.loads(m.group(2).strip())
            except json.JSONDecodeError as e:
                print(f"  VALIDATION ERROR {os.path.basename(filepath)}: {e}")
                errors += 1
    if errors == 0:
        print("All JSON-LD blocks valid.")
    else:
        print(f"{errors} validation errors — check above.")

if __name__ == '__main__':
    main()
