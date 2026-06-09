"""
Remove em dashes from all site HTML files with context-aware replacements:
  - <title> / og:title / JSON-LD headline  →  ': '
  - h1-h6 (no existing colon)              →  ': '
  - h1-h6 (colon already present)          →  ', '
  - </strong> followed by em dash          →  '</strong>: '  (label: description)
  - all other HTML content                 →  ', '
  - regular <script> blocks               →  untouched
"""

import re
import glob
import os

SKIP_FILES = {
    'email-signup-cta.html',
    'distillery-garrard-county.html',
    'distillery-barton-1792.html',
}

EM = '—'          # — unicode em dash
EM_ENT = '&mdash;'    # HTML entity form


def process_html(text):
    # ------------------------------------------------------------------ #
    # Step 1: protect regular <script> blocks so we never touch JS code.  #
    # JSON-LD blocks (<script type="application/ld+json">) are left in    #
    # place and handled separately in step 2.                             #
    # ------------------------------------------------------------------ #
    js_blocks = []

    def protect(m):
        attrs = m.group(1)
        if 'ld+json' in attrs.lower():
            return m.group(0)  # leave JSON-LD for step 2
        js_blocks.append(m.group(0))
        return f'\x00JS{len(js_blocks) - 1}\x00'

    text = re.sub(
        r'<script([^>]*)>(.*?)</script>',
        protect,
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # ------------------------------------------------------------------ #
    # Step 2: JSON-LD blocks — headline fields get ': ', rest get ', '   #
    # ------------------------------------------------------------------ #
    def fix_jsonld(m):
        b = m.group(0)
        # headline: "X — Y" → "X: Y"
        b = re.sub(
            r'("headline"\s*:\s*"[^"]*?) ' + EM + r' ([^"]*?")',
            r'\1: \2',
            b,
        )
        # remaining em dashes in JSON-LD → ', '
        b = b.replace(f' {EM} ', ', ')
        b = b.replace(f' {EM_ENT} ', ', ')
        b = b.replace(EM_ENT, ', ')
        return b

    text = re.sub(
        r'<script[^>]*ld\+json[^>]*>.*?</script>',
        fix_jsonld,
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # ------------------------------------------------------------------ #
    # Step 3: <title> tags → ': '                                        #
    # ------------------------------------------------------------------ #
    text = re.sub(
        r'(<title[^>]*>)(.*?)(</title>)',
        lambda m: m.group(1)
            + m.group(2).replace(f' {EM} ', ': ').replace(f' {EM_ENT} ', ': ').replace(EM_ENT, ':')
            + m.group(3),
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # ------------------------------------------------------------------ #
    # Step 4: og:title meta content attribute → ': '                     #
    # ------------------------------------------------------------------ #
    def fix_og_title_tag(m):
        return re.sub(
            r'(content=")([^"]*?)(")',
            lambda c: c.group(1)
                + c.group(2).replace(f' {EM} ', ': ').replace(f' {EM_ENT} ', ': ').replace(EM_ENT, ':')
                + c.group(3),
            m.group(0),
        )

    # property="og:title" anywhere in the meta tag
    text = re.sub(
        r'<meta[^>]*property=["\']og:title["\'][^>]*>',
        fix_og_title_tag,
        text,
        flags=re.IGNORECASE,
    )
    # reversed attribute order: content="..." property="og:title"
    text = re.sub(
        r'<meta[^>]*content="[^"]*' + EM + r'[^"]*"[^>]*property=["\']og:title["\'][^>]*>',
        fix_og_title_tag,
        text,
        flags=re.IGNORECASE,
    )

    # ------------------------------------------------------------------ #
    # Step 5: h1–h6 headings                                             #
    #   already has ': '  →  ', '                                        #
    #   no existing colon →  ': '                                        #
    # ------------------------------------------------------------------ #
    def fix_heading(m):
        open_t, inner, close_t = m.group(1), m.group(2), m.group(3)
        rep = ', ' if ': ' in inner else ': '
        inner = inner.replace(f' {EM} ', rep)
        inner = inner.replace(f' {EM_ENT} ', rep)
        inner = inner.replace(EM_ENT, rep.strip())
        return open_t + inner + close_t

    text = re.sub(
        r'(<h[1-6][^>]*>)(.*?)(</h[1-6]>)',
        fix_heading,
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # ------------------------------------------------------------------ #
    # Step 6: </strong> followed by em dash → '</strong>: '              #
    #   Handles <strong>Label</strong> — Description pattern             #
    # ------------------------------------------------------------------ #
    text = re.sub(
        r'</strong>\s*(?:' + EM + r'|' + EM_ENT + r')\s*',
        '</strong>: ',
        text,
        flags=re.IGNORECASE,
    )

    # ------------------------------------------------------------------ #
    # Step 7: all remaining spaced em dashes → ', '                      #
    # ------------------------------------------------------------------ #
    text = text.replace(f' {EM} ', ', ')

    # ------------------------------------------------------------------ #
    # Step 8: remaining &mdash; entities (with/without spaces) → ', '   #
    # ------------------------------------------------------------------ #
    text = text.replace(f' {EM_ENT} ', ', ')
    text = text.replace(f'{EM_ENT} ', ', ')
    text = text.replace(EM_ENT, ', ')

    # ------------------------------------------------------------------ #
    # Step 9: restore protected JS blocks                                 #
    # ------------------------------------------------------------------ #
    for i, block in enumerate(js_blocks):
        text = text.replace(f'\x00JS{i}\x00', block)

    return text


if __name__ == '__main__':
    # Run from the project root (parent of scripts/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    files = sorted(glob.glob('*.html'))
    changed, skipped = [], []

    for filepath in files:
        name = os.path.basename(filepath)
        if name in SKIP_FILES or '(1)' in name:
            skipped.append(name)
            continue

        with open(filepath, 'r', encoding='utf-8', newline='') as f:
            original = f.read()

        processed = process_html(original)

        if processed != original:
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                f.write(processed)
            changed.append(name)
            print(f'  updated: {name}')

    print(f'\n{len(changed)} files updated, {len(skipped)} skipped')
