#!/usr/bin/env python3
"""
Change TouristAttraction @type from a string to an array:
  "@type": "TouristAttraction"
  -> "@type": ["TouristAttraction", "LocalBusiness"]

This makes openingHours a valid property (inherited from LocalBusiness)
while preserving TouristAttraction semantics.
"""

import os, re, json, glob

BASE_DIR = r"C:\Users\cowde\Desktop\mybourbontrailplan"

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

        if data.get('@type') == 'TouristAttraction':
            data['@type'] = ['TouristAttraction', 'LocalBusiness']
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
        f for f in glob.glob(os.path.join(BASE_DIR, "distillery-*.html"))
        if ' ' not in os.path.basename(f)
        and 'garrard-county' not in f
        and 'barton-1792' not in f
    ]

    updated = 0
    for filepath in sorted(html_files):
        if process_file(filepath):
            print(f"  Updated: {os.path.basename(filepath)}")
            updated += 1

    print(f"\n{updated} files updated.")

    # Validate: all TouristAttraction blocks should now be arrays
    errors = 0
    still_string = 0
    for filepath in sorted(html_files):
        content = open(filepath, encoding='utf-8').read()
        for m in BLOCK_RE.finditer(content):
            try:
                data = json.loads(m.group(2).strip())
            except json.JSONDecodeError as e:
                print(f"  PARSE ERROR {os.path.basename(filepath)}: {e}")
                errors += 1
                continue
            t = data.get('@type')
            if t == 'TouristAttraction':
                print(f"  STILL STRING TYPE: {os.path.basename(filepath)}")
                still_string += 1
            elif isinstance(t, list) and 'TouristAttraction' in t and 'LocalBusiness' in t:
                pass  # correct
            elif isinstance(t, list) and 'TouristAttraction' in t:
                print(f"  MISSING LocalBusiness: {os.path.basename(filepath)}: {t}")
                errors += 1

    if errors == 0 and still_string == 0:
        print("All TouristAttraction schemas use array type [TouristAttraction, LocalBusiness].")
    else:
        print(f"{errors} errors, {still_string} still using string type.")

if __name__ == '__main__':
    main()
