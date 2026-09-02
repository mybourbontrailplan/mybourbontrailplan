"""Check (and optionally fix) distillery rating drift.

Every rating lives in three places: the profile page's snapshot headline, the
card in distilleries.html, and the rating: field in trip-builder.html's D array.
They drift. The profile is canonical per CLAUDE.md, so this reads each profile's
snapshot value as truth and reports anything that disagrees.

Run from the repo root:
    python scripts/check_ratings.py            # report drift, exit 1 if any
    python scripts/check_ratings.py --apply    # sync the other two to the profile

First run (August 2026) found 23 of 60 disagreeing: 16 wrong in the directory,
7 wrong in the trip builder. Neither secondary copy is trustworthy on its own.
"""
import re, sys, glob, io

APPLY = '--apply' in sys.argv

def to_file(href):
    """Accept /distillery-x or distillery-x.html, return the filename."""
    h = href.lstrip('/').split('?')[0].split('#')[0]
    return h if h.endswith('.html') else h + '.html'


canon = {}
for f in sorted(glob.glob('distillery-*.html')):
    if ' (1)' in f: continue
    s = open(f, encoding='utf-8').read()
    m = re.search(r'snap-value">\s*([0-9]+\.[0-9])\s*/\s*10', s)
    if m: canon[f] = m.group(1)

changes = {'distilleries.html': [], 'trip-builder.html': []}

# ---- distilleries.html: <div class="dist-card-rating">X</div> inside each card
d = open('distilleries.html', encoding='utf-8').read()
def fix_card(m):
    href, attrs, body = m.group(1), m.group(2), m.group(3)
    prof = to_file(href)
    want = canon.get(prof)
    if not want: return m.group(0)
    def rep(rm):
        have = rm.group(1).strip()
        if have != want:
            changes['distilleries.html'].append((prof, have, want))
            return f'dist-card-rating">{want}<'
        return rm.group(0)
    newbody = re.sub(r'dist-card-rating">([^<]+)<', rep, body, count=1)
    return f'<a href="{href}" class="dist-card"{attrs}>{newbody}</a>'
CARD_RE = r'<a href="(/?distillery-[^"]+?)" class="dist-card"([^>]*)>([\s\S]{0,1800}?)</a>'
d2 = re.sub(CARD_RE, fix_card, d)
if not re.search(CARD_RE, d):
    sys.exit("distilleries.html: 0 dist-cards parsed - the card regex is out of "
             "date and this check is not running.")

# ---- trip-builder.html: profile:"X" ... rating:N
t = open('trip-builder.html', encoding='utf-8').read()
def fix_tb(m):
    href, mid, have = m.group(1), m.group(2), m.group(3)
    want = canon.get(to_file(href))
    if want and have != want:
        changes['trip-builder.html'].append((to_file(href), have, want))
        return f'profile:"{href}"{mid}rating:{want}'
    return m.group(0)
TB_RE = r'profile:"(/?distillery-[^"]+?)"([^}]*?)rating:([0-9.]+)'
t2 = re.sub(TB_RE, fix_tb, t)
if not re.search(TB_RE, t):
    sys.exit("trip-builder.html: 0 profile entries parsed - the regex is out of "
             "date and this check is not running.")

for fn, rows in changes.items():
    print(f"\n=== {fn}: {len(rows)} rating(s) to correct ===")
    for prof, have, want in sorted(rows):
        print(f"   {prof:44s} {have:5s} -> {want}")

total = sum(len(v) for v in changes.values())
print(f"\ntotal edits: {total}   (canonical values read from {len(canon)} profiles)")

if APPLY:
    io.open('distilleries.html','w',encoding='utf-8',newline='\n').write(d2)
    io.open('trip-builder.html','w',encoding='utf-8',newline='\n').write(t2)
    print("WRITTEN")
else:
    print("dry run only, pass --apply to write")

if not APPLY and total:
    sys.exit(1)
