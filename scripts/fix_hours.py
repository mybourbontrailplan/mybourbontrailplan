"""One-shot script to update openingHours JSON-LD and body <strong>Hours:</strong> text
across all 31 distillery profiles with stale hours."""

import os

BASE = r"C:\Users\cowde\Desktop\mybourbontrailplan"

UPDATES = [
    ("distillery-buffalo-trace.html",
        '"openingHours": "Mo-Sa 09:00-17:00, Su 12:00-17:00"',
        '"openingHours": "Mo-Sa 09:00-17:00, Su 11:00-17:00"',
        "Monday–Saturday 9 AM – 5 PM, Sunday 12 PM – 5 PM (tour times vary, check website)",
        "Monday–Saturday 9 AM – 5 PM, Sunday 11 AM – 5 PM (tour times vary, check website)"),

    ("distillery-castle-key.html",
        '"openingHours": "Th-Su 10:00-17:00"',
        '"openingHours": "We-Sa 10:30-17:00, Su 11:00-17:00"',
        "Thursday–Sunday 10 AM – 5 PM. Closed Mon–Wed.",
        "Wednesday–Saturday 10:30 AM – 5 PM, Sunday 11 AM – 5 PM. Closed Mon–Tue."),

    ("distillery-new-riff.html",
        '"openingHours": "We-Su 12:00-18:00"',
        '"openingHours": "Tu-Th 11:00-19:00, Fr-Sa 11:00-20:00, Su 11:00-17:00"',
        "Wednesday–Sunday 12 PM – 6 PM. Closed Mon–Tue.",
        "Tuesday–Thursday 11 AM – 7 PM, Friday–Saturday 11 AM – 8 PM, Sunday 11 AM – 5 PM. Closed Monday."),

    ("distillery-four-roses.html",
        '"openingHours": "Tu-Sa 09:00-17:00, Su 12:00-16:00"',
        '"openingHours": "We-Sa 09:00-16:00, Su 12:00-16:00"',
        "Tuesday–Saturday 9 AM – 5 PM, Sunday 12 PM – 4 PM. Closed Monday.",
        "Wednesday–Saturday 9 AM – 4 PM, Sunday 12 PM – 4 PM. Closed Monday–Tuesday."),

    ("distillery-heaven-hill.html",
        '"openingHours": "Mo-Sa 09:30-17:00, Su 12:00-17:00"',
        '"openingHours": "Mo-Sa 09:30-17:00, Su 13:00-17:00"',
        "Monday–Saturday 9:30 AM – 5 PM, Sunday 12 PM – 5 PM",
        "Monday–Saturday 9:30 AM – 5 PM, Sunday 1 PM – 5 PM"),

    ("distillery-willett.html",
        '"openingHours": "Mo-Sa 09:30-17:00, Su 12:00-16:00"',
        '"openingHours": "Mo-Sa 10:00-17:30"',
        "Monday–Saturday 9:30 AM – 5 PM, Sunday 12 PM – 4 PM",
        "Monday–Saturday 10 AM – 5:30 PM. Closed Sunday."),

    ("distillery-angels-envy.html",
        '"openingHours": "Mo-Sa 10:00-19:00, Su 12:00-18:00"',
        '"openingHours": "Mo-We 12:00-18:00, Th 11:00-20:00, Fr-Sa 10:00-20:00, Su 12:30-18:00"',
        "Monday–Saturday 10 AM – 7 PM, Sunday 12 PM – 6 PM (tour times vary)",
        "Monday–Wednesday 12 PM – 6 PM, Thursday 11 AM – 8 PM, Friday–Saturday 10 AM – 8 PM, Sunday 12:30 PM – 6 PM"),

    ("distillery-old-forester.html",
        '"openingHours": "Tu-Sa 10:00-18:00, Su 12:00-17:00"',
        '"openingHours": "Tu-Sa 10:00-17:00"',
        "Tuesday–Saturday 10 AM – 6 PM, Sunday 12 PM – 5 PM. Closed Monday.",
        "Tuesday–Saturday 10 AM – 5 PM. Closed Sunday and Monday."),

    ("distillery-evan-williams.html",
        '"openingHours": "Mo-Sa 10:00-18:00, Su 12:00-17:00"',
        '"openingHours": "Mo-Th 11:00-17:00, Fr-Sa 10:00-17:00, Su 13:00-17:00"',
        "Monday–Saturday 10 AM – 6 PM, Sunday 12 PM – 5 PM",
        "Monday–Thursday 11 AM – 5 PM, Friday–Saturday 10 AM – 5 PM, Sunday 1 PM – 5 PM"),

    ("distillery-bardstown-bourbon-co.html",
        '"openingHours": "Mo-Sa 10:00-17:00, Su 12:00-17:00"',
        '"openingHours": "Mo-Tu 10:00-15:00, We-Su 09:00-17:00"',
        "Monday–Saturday 10 AM – 5 PM, Sunday 12 PM – 5 PM",
        "Monday–Tuesday 10 AM – 3 PM, Wednesday–Sunday 9 AM – 5 PM"),

    ("distillery-green-river.html",
        '"openingHours": "We-Sa 10:00-17:00, Su 12:00-17:00"',
        '"openingHours": "We-Sa 09:00-17:00"',
        "Wednesday–Saturday 10 AM – 5 PM, Sunday 12 PM – 5 PM (hours may vary seasonally)",
        "Wednesday–Saturday 9 AM – 5 PM. Closed Sunday–Tuesday."),

    ("distillery-limestone-branch.html",
        '"openingHours": "Tu-Sa 10:00-17:00, Su 12:30-17:00"',
        '"openingHours": "Tu-Sa 09:30-17:00"',
        "Tuesday–Saturday 10 AM – 5 PM, Sunday 12:30 PM – 5 PM (check website for seasonal hours)",
        "Tuesday–Saturday 9:30 AM – 5 PM. Closed Sunday and Monday."),

    ("distillery-log-still.html",
        '"openingHours": "We-Sa 10:00-17:00, Su 12:00-17:00"',
        '"openingHours": "Mo-Sa 10:00-17:00, Su 11:00-15:00"',
        "Wednesday–Saturday 10 AM – 5 PM, Sunday 12 PM – 5 PM. Closed Mon–Tue.",
        "Monday–Saturday 10 AM – 5 PM, Sunday 11 AM – 3 PM"),

    ("distillery-jeptha-creed.html",
        '"openingHours": "We-Sa 10:00-17:00, Su 13:00-17:00"',
        '"openingHours": "Th-Sa 11:00-18:00, Su 12:00-17:00"',
        "Wednesday–Saturday 10 AM – 5 PM, Sunday 1 PM – 5 PM (check website for current hours)",
        "Thursday–Saturday 11 AM – 6 PM, Sunday 12 PM – 5 PM. Closed Mon–Wed."),

    ("distillery-wilderness-trail.html",
        '"openingHours": "Tu-Sa 10:00-17:00"',
        '"openingHours": "Tu-Sa 09:00-17:00"',
        "Tuesday–Saturday 10 AM – 5 PM. Closed Sun–Mon.",
        "Tuesday–Saturday 9 AM – 5 PM. Closed Sun–Mon."),

    ("distillery-town-branch.html",
        '"openingHours": "Mo-Sa 10:00-18:00, Su 12:00-18:00"',
        '"openingHours": "Mo 09:30-17:00, Th-Sa 09:30-17:00, Su 11:30-17:00"',
        "Monday–Saturday 10 AM – 6 PM, Sunday 12 PM – 6 PM",
        "Monday, Thursday–Saturday 9:30 AM – 5 PM, Sunday 11:30 AM – 5 PM. Closed Tuesday–Wednesday."),

    ("distillery-preservation.html",
        '"openingHours": "Th-Sa 10:00-17:00, Su 12:00-17:00"',
        '"openingHours": "Mo-Sa 09:30-17:00, Su 09:30-16:00"',
        "Thursday–Saturday 10 AM – 5 PM, Sunday 12 PM – 5 PM. Closed Mon–Wed.",
        "Monday–Saturday 9:30 AM – 5 PM, Sunday 9:30 AM – 4 PM"),

    ("distillery-boone-county.html",
        '"openingHours": "Th-Sa 10:00-17:00, Su 12:00-17:00"',
        '"openingHours": "Tu-Sa 10:00-17:30, Su 11:00-17:00"',
        "Thursday–Saturday 10 AM – 5 PM, Sunday 12 PM – 5 PM (check website)",
        "Tuesday–Saturday 10 AM – 5:30 PM, Sunday 11 AM – 5 PM. Closed Monday."),

    ("distillery-mb-roland.html",
        '"openingHours": "Mo-Sa 09:00-17:00"',
        '"openingHours": "Mo-Th 10:00-18:00, Fr-Sa 09:00-20:00, Su 13:00-18:00"',
        "Monday–Saturday 9 AM – 5 PM (check website for seasonal hours)",
        "Monday–Thursday 10 AM – 6 PM, Friday–Saturday 9 AM – 8 PM, Sunday 1 PM – 6 PM"),

    ("distillery-barrel-house.html",
        '"openingHours": "Mo-Su 11:00-17:00"',
        '"openingHours": "Mo-Sa 11:00-18:00, Su 12:00-18:00"',
        "Daily 11 AM – 5 PM (check website for current hours)",
        "Monday–Saturday 11 AM – 6 PM, Sunday 12 PM – 6 PM"),

    ("distillery-kentucky-artisan.html",
        '"openingHours": "Tu-Fr 10:00-16:00, Sa 10:00-14:00"',
        '"openingHours": "Tu-Sa 10:00-16:00, Su 12:00-16:00"',
        "Tuesday–Friday 10 AM – 4 PM, Saturday 10 AM – 2 PM (Closed Sun–Mon)",
        "Tuesday–Saturday 10 AM – 4 PM, Sunday 12 PM – 4 PM. Closed Monday."),

    ("distillery-rd1-spirits.html",
        '"openingHours": "Mo-Th 11:00-18:00, Fr-Sa 11:00-19:00, Su 12:00-18:00"',
        '"openingHours": "Mo-Th 11:00-18:00, Fr-Sa 11:00-19:00, Su 13:00-18:00"',
        "Mon–Thu 11 AM – 6 PM, Fri–Sat 11 AM – 7 PM, Sun 12 PM – 6 PM (Closed Wed)",
        "Mon–Thu 11 AM – 6 PM, Fri–Sat 11 AM – 7 PM, Sun 1 PM – 6 PM"),

    ("distillery-hartfield.html",
        '"openingHours": "Tu-Sa 10:00-18:00"',
        '"openingHours": "Mo 13:00-17:00, Tu-Sa 09:00-17:00"',
        "Tuesday–Saturday 10 AM – 6 PM (check website for current hours)",
        "Monday 1 PM – 5 PM, Tuesday–Saturday 9 AM – 5 PM. Closed Sunday."),

    ("distillery-dueling-grounds.html",
        '"openingHours": "Tu-Sa 10:00-17:00"',
        '"openingHours": "Mo-Th 10:00-18:00, Fr-Sa 10:00-19:00, Su 14:00-19:00"',
        "Tuesday–Saturday 10 AM – 5 PM (check website for current hours)",
        "Monday–Thursday 10 AM – 6 PM, Friday–Saturday 10 AM – 7 PM, Sunday 2 PM – 7 PM"),

    ("distillery-casey-jones.html",
        '"openingHours": "Tu-Sa 10:00-17:00"',
        '"openingHours": "Mo-Th 10:00-18:00, Fr 10:00-19:00, Sa 10:00-21:00, Su 12:00-18:00"',
        "Tuesday–Saturday 10 AM – 5 PM (check website, hours may vary)",
        "Monday–Thursday 10 AM – 6 PM, Friday 10 AM – 7 PM, Saturday 10 AM – 9 PM, Sunday 12 PM – 6 PM"),

    ("distillery-rabbit-hole.html",
        '"openingHours": "We-Sa 11:00-18:00, Su 12:00-17:00"',
        '"openingHours": "Tu-Sa 10:00-17:00"',
        "Wednesday–Saturday 11 AM – 6 PM, Sunday 12 PM – 5 PM. Closed Mon–Tue.",
        "Tuesday–Saturday 10 AM – 5 PM. Closed Sunday and Monday."),

    ("distillery-peerless.html",
        '"openingHours": "We-Sa 10:00-17:00, Su 12:00-17:00"',
        '"openingHours": "Mo-Th 10:00-18:00, Fr-Sa 10:00-17:00"',
        "Wednesday–Saturday 10 AM – 5 PM, Sunday 12 PM – 5 PM. Closed Mon–Tue.",
        "Monday–Thursday 10 AM – 6 PM, Friday–Saturday 10 AM – 5 PM. Closed Sunday."),

    ("distillery-makers-mark.html",
        '"openingHours": "Mo-Sa 09:30-17:00, Su 11:30-17:00"',
        '"openingHours": "Mo-Su 09:30-17:00"',
        "Monday–Saturday 9:30 AM – 5 PM, Sunday 11:30 AM – 5 PM",
        "Daily 9:30 AM – 5 PM"),

    ("distillery-glenns-creek.html",
        '"openingHours": "Th-Sa 10:00-16:00"',
        '"openingHours": "Mo-Sa 10:00-17:00, Su 11:00-17:00"',
        "Thursday–Saturday 10 AM – 4 PM (limited hours, call ahead)",
        "Monday–Saturday 10 AM – 5 PM, Sunday 11 AM – 5 PM"),

    ("distillery-stitzel-weller.html",
        '"openingHours": "We-Mo 10:00-18:00"',
        '"openingHours": "Mo 10:00-18:00, We-Sa 10:00-18:00, Su 12:00-18:00"',
        "Wed–Sat 10 AM – 6 PM, Sun 12 PM – 6 PM, Mon 10 AM – 5 PM (Closed Tues)",
        "Monday, Wednesday–Saturday 10 AM – 6 PM, Sunday 12 PM – 6 PM. Closed Tuesday."),

    ("distillery-michters.html",
        '"openingHours": "Th-Mo 11:00-19:00"',
        '"openingHours": "Mo-Sa 10:00-19:00, Su 13:00-19:00"',
        "Thursday–Monday 11 AM – 7 PM. Closed Tue–Wed.",
        "Monday–Saturday 10 AM – 7 PM, Sunday 1 PM – 7 PM"),
]

changed = []
errors = []

for fname, old_schema, new_schema, old_body, new_body in UPDATES:
    path = os.path.join(BASE, fname)
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        original = content
        content = content.replace(old_schema, new_schema)
        content = content.replace(old_body, new_body)
        if content == original:
            errors.append(f"NO MATCH: {fname}")
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            changed.append(fname)
    except Exception as e:
        errors.append(f"ERROR {fname}: {e}")

print(f"Updated {len(changed)} files:")
for f in changed:
    print(f"  OK: {f}")
if errors:
    print(f"\nProblems ({len(errors)}):")
    for e in errors:
        print(f"  {e}")
