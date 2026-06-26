"""
Add openingHours to JSON-LD schema and update body Hours text for 15 profiles.
Also fixes Bluegrass coordinates in trip-builder.html + distillery profile,
and adds Jim Beam production-pause note.
"""

import os, re

BASE = r"C:\Users\cowde\Desktop\mybourbontrailplan"

# ── 15 profiles: (filename, openingHours value, old_body, new_body) ──────────
PROFILES = [
    ("distillery-baker-bird.html",
        "Th-Fr 14:00-17:00, Sa-Su 13:00-17:00",
        "Call ahead for current hours and availability",
        "Thursday–Friday 2–5 PM (reservation required), Saturday–Sunday 1–5 PM"),

    ("distillery-bh-james.html",
        "We-Fr 11:00-18:00, Sa 12:00-18:00",
        "Check website for current hours",
        "Wednesday–Friday 11 AM – 6 PM, Saturday 12 PM – 6 PM. Closed Sunday–Tuesday."),

    ("distillery-bluegrass.html",
        "Mo-We 09:00-17:00, Th-Sa 09:00-18:00, Su 12:00-17:00",
        "Thursday–Sunday (check website for current hours)",
        "Monday–Wednesday 9 AM – 5 PM, Thursday–Saturday 9 AM – 6 PM, Sunday 12 PM – 5 PM"),

    ("distillery-copper-and-kings.html",
        "Mo 10:00-17:00, Tu 09:00-17:00, We-Th 10:00-18:00, Fr-Sa 10:00-22:00, Su 10:00-18:00",
        "Thursday–Sunday (check website for current hours)",
        "Monday 10 AM – 5 PM, Tuesday 9 AM – 5 PM, Wednesday–Thursday 10 AM – 6 PM, Friday–Saturday 10 AM – 10 PM, Sunday 10 AM – 6 PM"),

    ("distillery-fresh-bourbon.html",
        "We-Sa 12:00-20:00",
        "Thursday–Saturday (check website for current hours)",
        "Wednesday–Saturday 12 PM – 8 PM. Closed Sunday–Tuesday."),

    ("distillery-general-george.html",
        "Th 13:00-17:00, Fr 11:00-16:30, Sa 11:00-17:00",
        None, None),  # No body Hours field in this profile

    ("distillery-golden-pond.html",
        "Mo-Sa 09:00-17:00",
        "Call ahead for current hours",
        "Monday–Saturday 9 AM – 5 PM. Closed Sunday."),

    ("distillery-jackson-purchase.html",
        "Mo-Fr 09:00-17:00",
        "Check website for current hours",
        "Monday–Friday 9 AM – 5 PM. Closed Saturday and Sunday."),

    ("distillery-james-e-pepper.html",
        "Mo-Th 10:00-18:00, Fr-Sa 10:00-19:30, Su 11:30-17:30",
        "Wednesday–Sunday (check website for current hours)",
        "Monday–Thursday 10 AM – 6 PM, Friday–Saturday 10 AM – 7:30 PM, Sunday 11:30 AM – 5:30 PM"),

    ("distillery-larrikin.html",
        "Tu-Sa 10:00-18:00, Su 12:00-18:00",
        "Check website for current hours",
        "Tuesday–Saturday 10 AM – 6 PM, Sunday 12 PM – 6 PM. Closed Monday."),

    ("distillery-neeley-family.html",
        "Mo-Sa 11:00-18:00, Su 13:00-18:00",
        "Thursday–Saturday (check website or call for current hours)",
        "Monday–Saturday 11 AM – 6 PM, Sunday 1 PM – 6 PM"),

    ("distillery-old-pogue.html",
        "Tu-Sa 10:00-16:00",
        "Thursday–Saturday (limited hours, call ahead to confirm)",
        "Tuesday–Saturday 10 AM – 4 PM. Closed Sunday and Monday."),

    ("distillery-second-sight.html",
        "Fr-Sa 09:00-18:00, Su 09:00-17:00",
        "Thursday–Saturday (check website for current hours)",
        "Friday–Saturday 9 AM – 6 PM, Sunday 9 AM – 5 PM. Thursday by appointment. Closed Monday–Wednesday."),

    ("distillery-the-bard.html",
        "Mo-Su 10:00-17:00",
        "Check website or call for current hours",
        "Daily 10 AM – 5 PM"),

    ("distillery-wenzel.html",
        "We-Sa 11:00-21:00, Su 12:00-17:00",
        "Check website for current hours",
        "Wednesday–Saturday 11 AM – 9 PM, Sunday 12 PM – 5 PM. Closed Monday–Tuesday."),
]

changed = []
errors = []


def insert_opening_hours(content, hours_value):
    """Insert openingHours after telephone field; fall back to before url."""
    hours_line = f'  "openingHours": "{hours_value}",'

    # Try after telephone
    m = re.search(r'(\s+"telephone":\s+"[^"]*",)', content)
    if m:
        return content[:m.end()] + "\n" + hours_line + content[m.end():]

    # Fall back: before "url"
    m = re.search(r'(\s+"url":\s+)', content)
    if m:
        return content[:m.start()] + "\n" + hours_line + content[m.start():]

    return None  # could not find insertion point


# ── 1. Profile schema + body updates ─────────────────────────────────────────
for fname, hours_value, old_body, new_body in PROFILES:
    path = os.path.join(BASE, fname)
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        original = content

        # Skip if openingHours already present
        if '"openingHours"' in content:
            if old_body and new_body:
                content = content.replace(old_body, new_body)
            if content != original:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                changed.append(f"{fname} (body only, schema already present)")
            continue

        # Insert openingHours
        new_content = insert_opening_hours(content, hours_value)
        if new_content is None:
            errors.append(f"NO INSERTION POINT: {fname}")
            continue
        content = new_content

        # Update body hours text
        if old_body and new_body:
            content = content.replace(old_body, new_body)

        if content == original:
            errors.append(f"NO CHANGE: {fname}")
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            changed.append(fname)

    except Exception as e:
        errors.append(f"ERROR {fname}: {e}")


# ── 2. Bluegrass: fix schema coordinates + trip-builder entry ─────────────────

# Fix distillery-bluegrass.html schema coordinates
bg_path = os.path.join(BASE, "distillery-bluegrass.html")
try:
    with open(bg_path, "r", encoding="utf-8") as f:
        content = f.read()
    original = content
    content = content.replace('"latitude": 38.0355,', '"latitude": 38.1340,')
    content = content.replace('"longitude": -84.5205', '"longitude": -84.6835')
    if content != original:
        with open(bg_path, "w", encoding="utf-8") as f:
            f.write(content)
        changed.append("distillery-bluegrass.html (schema coordinates)")
    else:
        errors.append("Bluegrass coordinates: no change (may already be correct)")
except Exception as e:
    errors.append(f"ERROR distillery-bluegrass.html coords: {e}")

# Fix trip-builder.html Bluegrass entry
tb_path = os.path.join(BASE, "trip-builder.html")
try:
    with open(tb_path, "r", encoding="utf-8") as f:
        content = f.read()
    original = content
    old_tb = '{id:"bluegrass",name:"Bluegrass Distillers",lat:38.0355,lng:-84.5205,region:"Lexington",type:"Craft",cost:"$15–$25",costAvg:15,booking:"Easy",profile:"distillery-bluegrass.html",desc:"True craft operation in downtown Lexington. Blue corn bourbon.",rating:7.7,bookWeeks:"Walk-up"}'
    new_tb = '{id:"bluegrass",name:"Bluegrass Distillers",lat:38.1340,lng:-84.6835,region:"Lexington",type:"Craft",cost:"$15–$25",costAvg:15,booking:"Easy",profile:"distillery-bluegrass.html",desc:"62-acre horse country farm in Midway. Grain-to-glass bourbon.",rating:7.7,bookWeeks:"Walk-up"}'
    content = content.replace(old_tb, new_tb)
    if content != original:
        with open(tb_path, "w", encoding="utf-8") as f:
            f.write(content)
        changed.append("trip-builder.html (Bluegrass coordinates + desc)")
    else:
        errors.append("trip-builder.html Bluegrass: no match — check exact string")
except Exception as e:
    errors.append(f"ERROR trip-builder.html: {e}")


# ── 3. Jim Beam: add production-pause note ────────────────────────────────────
jb_path = os.path.join(BASE, "distillery-jim-beam.html")
try:
    with open(jb_path, "r", encoding="utf-8") as f:
        content = f.read()
    original = content

    # Update What to Expect para 2 — remove stale "production process" line
    old_p2 = "The standard tour is solid but not distinctive, you'll see the same production process you've seen elsewhere. Where Jim Beam shines is in their <strong>premium experiences</strong>"
    new_p2 = "The standard tour is solid but not distinctive. Where Jim Beam shines is in their <strong>premium experiences</strong>"
    content = content.replace(old_p2, new_p2)

    # Insert production-pause notice before that paragraph
    old_p1_end = "and offers the most variety of any distillery on the trail in terms of experience options.</p>"
    new_p1_end = ("and offers the most variety of any distillery on the trail in terms of experience options.</p>\n"
                  '<p><strong>Note:</strong> Jim Beam paused distilling at Clermont for 2026 due to industry-wide demand softening. '
                  "All tours, tastings, the Cookhouse restaurant, and the gift shop remain fully open. "
                  "The stillhouse and warehouses are part of the campus tour.</p>")
    content = content.replace(old_p1_end, new_p1_end)

    # Update Stillhouse Tour description
    old_tour = "The standard distillery tour covering the full production process. Well-organized, decent tasting at the end. A reliable choice if you haven't visited before."
    new_tour = "The standard campus tour through the historic stillhouse and aging warehouses. Distilling is paused for 2026, but the tour is well-organized with a solid tasting at the end. A reliable choice if you haven't visited before."
    content = content.replace(old_tour, new_tour)

    if content != original:
        with open(jb_path, "w", encoding="utf-8") as f:
            f.write(content)
        changed.append("distillery-jim-beam.html (production pause note)")
    else:
        errors.append("distillery-jim-beam.html: no changes matched")
except Exception as e:
    errors.append(f"ERROR distillery-jim-beam.html: {e}")


# ── Report ─────────────────────────────────────────────────────────────────────
print(f"Changed {len(changed)} files:")
for f in changed:
    print(f"  OK: {f}")
if errors:
    print(f"\nProblems ({len(errors)}):")
    for e in errors:
        print(f"  {e}")
