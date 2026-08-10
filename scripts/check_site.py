"""Mechanical checks for the rules in CLAUDE.md.

Run from the repo root before committing:
    python scripts/check_site.py            # report, exit 1 on failures
    python scripts/check_site.py --counts   # also print current inventory counts

The point of this file is that a rule you can check should not be a rule you have
to remember. Every check here exists because the thing it checks went wrong at
least once. Failures block; warnings are things to look at but not gates.

Deliberately NOT checked (needs human judgment): whether a rating is correct,
whether copy is accurate, whether a venue fact is current.
"""

import glob
import json
import os
import re
import sys
from collections import defaultdict

# Windows consoles default to cp1252 and site copy contains arrows and dashes.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

FAIL, WARN = [], []
def fail(page, msg): FAIL.append((page, msg))
def warn(page, msg): WARN.append((page, msg))

# Files excluded from the live site on purpose (CLAUDE.md).
BLOCKED = {"distillery-garrard-county.html", "distillery-barton-1792.html"}

# ---------------------------------------------------------------------------
# BASELINE: pre-existing title/meta overages, recorded August 2026 when this
# checker was written. These are real debt, not exceptions to the rule. They are
# listed so the checker can do its actual job, which is catching NEW violations,
# instead of drowning them in 34 old ones.
#
# Values are (title_len, meta_len); 0 means that field was fine.
# Rules: a listed page still over its recorded length is a WARN. A page NOT
# listed that goes over is a FAIL. A listed page that gets fixed prints a note
# telling you to delete its line, so the list shrinks and never silently rots.
# ---------------------------------------------------------------------------
BASELINE = {
    "about.html": (0, 172),
    "best-time-to-visit-bourbon-trail.html": (92, 171),
    "bourbon-trail-non-bourbon-drinkers.html": (98, 172),
    "bourbon-trail-transportation-guide.html": (0, 196),
    "buffalo-trace-gift-shop-guide.html": (0, 179),
    "distillery-baker-bird.html": (0, 178),
    "distillery-bardstown-bourbon-co-louisville.html": (95, 184),
    "distillery-bardstown-bourbon-co.html": (0, 180),
    "distillery-bluegrass.html": (86, 174),
    "distillery-buffalo-trace.html": (0, 180),
    "distillery-castle-key.html": (0, 171),
    "distillery-chicken-cock.html": (0, 189),
    "distillery-copper-and-kings.html": (85, 173),
    "distillery-dark-arts.html": (0, 179),
    "distillery-evan-williams.html": (0, 171),
    "distillery-four-roses.html": (0, 189),
    "distillery-general-george.html": (0, 192),
    "distillery-green-river-louisville.html": (86, 193),
    "distillery-jim-beam.html": (0, 179),
    "distillery-log-still.html": (0, 188),
    "distillery-lux-row.html": (0, 176),
    "distillery-makers-mark.html": (0, 173),
    "distillery-monks-road-boiler-house.html": (0, 178),
    "distillery-pensive.html": (0, 171),
    "distillery-preservation.html": (0, 189),
    "distillery-whiskey-thief.html": (0, 183),
    "kentucky-bourbonfest.html": (89, 177),
}
FIXED_SINCE_BASELINE = []
# Not real pages: Drive sync duplicates and the CTA fragment.
def is_page(f):
    return " (1)" not in f and f != "email-signup-cta.html"

PAGES = sorted(f for f in glob.glob("*.html") if is_page(f))
PROFILES = [f for f in PAGES if f.startswith("distillery-")]
SITE_PAGES = [f for f in PAGES if f not in BLOCKED]

def read(f):
    with open(f, encoding="utf-8") as fh:
        return fh.read()

SRC = {f: read(f) for f in PAGES}


def strip_code(s):
    """Remove script/style so text checks do not trip on JS string literals."""
    s = re.sub(r"<script[\s\S]*?</script>", " ", s)
    s = re.sub(r"<style[\s\S]*?</style>", " ", s)
    return s


# ---------------------------------------------------------------- copy style
# Reader-facing copy only. JS comments and code are not site content, so the
# check runs on the page with script/style stripped, plus title and meta, which
# are reader-facing in search results.
# SITE_PAGES, not PAGES: the two blocked profiles are not published, so copy
# rules do not apply to them and flagging them is pure noise.
for f in SITE_PAGES:
    visible = strip_code(SRC[f])
    meta = " ".join(re.findall(r'<(?:title|meta)[^>]*>', SRC[f]))
    n = len(re.findall(r"&mdash;|—", visible + meta))
    if n:
        fail(f, f"{n} em dash(es) in reader-facing copy; see the copy style table in CLAUDE.md")


# ------------------------------------------------------- titles, meta, canonical
def length_check(f, field, actual, limit):
    """FAIL for new overages, WARN for ones recorded in BASELINE."""
    if actual < limit:
        return False
    idx = 0 if field == "title" else 1
    recorded = BASELINE.get(f, (0, 0))[idx]
    if recorded:
        warn(f, f"{field} is {actual} chars (limit {limit}) - known debt, in the "
                f"check_site.py BASELINE")
    else:
        fail(f, f"{field} is {actual} chars, limit is {limit}")
    return True

for f in SITE_PAGES:
    s = SRC[f]
    t = re.search(r"<title>(.*?)</title>", s, re.S)
    if not t:
        fail(f, "no <title>")
    else:
        over = length_check(f, "title", len(t.group(1)), 85)
        if not over and BASELINE.get(f, (0, 0))[0]:
            FIXED_SINCE_BASELINE.append(f"{f} title")

    d = re.search(r'name="description"\s+content="(.*?)"', s, re.S)
    if not d:
        fail(f, "no meta description")
    else:
        rendered = d.group(1).replace("&amp;", "&")
        over = length_check(f, "meta description", len(rendered), 170)
        if not over and BASELINE.get(f, (0, 0))[1]:
            FIXED_SINCE_BASELINE.append(f"{f} meta description")

    c = re.search(r'rel="canonical"\s+href="([^"]+)"', s)
    if not c:
        fail(f, "no canonical")
    else:
        want = ("https://mybourbontrailplan.com/" if f == "index.html"
                else f"https://mybourbontrailplan.com/{f}")
        if c.group(1) != want:
            fail(f, f"canonical is {c.group(1)}, expected {want}")

    for prop in ("og:title", "og:description", "og:type", "og:url"):
        if f'property="{prop}"' not in s:
            warn(f, f"missing {prop}")


# --------------------------------------------------------- required furniture
for f in SITE_PAGES:
    s = SRC[f]
    if "G-DVK4D6KJJP" not in s:
        fail(f, "no GA measurement ID")
    if "googletagmanager.com/gtag/js" not in s:
        fail(f, "no GA loader script tag")
    if "assets.mailerlite.com/js/universal.js" not in s:
        warn(f, "no MailerLite universal script")
    if "-webkit-text-size-adjust" not in s:
        fail(f, "missing -webkit-text-size-adjust (iOS Safari text inflation)")
    if "favicon-32.png" not in s:
        warn(f, "missing favicon chain")
    # nav must carry a Map link, and collapse at 900px
    if 'href="map.html"' not in s and f != "map.html":
        warn(f, "no nav link to map.html")
    if "max-width:900px" not in s.replace(" ", "") and "max-width: 900px" not in s:
        warn(f, "no 900px hamburger breakpoint")
    # unguarded gtag calls outside the init block
    for m in re.finditer(r"(.{0,40})\bgtag\('event'", s):
        if "typeof gtag" not in m.group(1):
            warn(f, "possible unguarded gtag('event') call")
            break


# ------------------------------------------------------------------ JSON-LD
GOOD_PUBLISHER = {"@type": "Organization", "name": "Bourbon Trail Planner"}
for f in SITE_PAGES:
    for m in re.finditer(r'<script type="application/ld\+json">([\s\S]*?)</script>', SRC[f]):
        raw = m.group(1)
        try:
            j = json.loads(raw)
        except Exception as e:
            fail(f, f"JSON-LD does not parse: {e}")
            continue
        blocks = j if isinstance(j, list) else [j]
        for b in blocks:
            if not isinstance(b, dict):
                continue
            t = b.get("@type")
            types = t if isinstance(t, list) else [t]
            if "TouristAttraction" in types:
                if "LocalBusiness" not in types:
                    fail(f, '@type must be the array ["TouristAttraction","LocalBusiness"]')
                if "review" in b or "reviewRating" in b or "aggregateRating" in b:
                    fail(f, "TouristAttraction carries a review/rating block (Google policy violation)")
            for key in ("author", "publisher"):
                if key in b and isinstance(b[key], dict):
                    if b[key].get("@type") != "Organization":
                        fail(f, f"{key} must be an Organization, got {b[key].get('@type')}")
                    elif b[key].get("name") != "Bourbon Trail Planner":
                        fail(f, f'{key}.name must be "Bourbon Trail Planner", got {b[key].get("name")!r}')
            for key in ("datePublished", "dateModified"):
                if key in b and isinstance(b[key], str):
                    if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$", b[key]):
                        fail(f, f"{key} must be ISO 8601 with offset, got {b[key]!r}")


# ------------------------------------------------- guide date: three surfaces
MONTHS = ("January February March April May June July August September "
          "October November December").split()
for f in SITE_PAGES:
    s = SRC[f]
    dm = re.search(r'"dateModified":\s*"(\d{4})-(\d{2})', s)
    vis = re.search(r"Updated\s+([A-Z][a-z]+)\s+(\d{4})", strip_code(s))
    if dm and vis:
        want_m = MONTHS[int(dm.group(2)) - 1]
        if vis.group(1) != want_m or vis.group(2) != dm.group(1):
            fail(f, f"date surfaces disagree: schema says {want_m} {dm.group(1)}, "
                    f"visible line says {vis.group(1)} {vis.group(2)}")
    elif dm and not vis:
        warn(f, "has schema dateModified but no visible 'Updated {Month} {Year}' line")


# -------------------------------------------------------- link integrity
for f in PAGES:
    for href in set(re.findall(r'href="([a-z0-9][a-z0-9\-]*\.html)(?:#[^"]*)?"', SRC[f])):
        if not os.path.exists(href):
            fail(f, f"link to missing file: {href}")
    for src in set(re.findall(r'src="(images/[^"]+?)"', SRC[f])):
        clean = src.split("?")[0]
        if not os.path.exists(clean):
            fail(f, f"missing asset: {clean}")
        if clean.startswith("images/Icons/"):
            fail(f, "images/Icons/ is the wrong casing; Netlify is case-sensitive")


# ------------------------------------------- blocked pages must not be linked
SITE_FILES = ["distilleries.html", "trip-builder.html", "map.html"] + [
    f for f in PAGES if f.startswith("bourbon-trail-map-")]
for b in BLOCKED:
    for f in SITE_FILES:
        if os.path.exists(f) and b in SRC.get(f, ""):
            fail(f, f"references excluded page {b}")
    if os.path.exists("sitemap.xml") and b in read("sitemap.xml"):
        fail("sitemap.xml", f"contains excluded page {b}")


# --------------------------------------------------------------- sitemap
if os.path.exists("sitemap.xml"):
    sm = read("sitemap.xml")
    listed = set(re.findall(r"<loc>https://mybourbontrailplan\.com/([^<]*)</loc>", sm))
    for f in SITE_PAGES:
        key = "" if f == "index.html" else f
        if key not in listed:
            warn("sitemap.xml", f"{f} is not in the sitemap (run generate_sitemap.py)")


# ---------------------------------------------------- hardcoded region totals
COUNT_RE = re.compile(
    r"\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen)"
    r"\s+distilleries\b", re.I)
# Pacing/pair phrasing is allowed; see the count policy in CLAUDE.md.
ALLOWED = re.compile(
    r"(per day|a day|in a day|ceiling|furthest apart|apart\b|over 3 days|"
    r"60\+|over \d+|about \d+|roughly \d+|showing|between stops|craft stop|"
    r"walking distance|on foot|in three days|\+ 1 craft|"
    r"you'?ll hit|hit \d+|clusters?|&bull;|\bday \d)", re.I)
for f in SITE_PAGES:
    txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", strip_code(SRC[f])))
    for m in COUNT_RE.finditer(txt):
        ctx = txt[max(0, m.start() - 70):m.end() + 70]
        if not ALLOWED.search(ctx):
            warn(f, f'possible hardcoded count: "...{m.group(0)}..." in "{ctx.strip()[:90]}"')


# ---------------------------------------------------------- affiliate links
# CLAUDE.md used to list all 11 Booking.com URLs verbatim so they could be
# checked by eye. That is a second copy of live data, which is the drift pattern
# this file exists to prevent, so the list was removed and the invariants are
# asserted here instead: right publisher ID, right tracking domain, pointing at
# booking.com. Corruption now fails a check rather than needing a doc read.
CJ_DOMAINS = {"www.kqzyfj.com", "www.anrdoezrs.net", "www.tkqlhce.com", "www.jdoqocy.com"}
CJ_PUBLISHER = "click-101752228-17293132"
for f in SITE_PAGES:
    for m in re.finditer(r'href="https://([^/"]+)/(click-[0-9\-]+)\?url=([^"]*)"', SRC[f]):
        host, pub, target = m.group(1), m.group(2), m.group(3)
        if host not in CJ_DOMAINS:
            fail(f, f"affiliate link on unknown tracking domain {host}")
        if pub != CJ_PUBLISHER:
            fail(f, f"affiliate link has publisher {pub}, expected {CJ_PUBLISHER}")
        if "booking.com" not in target:
            fail(f, f"CJ affiliate link does not target booking.com: {target[:60]}")
    # any CJ-looking domain used without the tracking path at all
    for host in CJ_DOMAINS:
        if host in SRC[f] and CJ_PUBLISHER not in SRC[f]:
            fail(f, f"uses CJ domain {host} without the {CJ_PUBLISHER} tracking path")
    if "vrbo.com/affiliate" in SRC[f] and "vrbo.com/affiliate/VD0a4b2" not in SRC[f]:
        fail(f, "VRBO affiliate link is not the expected VD0a4b2 code")


# ------------------------------------------------------------- rating drift
def profile_ratings():
    out = {}
    for f in PROFILES:
        m = re.search(r'snap-value">\s*([0-9]+\.[0-9])\s*/\s*10', SRC[f])
        if m:
            out[f] = m.group(1)
    return out

canon = profile_ratings()
if os.path.exists("distilleries.html"):
    for m in re.finditer(r'<a href="(distillery-[^"]+\.html)" class="dist-card"[^>]*>([\s\S]{0,1800}?)</a>',
                         SRC["distilleries.html"]):
        r = re.search(r'dist-card-rating">([0-9.]+)<', m.group(2))
        if r and m.group(1) in canon and r.group(1) != canon[m.group(1)]:
            fail("distilleries.html",
                 f"{m.group(1)} rating {r.group(1)} disagrees with profile {canon[m.group(1)]}"
                 " (run scripts/check_ratings.py --apply)")
if os.path.exists("trip-builder.html"):
    for m in re.finditer(r'profile:"(distillery-[^"]+\.html)"[^}]*?rating:([0-9.]+)',
                         SRC["trip-builder.html"]):
        if m.group(1) in canon and m.group(2) != canon[m.group(1)]:
            fail("trip-builder.html",
                 f"{m.group(1)} rating {m.group(2)} disagrees with profile {canon[m.group(1)]}"
                 " (run scripts/check_ratings.py --apply)")


# ------------------------------------------------------------------- report
def counts():
    tb = len(re.findall(r'profile:"distillery-', SRC.get("trip-builder.html", "")))
    mp = SRC.get("map.html", "")
    mp_n = len(re.findall(r'profile:"distillery-', mp.split("const DISTILLERIES", 1)[-1]))
    cards = len(re.findall(r'class="dist-card"', SRC.get("distilleries.html", "")))
    print("Inventory (derive, never hardcode):")
    print(f"  profile files                {len(PROFILES)}  ({len(BLOCKED)} excluded from the site)")
    print(f"  directory cards              {cards}")
    print(f"  trip-builder D entries       {tb}")
    print(f"  map.html pins                {mp_n}")
    print(f"  site pages                   {len(SITE_PAGES)}")
    print(f"  icons in images/icons        {len(glob.glob('images/icons/*.svg'))}")
    print()

if "--counts" in sys.argv:
    counts()

by_page = defaultdict(list)
for p, m in FAIL:
    by_page[p].append(("FAIL", m))
for p, m in WARN:
    by_page[p].append(("WARN", m))

if by_page:
    for p in sorted(by_page):
        print(p)
        for lvl, m in by_page[p]:
            print(f"  {lvl}  {m}")
    print()

if FIXED_SINCE_BASELINE:
    print("Fixed since the baseline was taken. Delete these from BASELINE in "
          "scripts/check_site.py so the list keeps shrinking:")
    for x in sorted(set(FIXED_SINCE_BASELINE)):
        print(f"  {x}")
    print()

baselined = sum(1 for lvl_msgs in by_page.values() for lvl, m in lvl_msgs if "BASELINE" in m)
print(f"checked {len(SITE_PAGES)} pages: {len(FAIL)} failure(s), {len(WARN)} warning(s)"
      f" ({baselined} of the warnings are baselined title/meta debt)")
if FAIL:
    print("\nFAIL - fix the above, or update CLAUDE.md if the rule has genuinely changed.")
    sys.exit(1)
print("PASS")
