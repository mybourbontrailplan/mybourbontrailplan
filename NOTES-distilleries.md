# Venue & Content Accuracy Notes

Per-venue facts, corrections and traps. **Read the entry for any venue you are about to write about.** These are things that have been got wrong before, usually because a plausible-sounding assumption was wrong.

`CLAUDE.md` holds the rules; this file holds the facts. If something here contradicts a rule in CLAUDE.md, CLAUDE.md wins and this file needs fixing.

**Verify before trusting.** Everything here was true when written. Entries carry a date where it matters. If an entry names a file, a section or a piece of copy, confirm it still exists before relying on it, especially entries tagged `[UNVERIFIED]` or `[NEEDS CHECK]`.

---

## Venues with two locations (the most common source of error)

Four brands run two venues each, and copy regularly attributes one's hours, phone or address to the other.

### Bardstown Bourbon Company
1. **Bardstown campus**, 1500 Parkway Dr. The working distillery and full tour. `distillery-bardstown-bourbon-co.html`. Hours Mo-Tu 10-3, We-Su 9-5.
2. **Louisville tasting room**, 730 W Main St on Whiskey Row. `distillery-bardstown-bourbon-co-louisville.html`. Phone (502) 791-6575, **Mo-Sa 11-7, closed Sunday**. Directory-only, no map pin.

Nothing is distilled in Louisville. Do not reuse the campus's hours or address on the Louisville page. The Louisville room's draw is Louisville-only exclusive releases plus staff who explain BBC's sourcing and collaboration model well; Value scored 7.0, the lowest of the tasting rooms, so the copy says plainly that you pay for what you get. The Whiskey Row guide's BBC stop linked to the *Bardstown* profile until July 2026; fixed.

### Green River (both locations are Official Trail)
1. **Owensboro**, 10 Distillery Rd. The working distillery. `distillery-green-river.html`. Phone (270) 691-9001, hours We-Sa 9-5.
2. **Louisville tasting room**, 714 W Main St, opened 2025. `distillery-green-river-louisville.html`. Phone (502) 804-5383, Tue-Sat 11-7, **closed Sunday and Monday**.

Kyle verified against the KDA/KBT site in July 2026 that **both** locations are listed on the official trail, so both carry the Official Trail badge. Nothing is distilled in Louisville. Do not cross-contaminate the phone numbers or hours. Louisville's signature experience is Fill-Your-Spirits, $15 per person plus the cost of a bottle, and which barrel is open varies.

### Chicken Cock
1. **Circa 1856 Bardstown**, 103 E Stephen Foster Ave, opened 2024. The main venue and the one `distillery-chicken-cock.html` covers.
2. **"The Coupe"**, NuLu, Louisville. A speakeasy/cocktail destination, relaunched March 2026. A separate venue, *not* the Bardstown one.

The main venue is in **Bardstown, not Lawrenceburg** (Lawrenceburg is Wild Turkey). The Whiskey Row guide asserted "the Lawrenceburg tasting room" and was corrected July 2026. Nothing is distilled at either: Chicken Cock is "crafted in partnership with Bardstown Bourbon Company", which is why the Bardstown venue is `data-production="tasting"` despite the card calling it a micro-distillery. **Rating 7.0** — the bar is smaller than expected and the accessible area is limited to the bar plus two front gift shop rooms. The old fashioned flight is a highlight worth mentioning.

### Monk's Road Boiler House
`distillery-monks-road-boiler-house.html`. Log Still's Louisville outpost at 131 W Main St on Whiskey Row, opened July 2024, phone (502) 230-6600. Fine dining plus tasting room in a restored industrial space; the first distillery tasting room on the Row to offer full dining. The whiskey is distilled at Log Still in New Haven (`distillery-log-still.html`), so this is directory-only, no map or trip-builder pin. Uses the **Food & Dining** bar in place of Gift Shop. Rating 8.4.

**Hours are the trap.** Open seven days but the opening time moves: Mo-We 3 PM, Th 12 PM, Fr-Sa 12 PM (to 11:45 PM, the latest kitchen on the Row), Su 5 PM. **It is only a lunch option Thursday through Saturday.** The walking guide called it "a natural lunch" flatly and its route block listed it under Lunch with no caveat; both were corrected July 2026. Do not reintroduce an unqualified lunch recommendation.

---

## Official-trail status and badges

- **Buffalo Trace is NOT an official Kentucky Bourbon Trail member.** Sazerac left the KDA in 2009 and never rejoined. Its profile badge and any card or label must say "Independent" / "Independent Distillery", never "Official Trail" or "Official Bourbon Trail". A leftover official badge on the profile was caught and fixed July 2026. This is worth stating positively in copy, because readers find it surprising and it is a genuinely useful fact.
- **General George Stillhouse** carries the **Official Trail** badge (joined KBT January 2026). It is a craft producer *and* on the official trail; both are true and not in conflict.
- **Pensive Distilling Co.** carries the **Official Trail** badge (confirmed July 2026). `data-type` stays `craft` in `distilleries.html` because it is a small producer; only the display badge says Official Trail.
- **Becker & Bird Distillery** — `distillery-baker-bird.html`. The distillery's official KBT name is **Becker & Bird**; the winery on the same property is called **Baker-Bird**. The filename stays as-is for URL continuity. Do not "fix" the filename.

---

## Individual venue detail

### Augusta Distillery
`distillery-augusta.html`. Separate from Becker & Bird, also in Augusta KY, at 207 Seminary Ave. Produces Buckner's bourbon (Best Bourbon at the 2023 San Francisco World Spirits Competition). **Wed-Sat 11-5 only.** Rating 8.1. River Proof Barrel Experience ($29) is the signature tour. Trip builder pin lat 38.7731, lng -83.9968. Smart pairing: Augusta + Becker & Bird, a 5-minute walk apart.

### General George Stillhouse & Distillery
`distillery-general-george.html`. Western KY craft distillery at Falls of Rough, Grayson County, 1867 Junction Rd. Land once owned by George Washington. Joined KBT January 2026. Produces Founding Fox bourbon, gin and vodka, plus Shakertown Spirits and Bluefield Bourbon. Three tours: Ambassador's Tour + Thieving (1 hr, top pick), Founding Fox Tasting & Tour (40 min), Tasting in the Fox Den (30 min). **Pricing is not published** — booking goes through generalgeorgestillhouse.setmore.com. Rating 7.0. Phone (702) 505-9481. Trip builder pin lat 37.5546, lng -86.5132, corrected July 2026 to the geocoded 1867 Junction Rd address (was 37.5607, -86.5326). Smart pairing: General George + Green River, about 50 minutes.

### Pensive Distilling Co.
`distillery-pensive.html`. Newport KY craft distillery in a historic Prohibition-era building. **Speakeasy tasting room requires a password**, provided at booking. Named after Pensive, the 1944 Kentucky Derby and Preakness winner. The on-site kitchen is award-winning (City Beat Top 10 NKY Restaurants) and every menu item is named after a racehorse. Live music Fridays. Tours $15-$25, easy booking via Peek. Rating 8.0. Pair with New Riff, 5 minutes, same city. Trip builder pin lat 39.09, lng -84.4923, corrected July 2026 to the 720 Monmouth St Newport address (was 38.9928, -84.4969, which sat about 6.7 mi south of Newport). Region Northern (Newport maps to Northern in `RG`).

### Stitzel-Weller gift shop
**Old Fitzgerald is now a Heaven Hill brand, produced in Bardstown, and is NOT available at Stitzel-Weller.** The gift shop reliably carries Blade & Bow, I.W. Harper and Bulleit. Orphan Barrel releases show up occasionally but cannot be counted on, so do not present them as a reliable find. The Old Fitzgerald history is fine as historical context (it was produced there), but do not imply visitors can buy it there.

### WhistlePig The Vault
Louisville tasting room at 403 E Market St (NuLu, near Angel's Envy), opened 2026. Vermont-based, rye-focused, not a Kentucky distillery. **In scope for a tasting-room profile plus a directory card** (decision reversed July 2026: it was previously excluded as "a brand experience room, not a production facility", but that is exactly what `data-production="tasting"` now encodes, so the reason expired once the directory could represent the distinction). Directory-only like every urban tasting room: no trip-builder or map pin.

Key detail: the original 1911 bank pneumatic tube system is used to mix and deliver drinks, visibly in action from your seat. Tasting tiers: $50 hosted (groups 4-10), $250 Vault Collection, $300 Vault Experience (up to 6 guests). Hours Tue-Sat 10am-5pm. Cocktail bar is walk-in; seated tastings require a reservation.

**[NEEDS CHECK] The profile page does not exist yet.** As of August 2026 WhistlePig is covered only as a callout card in the "Speakeasies & New Openings" section of `louisville-whiskey-row-walking-guide.html`, and is referenced as plain text (not a link) on `embed-bourbon-trail-map.html` and the Louisville regional map page. Once the profile ships, those references should become links.

### Closed and excluded venues
- **Garrard County Distilling Co.** — SHUT DOWN. `distillery-garrard-county.html` remains in the repo but must NOT be added to the site anywhere.
- **Barton 1792** — not open to the public. `distillery-barton-1792.html` exists but is intentionally excluded from `distilleries.html`, `trip-builder.html`, `map.html` and `sitemap.xml`.
- **Three Boys Farm Distillery** is now **Whiskey Thief Distilling Co.**

### Geography traps
- **Log Still is in New Haven, KY**, not New Hope. Kyle's Airbnb is in New Hope. Different places, about a mile apart.

---

## Restaurants and food

- **The Rickhouse Restaurant & Lounge is in BARDSTOWN**, 112 Xavier Dr. Dinner only, closed Mondays. A legitimate bourbon-forward dinner spot. **NEVER present it as a Frankfort option** — it turns up in Frankfort search results and has been misfiled before.
- **Rick's White Light Diner (Frankfort)** — appears closed as of late 2025. Do not recommend.
- **Bourbon on Main (Frankfort)** — verified Frankfort lunch option, bourbon-focused. Used as the Day 3 lunch recommendation, replacing a nonexistent "Rick House" in Frankfort. Appears in the itinerary, eat-and-drink, where-to-stay, and the Castle & Key nearby card.
- **Wallace Station** — deli and bakery at Midway, near Woodford Reserve. Excellent sandwiches, popular with locals, so arrive before the lunch rush. The reliable food recommendation for the Lexington/Versailles corridor.
- **Heaven's to Betsy Bakery** — Lawrenceburg, scratch bakery and lunch spot, and the Reuben is one of the best Kyle has had anywhere. Small place, locals know about it, so go early. On `eat-and-drink-bourbon-trail.html` in the On the Road section, plus a Wild Turkey nearby card. **It was originally added 31 March 2026, silently destroyed on 8 April by the Google Drive overwrite (see the incident note in CLAUDE.md), and restored from history in August 2026.** If it disappears again, that is the signature of the same problem, not an editorial decision.
- **[GAP] `eat-and-drink-bourbon-trail.html` has no Lexington section.** It covers Louisville, Bardstown, Frankfort and "On the Road". Meanwhile `distillery-dark-arts.html` asserts Lexington has the best dining on the trail outside Louisville. The Lexington regional map page handles this honestly rather than inventing restaurants. A Lexington section is the obvious follow-up.

---

## Booking data provenance (July 2026, restated August 2026)

Booking tiers and lead times for the ten majors (Buffalo Trace, Angel's Envy, Maker's Mark, Woodford Reserve, Old Forester, Wild Turkey, Four Roses, Heaven Hill, Evan Williams, Jim Beam) were verified against official distillery reservation pages in July 2026.

**Buffalo Trace** releases new dates weekly on **Wednesdays at 10:00 AM Eastern**, each release covering a 7-day window about 8 weeks out. Never describe it as having "no drop day" or opening "Monday mornings". Tours are free, which is exactly why they are the hardest reservation in Kentucky.

**Jim Beam** main-line distillation at Clermont is **paused for 2026**. Tours, tastings and the Kitchen Table are all still operating.

**[UNVERIFIED] Hours blocks** on `distillery-wild-turkey.html`, `distillery-wilderness-trail.html`, `distillery-hartfield.html` and `distillery-kentucky-artisan.html` still carry the copy-pasted template pattern and have never been verified against the venues. Next verification pass due before the 2027 index refresh.

---

---

## [NEEDS KYLE] Content lost in the April 2026 Drive overwrite, not yet restored

Two items were deleted by commit `b6f383c` and deliberately **not** restored, because the copy is from April 2026 and makes factual claims about facilities and tours that may have changed since. Confirm they are still accurate, then restore from `git show b6f383c~1:<file>`.

1. **Heaven Hill: the Springs Distillery and the Heritage Rising Tour.** The removed copy said Heaven Hill's brand-new **$200M Springs Distillery opened September 2025**, marking the return of distilling to Bardstown, and listed a **Heritage Rising Tour** of it. Also removed: a nearby card for **Five Brothers Bar & Kitchen**, described as a good spot after your tasting. If the tour still runs, this is strong content that the profile currently lacks entirely.
2. **Woodford Reserve: the Barrel to Bottle Experience.** Described as their premium deep-dive, covering the full process from raw grain to finished bottle. Check whether it is still offered and at what price before restoring.

Also worth knowing: the same overwrite removed coordinate and schema values that have since been superseded, so do not blanket-restore that commit. Only these two content items are outstanding.

---

## Editorial stance

- Kyle has real bourbon trail experience. The site reflects honest, opinionated reviews from actual visits, which is the entire premise.
- Distilleries **can** pay for featured listings but **cannot** change ratings. This is disclosed on the About page.
- Visitor stat: "Record 2.7 million annual visitors and growing" — safe to use as evergreen.
- The budget guide uses **per-person** pricing throughout.
