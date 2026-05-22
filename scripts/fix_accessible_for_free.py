#!/usr/bin/env python3
"""
Add isAccessibleForFree to any TouristAttraction schema that's missing it.

Most distilleries charge for tours (isAccessibleForFree: false).
Known exceptions (free entry) are listed in FREE_SLUGS.
"""

import os, re, json, glob

BASE_DIR = r"C:\Users\cowde\Desktop\mybourbontrailplan"

# Distilleries with free entry/tours
FREE_SLUGS = {
    "buffalo-trace",  # free public tours
}

BLOCK_RE = re.compile(
    r'(<script type="application/ld\+json">)\s*(.*?)\s*(</script>)',
    re.DOTALL
)

def get_slug(filepath):
    name = os.path.basename(filepath)
    return name.replace("distillery-", "").replace(".html", "")

def process_file(filepath):
    slug = get_slug(filepath)
    is_free = slug in FREE_SLUGS

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

        if data.get('@type') != 'TouristAttraction':
            return m.group(0)

        if 'isAccessibleForFree' not in data:
            # Insert after 'geo' if present, otherwise after 'address', otherwise at end
            new_data = {}
            inserted = False
            for k, v in data.items():
                new_data[k] = v
                if k in ('geo', 'openingHours') and not inserted:
                    new_data['isAccessibleForFree'] = is_free
                    inserted = True
            if not inserted:
                new_data['isAccessibleForFree'] = is_free
            file_changed = True
            new_json = json.dumps(new_data, indent=2, ensure_ascii=False)
            return f"{prefix}\n{new_json}\n{suffix}"

        return m.group(0)

    new_content = BLOCK_RE.sub(replacer, content)

    if file_changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
    return file_changed

def main():
    html_files = [
        f for f in glob.glob(os.path.join(BASE_DIR, "distillery-*.html"))
        if ' ' not in os.path.basename(f)
        and 'garrard-county' not in f
        and 'barton-1792' not in f
    ]

    updated = 0
    for filepath in sorted(html_files):
        if process_file(filepath):
            slug = get_slug(filepath)
            free_label = " (FREE)" if slug in FREE_SLUGS else ""
            print(f"  Fixed: {os.path.basename(filepath)}{free_label}")
            updated += 1

    print(f"\n{updated} files updated.")

    # Validate all TouristAttraction blocks have isAccessibleForFree
    missing = 0
    for filepath in sorted(html_files):
        content = open(filepath, encoding='utf-8').read()
        for m in BLOCK_RE.finditer(content):
            try:
                data = json.loads(m.group(2).strip())
            except json.JSONDecodeError:
                continue
            if data.get('@type') == 'TouristAttraction' and 'isAccessibleForFree' not in data:
                print(f"  STILL MISSING isAccessibleForFree: {os.path.basename(filepath)}")
                missing += 1

    if missing == 0:
        print("All TouristAttraction schemas have isAccessibleForFree.")
    else:
        print(f"{missing} schemas still missing isAccessibleForFree.")

if __name__ == '__main__':
    main()
