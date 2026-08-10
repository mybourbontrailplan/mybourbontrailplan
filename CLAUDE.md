# CLAUDE.md — mybourbontrailplan.com

Kyle's Kentucky Bourbon Trail trip-planning site. Static HTML/CSS/JS, deployed on Netlify via GitHub auto-deploy. Also a content funnel for Kyle's Airbnb (New Hope Bourbon Stop, near Bardstown).

**This file is rules and workflow. Two companion files hold the detail:**

| File | Read it when |
|---|---|
| `NOTES-distilleries.md` | Writing about any specific venue, restaurant or booking detail. Contains the corrections and traps. |
| `NOTES-internals.md` | Working inside `trip-builder.html`, `map.html`, the icon system, or the PDF generator. |

**Run `python scripts/check_site.py` before you commit.** It enforces most of the mechanical rules below (em dashes, title/meta lengths, canonicals, required scripts, schema shape, link integrity, excluded pages, rating drift). If a rule can be checked, it is checked there rather than relied on from memory.

**Do not put counts in this file.** Numbers of distilleries, pages or icons go stale and this file has been wrong about all three. Derive them: `check_site.py` prints current counts.

---

## Deployment

**Repo:** github.com/mybourbontrailplan/mybourbontrailplan. Workflow is `git pull` → make changes → stage → commit → push.

**Deploying is just pushing** — Netlify auto-builds on every push to `main`. There is no deploy command. **Do NOT run `netlify deploy --prod --dir=.`**; the CLI is not installed (`netlify` is not on PATH) and is not needed. That step used to be documented here and always failed, because the push had already deployed the site. The `.netlify/` folder is leftover state from a one-time CLI use, not active config.

### 1. Regenerate the sitemap, if pages were added, removed or noindex-toggled
```
python scripts\generate_sitemap.py
```
Scans root-level HTML, applies the blocklist and noindex exclusions, writes a fresh `sitemap.xml`. Commit it with the rest of the deploy. Skip for CSS-only or content-only edits to existing pages.

### 2. Push
```
git add <the files you changed>
git commit -m "message"
git push origin main
```
Stage files explicitly rather than `git add .` — the working tree usually carries local-only noise (`.claude/settings.local.json`, `.claude/worktrees/`).

### 3. Verify it landed, against VISIBLE TEXT not markup
```
$r = Invoke-WebRequest -Uri "https://mybourbontrailplan.com/{page}.html?cachebust=$(Get-Random)" -UseBasicParsing
$r.Content -match '{a string your change added}'
```

**Netlify post-processes the HTML it serves, so the deployed source is not byte-identical to the repo.** Confirmed repeatedly:
- `.html` extensions are stripped: `href="distillery-x.html"` is served as `href='/distillery-x'`.
- `href="index.html"` becomes `href='/'`.
- Double quotes become single quotes, **and attributes get reordered**: `<a href="index.html" class="logo">` is served as `<a class='logo' href='/'>`.

So grepping for `href="foo.html"`, `class="dist-card"`, or an attribute pair in a particular order returns **zero and looks like a failed deploy when the deploy was fine.** This has burned multiple debugging cycles, most recently a live rating verification that appeared to fail because `class` now precedes `href`. Grep for **prose the change introduced**, a rendered label, or an extension-less fragment. Also beware strings that span a tag: `"not an official member"` fails if the copy is `not <strong>an official</strong> member`.

### 4. Submit to IndexNow, immediately
```
python scripts\indexnow_submit_changed.py
```
Non-negotiable for deploys with HTML changes; the site leans heavily on Bing. Wait for the step-3 live check to pass **first** — pinging before the deploy finishes makes crawlers re-index the old content. Paste the output back to the user; do not swallow it. HTTP 200 and 202 are both success; anything else, surface it.

**Skip only if:** no HTML changed (CSS/JS-only), the deploy is a rollback or no-op, or the script already ran for this commit.

**Use `python scripts\indexnow_bulk_submit.py` instead when 20+ HTML files changed** (site-wide template updates), to avoid per-URL rate limits. It submits every sitemap URL.

**Gotcha: back-to-back commits silently drop URLs.** The script hardcodes `git diff --name-only HEAD~1 HEAD`, so it only ever sees the **most recent commit**. If a second commit lands before you run it, the first commit's URLs are never submitted and nothing warns you. This has happened at least twice. Run it immediately after each push. If two commits already landed, submit the missed URLs manually, reusing the script's own functions so the key and payload stay identical:
```python
import importlib.util
spec = importlib.util.spec_from_file_location("m", "scripts/indexnow_submit_changed.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.submit(["https://mybourbontrailplan.com/foo.html"], m.load_key())
```

---

## Tech stack

- Static HTML/CSS/JS. **No build tools, no framework, no CMS** — every page is a standalone HTML file at root level.
- Fonts: DM Sans (body) + Fraunces (display).
- Maps: Leaflet.js with CartoDB Light tiles. SortableJS 1.15.6 for trip-builder drag-to-reorder, loaded from unpkg after Leaflet.
- QR codes: `js/qr.js`, a vendored encoder. See "Printable QR cards" below.
- Analytics: GA4 `G-DVK4D6KJJP` on all pages. Custom events: `email_signup`, `trip_builder_complete`, `share_link_copied`, `plan_loaded_from_link`, `affiliate_click`, `embed_load`, `embed_snippet_copied`, `host_toolkit_generate`.
- Email: MailerLite, account 2164831, universal script on every page after the GA script.
- Affiliates: CJ Affiliate for Booking.com and VRBO, direct Airbnb.
- Contact and About render the email address in JS to prevent scraping/mangling.
- Search Console verified via meta tag on all pages.

## Design system

- Primary blue `#1B4F72`, accent gold `#D4A03C`, dark `#0E2F44`.
- CSS variables: `--primary`, `--primary-light`, `--primary-dark`, `--accent`, `--accent-light`, `--font-display`, `--font-body`, `--text`, `--text-secondary`, `--text-light`, `--border`, `--bg-subtle`.
- Modern, clean, SaaS-inspired. White backgrounds, subtle shadows, 12px radius.
- Icons: brand SVGs in `images/icons/`. Full rules in `NOTES-internals.md`.

---

## File structure

Root-level HTML pages, an `images/` folder (distillery photos named `{distillery}-N.jpg`, EXIF-fixed, max 1200px, ~80% JPEG), `images/icons/` for brand SVGs, `js/` for vendored scripts, and `scripts/` for Python tooling.

**Core pages:** `index.html`, `3-day-bourbon-trail-itinerary.html` (flagship SEO page, 2/3/4-day selector), `distilleries.html` (filterable directory, sort by rating/A-Z; the count is set dynamically on load by `applyFilters()`), `map.html`, `trip-builder.html`, `bourbon-trail-booking-guide.html`, `bourbon-trail-budget-guide.html`, `where-to-stay-bourbon-trail.html`, `guides.html`.

**Content:** `eat-and-drink-bourbon-trail.html`, `about.html` (monetisation disclosure), `contact.html`.

**Guides:** `best-time-to-visit-bourbon-trail.html`, `bourbon-trail-non-bourbon-drinkers.html`, `louisville-whiskey-row-walking-guide.html`, `bourbon-trail-transportation-guide.html`, `kentucky-bourbonfest.html`, `kentucky-whiskey-trail.html`, `bourbon-trail-bachelor-party-guide.html`, `buffalo-trace-gift-shop-guide.html`.

**Map pages:** `map.html` (full interactive), `printable-bourbon-trail-map.html` (PDF landing page), `embed-bourbon-trail-map.html` (widget + host toolkit), and four regional pages `bourbon-trail-map-{louisville,bardstown,frankfort,lexington}.html`.

**Distillery profiles:** `distillery-{name}.html`, one per venue. Two files exist but are **excluded from the site everywhere** (`distilleries.html`, `trip-builder.html`, `map.html`, `sitemap.xml`): `distillery-garrard-county.html` (shut down) and `distillery-barton-1792.html` (not open to the public).

**Other:** `sitemap.xml` (generated), `_redirects` (see below), `bourbon-trail-planning-checklist.pdf` (lead magnet), `bourbon-trail-map.pdf` (generated).

### Google Drive: resolved 10 August 2026, but read this before trusting old history

**The repo now lives at `C:\dev\mybourbontrailplan`, outside any synced folder.** It used to sit inside Google Drive, which destroyed published content once (below). Moving it out is the fix, and it is done: GitHub already provides the versioning and off-machine backup Drive was duplicating, so keep the repo out of Drive, Dropbox, OneDrive and any other sync root.

Two habits survive the move and are still worth keeping:
- **Never `git add .` here.** Stage explicitly. That advice appears in the deployment section too; this is why.
- **`git ls-files` beats a bare glob** for any sweep, because of `.claude/worktrees/`.

`check_site.py` still warns if a ` (1)` duplicate or `.tmp.driveupload/` appears in the tree. That should now never fire; if it does, something re-synced the repo into Drive and the working copy may not be what you think.

**The incident (commit `b6f383c`, 8 April 2026, "trip builder updates").** A `git add .` swept **228 `.tmp.driveupload/` files** plus two ` (1)` duplicates into a single commit that *also* restored **older copies of several HTML files over newer ones**. 252 files changed, 621 deletions, under a message about the trip builder. It silently deleted published content that nobody noticed for four months:

- The Heaven's to Betsy Bakery restaurant card and its Wild Turkey nearby card
- The Larrikin nearby card on Wild Turkey, 0.2 mi apart
- Buzzard's Roost nearby cards on Evan Williams, Michter's and Old Forester
- Heaven Hill's Springs Distillery and Heritage Rising Tour content
- Woodford's Barrel to Bottle Experience

A second commit the same day (`c9efa97`) has the identical signature. All of the above except the Heaven Hill and Woodford items were restored from `b6f383c~1` in August 2026.

**Why it stayed invisible for four months, which is the reusable lesson.** Nothing compared the site against itself, so a silent deletion read as normal. `check_site.py` now asserts that distilleries within 0.25 mi of each other cross-link, which is exactly what would have caught the Larrikin and Buzzard's Roost losses. Prefer checks of that shape - an invariant the content must satisfy - over trusting that a diff was reviewed.

**Commits before August 2026 may contain silent reverts.** When archaeology takes you into that history, do not assume a file's state in an old commit was intentional.

---

## Page templates

### Nav (every page)
Order: Plan Your Trip → Distilleries → Map → Where to Stay → Eat & Drink → Trip Builder → Guides → Booking Guide (CTA style). **Map must be a nav item on every new page.**

**Hamburger breakpoint is 900px site-wide.** Every page collapses `.nav-links` and shows `.mobile-menu-btn` at `max-width:900px`. Some pages retain an older `@media (max-width:640px)` block with redundant but harmless duplicate collapse lines plus that page's content rules; leave those content rules at their breakpoint.

**`.nav-links` gap is `26px`, not 32px.** Tightened deliberately so the wide lockup plus all eight links clear one line inside the 1200px cap. Do not raise it — the nav wraps to two lines above ~1200px if you do.

**Header logo, three tiers** via `<picture>` (first match wins):
```html
<a href="index.html" class="logo"><picture><source media="(max-width:900px)" srcset="images/bourbon-trail-planner-nav.svg?v=4"><source media="(max-width:1199px)" srcset="images/bourbon-trail-planner-icon.svg?v=4"><img src="images/bourbon-trail-planner-nav.svg" alt="Bourbon Trail Planner" class="logo-lockup" style="height:40px;width:auto;display:block"></picture></a>
```
Plus, in the `<style>` block: `@media (max-width:900px){.nav-links{display:none;}.mobile-menu-btn{display:block;}.logo-lockup{width:min(72vw,300px)!important;height:auto!important;}}` — the `!important` is required to beat the inline `height:40px`.

- **≥1200px** → full lockup at 40px height (the `<img>` default, no `<source>` matches).
- **901–1199px** → 40px pin icon with the full link row. The lockup would blow past the 1200px `.nav-inner` cap here; the icon frees ~260px so the nav stays on one line.
- **≤900px** → full lockup again at `width:min(72vw,300px)`, so the wordmark stays legible and clears the hamburger on a 375px phone.

Brand assets in `images/`: `bourbon-trail-planner-nav.svg` (wide lockup), `bourbon-trail-planner-icon.svg` (pin-only, `viewBox="74 88 364 364"`), plus `-nav-reversed.svg` and `-lockup*.svg`. The homepage footer uses `-nav-reversed.svg` at 36px; leave it alone when batch-editing headers.

**Favicon chain** in every `<head>`, versioned to bust caches. Bump `?v=` on all three **and** the `<picture>` srcset together when the icon art changes:
```html
<link rel="icon" type="image/svg+xml" href="/images/bourbon-trail-planner-icon.svg?v=4">
<link rel="icon" type="image/png" sizes="32x32" href="images/favicon-32.png?v=4">
<link rel="apple-touch-icon" sizes="180x180" href="images/apple-touch-icon-180.png?v=4">
```

### Footer, two variants
**Homepage only:** multi-column grid (Plan / Explore / Resources) with custom classes (`.footer-inner`, `.footer-col`) and a `.footer-bottom` bar.

**Every other page:** single-row flexbox, all nav links inline, Instagram handle line, copyright. No custom footer CSS needed. Copy the block from any interior page such as `distilleries.html`; the `<footer>` element itself takes its background from that page's CSS.

### Required on every page
GA script, MailerLite universal script (after GA, before `</body>`), correct self-canonical, OG tags, favicon chain, and `-webkit-text-size-adjust: 100%` in the `html` rule (iOS Safari text inflation). `check_site.py` verifies all of these.

**GA must be exactly two separate `<script>` tags:** (1) `<script async src="https://www.googletagmanager.com/gtag/js?id=G-DVK4D6KJJP"></script>` and (2) the inline `dataLayer` / `gtag('config', ...)` block. **Never nest one `<script>` inside another** — the parser misreads it, the JS throws, and `gtag` is undefined for the whole page.

**All `gtag(...)` calls must be guarded:** `if(typeof gtag==='function'){gtag(...)}`, so a blocked tracker can never abort a user-facing action like opening a modal or firing a mailto.

---

## Distillery profiles

Use `distillery-buffalo-trace.html` as the template reference. Every profile needs the standard furniture above plus `TouristAttraction` JSON-LD (see `scripts/add_schema.py` for the structure).

- **`@type` must be the array `["TouristAttraction", "LocalBusiness"]`.** `openingHours` is a `LocalBusiness` property; a single string type triggers a schema.org validator warning.
- **Never add a `review` or `reviewRating` block.** Self-authored ratings violate Google's review-snippet policy and cause Rich Results Test critical errors.
- Photo gallery sits between "What to Expect" and "Tour Options", using `.photo-gallery` / `.gallery-grid`. Photos are `images/{distillery}-N.jpg` with `loading="lazy"`. Use `aspect-ratio: 4/3` with `object-fit: cover`, never a fixed height. Grid is `repeat(3, 1fr)` for three photos, `repeat(2, 1fr)` for four. Each gallery page includes a `.gallery-lightbox` div plus click-to-expand JS before `</body>`.
- Nearby pairing cards must link to real profile pages, never `href="#"`. Restaurant cards link to `eat-and-drink-bourbon-trail.html`; sidebar region guides link to `guides.html`.
- **Profiles have no date surfaces.** `TouristAttraction` carries no `dateModified` and profiles have no `.article-meta` bar. Do not add date fields just to have them.

### Sidebar Contact section, fixed order
1. `<a href="map.html?distillery={slug}" class="sidebar-link">See on Map &rarr;</a>` — always first
2. Phone row (`.sidebar-row`) — in Contact only, **not** in Quick Details
3. Official website link

**No Google Maps links** — the `map.html?distillery={slug}` deep link replaces them. Do not add `google.com/maps` URLs to the sidebar. Phone lives in Contact only, removed from Quick Details to kill the duplication.

### Internal linking conventions
- Every profile links to `map.html?distillery={slug}` via the sidebar "See on Map".
- Guide pages link to `map.html?region={region}` **in context**, not as a nav item. Currently done on: `where-to-stay-bourbon-trail`, `3-day-bourbon-trail-itinerary`, `eat-and-drink-bourbon-trail`, `louisville-whiskey-row-walking-guide`, `kentucky-bourbonfest`, `bourbon-trail-non-bourbon-drinkers`.
- Style inline region map links in guide body copy as `style="color:var(--primary-light);font-weight:500;"`.

### Ratings: six bars, two label sets
Every profile's "Our Honest Ratings" block uses **exactly six bars in this order**. Bars 2, 4, 5 and 6 are identical everywhere; **only bars 1 and 3 change** by venue class:

| # | Working distillery | Urban tasting room |
|---|---|---|
| 1 | Tour Quality | **Experience Quality** |
| 2 | Value for Money | Value for Money |
| 3 | Campus & Grounds | **Space & Atmosphere** |
| 4 | Gift Shop | Gift Shop |
| 5 | Booking Ease | Booking Ease |
| 6 | Crowd Level | Crowd Level |

- **Which set is an editorial judgment, NOT `data-production`.** Use the tasting-room labels only for an urban room with no grounds and no tour. `distillery-stitzel-weller.html` is tagged `tasting` but is a historic campus with real grounds and tours, so it correctly keeps the distillery labels. Currently on tasting-room labels: Dark Arts, Whiskey Thief (Louisville), Fresh Bourbon, Chicken Cock.
- **Why two sets:** the old rule forced all six distillery labels onto every venue and told you to silently reinterpret them. That produced Dark Arts scoring 9.0 for "Campus & Grounds" at a blending house with no campus — the number was right, the label was lying. Four of six bars stay identical **on purpose** so headline ratings stay comparable. Do not widen this into a separate tasting-room scale.
- **Relabelling is not re-rating.** When the two sets were introduced the existing urban rooms kept their scores, because the scores already encoded the reinterpreted meaning. If you move a venue between sets, change the label and leave the number alone.
- **Ratings score the VISIT, never the whiskey.** No "Whiskey Quality" bar, and do not grade how the bourbon tastes in body copy or the verdict either. If the whiskey is the story, make it a *recommendation* ("the old fashioned flight is the thing to order"), not a score. Buzzard's Roost and Dark Arts both had a Whiskey Quality bar; a reader emailed about the inconsistency and both were normalised.
- **The "Food & Dining" swap (bar 4)** replaces Gift Shop at exactly two venues where the kitchen is the reason to visit: `distillery-pensive.html` and `distillery-monks-road-boiler-house.html`. This is a **narrow, named exception**. Confirm with Kyle before applying it to a third venue.
- **Never invent a rating.** Every card carries a number and every profile six bars plus a verdict; these are Kyle's editorial judgments from real visits and are the premise of the site. If Kyle has not visited, do not ship a guessed score, do not average other venues, do not infer one from press coverage. Leave an explicit TODO and ask him.
- The headline rating (`Our Rating`, e.g. `7.5 / 10`) is **editorial, not the average of the six bars.** Changing bars does not require changing the headline.

### Ratings live in THREE files and they drift
The copies are the profile's `snap-value` headline (**canonical**), the `dist-card-rating` div in `distilleries.html`, and the `rating:` field in `trip-builder.html`'s `D` array. `map.html` carries no rating, so there is no fourth copy. Changing a rating means changing all three.

**Audited August 2026: 23 disagreed.** The instructive part is the split — the **directory** was wrong in 16 cases and the **trip builder** in 7, so both secondary copies had drifted in different places and there was no single stale file. Never assume one copy is the reliable one; always resolve to the profile. Several trip-builder errors were digit transpositions (Evan Williams 7.8 stored as 8.7).

**Run `python scripts/check_ratings.py`** to detect drift (exit 1 if any), `--apply` to sync to the profile.

---

## SEO

- Canonicals point to `https://mybourbontrailplan.com/filename.html`, with the extension. The homepage is bare `https://mybourbontrailplan.com/`.
- Titles under 85 characters, meta descriptions under 170.
- Every page needs OG tags: `og:title`, `og:description`, `og:type`, `og:url`.
- **Schema by page type:** distillery profiles `["TouristAttraction","LocalBusiness"]` with `address`, `geo`, `telephone`, `openingHours`, `isAccessibleForFree`, `url`, `sameAs`; guides/articles `Article` with `url`, `mainEntityOfPage`, `author`, `publisher`, `datePublished`, `dateModified`; directory and map pages `CollectionPage` with `url` + `publisher`; homepage `WebSite` + `Organization` (two blocks); trip builder `WebApplication`; About `AboutPage`; Contact `ContactPage`. Add `FAQPage` where a page has a real FAQ.
- **author/publisher is always** `{"@type": "Organization", "name": "Bourbon Trail Planner"}` — never `Person`, never a different name.
- **datePublished/dateModified are ISO 8601 with an Eastern offset**, e.g. `2026-02-22T00:00:00-05:00`, never bare `YYYY-MM-DD`. The site stamps `-05:00` year-round for consistency, including summer dates technically on `-04:00`. Do not "fix" some to `-04:00` and leave a mixed pattern.

### Updating a guide's date: THREE surfaces, every time
On any **content** change to a guide or article, bump all three. They live in two files and forgetting one is the most repeated mistake on this site.

1. **JSON-LD `dateModified`** in the page `<head>`.
2. **The visible "Updated {Month} {Year}"** in the `.article-meta` bar under the H1.
3. **The `.guide-date` span on that guide's card in `guides.html`** — a different file, which is why it gets forgotten. Existing spans are inconsistent: most show a bare **publish** month matching `datePublished`, a few are prefixed `Updated `. If a card says `Updated `, keep the prefix and bump the month. If it shows a bare publish date, leave it unless deliberately converting. Some cards have no date span at all; that is fine, there is simply nothing to bump.

- Leave `datePublished` alone; it records original publication.
- **`guides.html` card copy goes stale too.** The card `<p>` duplicates claims from the page. On a material change, reread the blurb, not just the date.
- Skip the bump for pure style/markup edits (CSS, nav/footer templates, favicon versions). Bump for anything a reader notices: new facts, corrections, rewritten copy, added or removed sections.
- Every guide's `.article-meta` should carry a read-time item and an Updated item. Read time is roughly **200 words per minute** over the body copy.

---

## Copy style

### No em dashes, anywhere in site content
The site was fully de-em-dashed in June 2026 (1,018 instances). Use:

| Context | Replacement |
|---|---|
| `<title>`, `og:title`, JSON-LD `headline` | `: ` |
| Heading with no existing colon | `: ` |
| Heading that already contains `: ` | `, ` |
| `<strong>Label</strong> — Description` | `: ` |
| Body copy, card descriptions, meta descriptions | `, ` |
| Short connective phrases where a comma reads awkwardly | ` - ` |

`python scripts/remove_em_dashes.py` cleans a batch (e.g. after importing copy). `check_site.py` fails on any that reappear.

### Other punctuation
Regular hyphens (` - `) are fine where a comma would create a run-on. No smart/curly quotes in HTML; use straight quotes or entities.

### Never hardcode counts
Prefer removing counts entirely. Where a number is unavoidable use the rounded **"60+"** form.

- **Region totals are the worst offenders** and are banned. A per-region count must stay in sync across `map.html`'s region cards, the four regional pages (title, meta, hero pills, body copy) and anything quoting it, and it breaks whenever a distillery is added. It shipped wrong twice in one week: `map.html` said 12 Bardstown and 8 Western when the pin data said 11 and 9, and a regional page hero claimed "seven of them sit on one street" while its own cluster card correctly said five (the seven had silently counted unpinned tasting rooms). All region totals have been removed from `map.html`'s `.region-card-stats` and from the four regional pages.
- **Never hardcode counts in trip-builder onboarding or empty-state copy.** Current badge: "Explore Kentucky distilleries · free to use". Current empty-state subhead: "across Kentucky's best distilleries".
- **If you want a number, derive it.** The one count a visitor sees is the live "Showing N distilleries" in the map sidebar, computed by `applyFilter()` at runtime, which cannot drift.
- **Counts describing pacing or a pair are fine** and should not be scrubbed: "three distilleries is the honest ceiling", "2 to 3 per day", "the two furthest apart are twenty minutes apart". The test is whether adding a distillery makes the sentence false.

### Content rules
- **The KDA Passport program ended July 2025.** Never reference the Kentucky Bourbon Trail Passport, stamp program or KDA companion app. If a page mentions it, remove it.
- **"Urban Bourbon Trail" is a program we do not cover** (decided August 2026). It is a Louisville Tourism program covering **bars and restaurants, not distilleries**, and its passport component has changed. Do not describe the program, reference a passport or t-shirt reward, or claim any property is an official stop. `hotels near urban bourbon trail in louisville` is the biggest query hitting `where-to-stay-bourbon-trail.html`, but the searcher's real question is "which hotel lets me walk to distilleries", which the Louisville walkability section answers. Use "urban bourbon" or "Louisville's urban bourbon scene" descriptively at most once or twice per page. Same reasoning as the KDA note: we do not describe programs we have not verified and do not cover.
- **Booking tier definitions** (restated August 2026 to match how the cards are actually tagged): **Easy** = walk-ups often work, a week or two is plenty. **Moderate** = you want a reservation, usually 2-4 weeks ahead. **Hard** = book 4+ weeks ahead, and the toughest calendars only open ~8 weeks out. The tier is **not** a pure function of lead time; it also encodes walk-up availability and how many slots exist per day, which is why a few Moderate cards carry a 1-week book-ahead. Do not "fix" those by re-tiering. The canonical lead time is the **Book Ahead snapshot value on the profile**; the booking guide's master table and trip-builder's `bookWeeks` must agree with it.
- **Region taxonomy.** Public-facing copy uses six regions: Louisville, Bardstown, Frankfort, Lexington/Lawrenceburg, Northern Kentucky, Western Kentucky. But **`map.html` filter buttons are Louisville / Bardstown / Frankfort / Lexington / Other**, with Northern and Western both normalising to Other. `trip-builder.html` has finer-grained buttons. **Never write copy telling users to "tap Western" or "tap Northern" on the map** — those buttons do not exist. Point to the trip builder for those regions.

---

## Data integrity: things that exist in more than one place

Most bugs on this site are one copy of a fact drifting from another. The pattern to prefer is **derive it**; where that is not possible, know the full list of copies.

| Fact | Copies | Canonical | Check |
|---|---|---|---|
| Distillery rating | profile snapshot, `distilleries.html` card, `trip-builder.html` `D` array | profile | `scripts/check_ratings.py` |
| Booking lead time | profile Book Ahead snapshot, booking guide table, `trip-builder.html` `bookWeeks` | profile | manual |
| Guide date | JSON-LD `dateModified`, visible `.article-meta` line, `guides.html` card | none, all three must match | `scripts/check_site.py` |
| Distillery presence | profile, `distilleries.html`, `trip-builder.html`, `map.html`, regional map page, `sitemap.xml` | n/a | `scripts/check_site.py` |
| PDF map data | derived at build time from `trip-builder.html` + `distilleries.html` | those two files | regenerate |

### Adding a new distillery
1. Verify coordinates on Google Maps (right-click → copy coordinates).
2. **Check pin overlap at zoom 14 — pins must be 28px+ apart.** If it cannot clear that, it is directory-only (see below).
3. Add to the `D` array in `trip-builder.html`, plus a smart pairing tip if another distillery is within a 5-minute drive.
4. Add to `distilleries.html`.
5. Add to `map.html`'s `DISTILLERIES` array.
6. Add a row to the matching **regional map page** (`bourbon-trail-map-{louisville|bardstown|frankfort|lexington}.html`) in its `.dl` list, in the order `map.html` draws the pins. Skip only for Northern or Western, which have no regional page. Add no counts while you are in there.
7. Add `TouristAttraction` JSON-LD to the profile (`address`, `geo`, `telephone`, `openingHours`, `url`, `sameAs`; no `review` block).
8. Regenerate the sitemap, then the PDF map: `python scripts\generate_pdf_map.py`. The generator reads `trip-builder.html` and `distilleries.html`, so it flows in automatically; pins renumber and the checklist reflows. Commit the regenerated PDF. If the distillery is in a brand-new city that maps to `Other`, the script prints a one-line warning telling you to add a `_CITY_REGION` entry.
9. Run `python scripts/check_site.py`.

### Urban tasting rooms are DIRECTORY-ONLY
A new urban tasting room gets a **profile page plus a card in `distilleries.html`, and nothing else.** No `trip-builder.html`, no `map.html`, and therefore never the PDF (the generator iterates the trip-builder `D` array, so a card with no `D` entry is silently skipped).

**Why:** the map and trip builder plan a *driving* route. These rooms are walk-up sub-stops of a block that is already pinned, and they physically cannot be pinned. Measured at zoom 14, Green River (714 W Main), Pursuit (722) and Bardstown Bourbon Co. (730) fall **3.5–7px apart** against a 28px minimum. They would render as one unreadable blob, and OverlappingMarkerSpiderfier was deliberately removed and must not come back. The 700 block is already represented by Buzzard's Roost (624) and Michter's Fort Nelson (801).

- **This is not a blanket "tasting rooms are excluded" rule.** Stitzel-Weller, Dark Arts, Fresh Bourbon, Chicken Cock and Whiskey Thief (Louisville) **are** in the trip builder and map and should stay: they are spaced fine and are drive-to destinations. Do not "consistency-fix" them by removing pins.
- A future tasting room that is a genuine drive-to destination and clears 28px from every existing pin can have a pin. **The test is spacing and routability, not `data-production`.**
- Known pre-existing violation: Evan Williams and Buzzard's Roost sit 22.3px apart. Left alone; do not make it worse.

---

## Embeddable map widget

`map.html?embed=1` strips the nav, footer, SEO content block and PDF modal, and fills the viewport, so partners can iframe the map. `embed-bourbon-trail-map.html` is the landing page that generates the snippet and the no-website host toolkit. Implementation detail is in `NOTES-internals.md`.

- **Framing is allowed and requires no headers.** The site sends no `X-Frame-Options` and no CSP. If you ever add a `_headers` file, do not set a site-wide `frame-ancestors` without carving out the embed.
- **The attribution `<a>` must live in the parent page, outside the iframe.** A link inside an iframe passes no equity, so an in-frame credit would be decoration rather than the actual trade. This is the single detail that decides whether the widget produces referring domains.
- **The snippet ships `loading="lazy"`**, so the widget costs an unscrolled host page nothing.
- **`internal=1` is required when embedding our own map on our own pages** (the regional map pages). It suppresses GA inside the frame, hides the attribution badge, and makes link clicks navigate the whole tab. Without it, every regional page view fires `embed_load` with `embed_host` set to our own domain, corrupting the metric that exists to show which **partners** deployed the widget, and double-counts `map.html` pageviews.
- **The widget writes no cookies and no storage** on a partner's guests, because GA runs in Consent Mode with `analytics_storage: 'denied'` in embed mode. The embed page promises this in writing, so keep it true. Trade-off: embed views have no persistent client ID, so GA4 counts them as new users each time; do not read "users" on embed traffic as people.

### Printable QR cards and `_redirects`
`js/qr.js` is a **vendored** QR encoder (byte mode, versions 1-40, all four EC levels), not a third-party API: an external endpoint would leak the URL, add an uncontrolled dependency, and can rot silently on printed material that lives in a guest binder for years. `scripts/verify_qr.js` proves it against the `qrcode` Python package for every version, level and mask (2,672 matrices, 0 diffs). Run it if you touch the encoder. Bump the `?v=` on the `js/qr.js` script tag when you do, or browsers serve the cached copy.

**`_redirects` exists at the repo root and the `/m/*` rules are PERMANENT.** (There is still no `netlify.toml`.) `/m/:region/:host` are the short links encoded into the printable QR cards. **A host prints a card once and it sits in a guest binder for years, so those paths can never be removed or renamed.** To change where they go, change the right-hand side and every card already in the wild keeps working. They are deliberately **302, not 301** — a 301 gets cached indefinitely and removes the ability to re-point them. Statewide uses the explicit slug `/m/ky`, because a bare `/m/<property-name>` would read the property name as a region. UTMs live in the redirect target, not the QR payload, so the encoded URL stays short; that dropped the QR from version 9 to 4-7, meaning chunkier modules at print size and a code that scans from across a room.

---

## Regional map pages

`bourbon-trail-map-{louisville,bardstown,frankfort,lexington}.html`. Each embeds the live map through `map.html?embed=1&internal=1&region={region}`, so **no distillery data is duplicated** — pins, popups and sidebar all come from `map.html`'s array.

- Adding a distillery means adding a row to its regional page (step 6 above). If you forget, the list is merely incomplete rather than wrong, which is deliberate and is why these pages carry no totals.
- **No Northern or Western page exists and none should be added** without a separate decision. Those regions normalise to `other` on the map and have no filter button, so a page would send readers hunting for controls that do not exist. The Lexington page states this and points to the trip builder.

---

## Affiliate links: DO NOT modify these URLs

Booking.com links use CJ Affiliate tracking, migrated from Awin/tidd.ly in June 2026. Format: `https://{cj-domain}/click-101752228-17293132?url={encoded-booking.com-url}` where `{cj-domain}` is one of `www.kqzyfj.com`, `www.anrdoezrs.net`, `www.tkqlhce.com`, `www.jdoqocy.com` — all valid, assigned per link at generation time.

**Ten Booking.com links are live**, all on `where-to-stay-bourbon-trail.html` (Old Talbott Tavern also appears on the itinerary): Hotel Distil, Omni Louisville, 21c Museum Louisville, Hampton Inn Louisville, Bardstown Motor Lodge, The Trail Hotel, Old Talbott Tavern, Capital Plaza, 21c Museum Lexington, Hilton Lexington Downtown.

**New Hope Bourbon Stop is the exception.** A CJ Booking.com link for it exists but is **not used on the site**, because Kyle's own property leads with direct booking (`bourbonstopky.com`, best rate) plus Airbnb and VRBO. Do not "restore" a Booking.com link there without asking — sending Kyle's own bookings through an affiliate network would cost him the direct margin.

**The exact URLs live in `where-to-stay-bourbon-trail.html`. Copy from there; never reconstruct one by hand.** They used to be listed here verbatim, which made this file a second copy of live data, the exact drift pattern documented above. Instead `check_site.py` now asserts the invariants on every affiliate link it finds: the publisher ID is `click-101752228-17293132`, the tracking domain is one of the four CJ domains, and the target is booking.com. Corruption fails a check rather than needing someone to compare against a doc.

VRBO: `https://vrbo.com/affiliate/VD0a4b2`. Kyle's Airbnb is a direct link, no affiliate network.

**Commission is earned on ANY Booking.com booking through the link, not just the linked property.**

---

## Email marketing (MailerLite)

Account 2164831, universal script on every page after the GA script. Signup forms on: homepage (modal), itinerary (modal), trip builder (inline), booking guide (inline), map (PDF modal). Three-email nurture sequence active. Lead magnet is the PDF checklist, delivered by welcome automation.

**Form IDs:** `CliYpr` = printable PDF map. `WD5yKI` = planning checklist lead magnet.

**GA4 event tracking on MailerLite forms.** Each page with an embedded form has a MutationObserver in its GA4 init block, watching for `.ml-form-successBody` changing from `display:none` to visible — the exact DOM transition MailerLite makes on confirmed subscription. It fires `email_signup` at most once per form per page load, with `method: 'pdf_map'` for `CliYpr` and `method: 'checklist'` for `WD5yKI`.

**If you add a page with a MailerLite form**, copy the observer one-liner from an existing form page. **The dataLayer.push interception approach was tried and is confirmed broken** — MailerLite does not push `form_submit` to the dataLayer for `ml-embedded` forms.

`trip_builder_complete` fires in `openEmailModal()` in trip-builder.html with `{'stops': N}`.

**Free Resources modal pattern:** homepage and itinerary have a "Free Trip Planning Resources" section with two gold-border cards side by side, stacking on mobile. Each opens its own modal containing the form; no inline widgets in the page flow. Functions `openPdfModal()`/`closePdfModal()` and `openChecklistModal()`/`closeChecklistModal()`, both at z-index 2000, closing on outside click or Escape. `map.html` has the PDF modal only.

---

## Known gotchas

- **Site emoji are HTML numeric entities, not raw characters.** They are written `&#128197;` / `&#9201;`, so grepping for the literal glyph (or a Unicode-range regex) returns **zero hits and looks like the site is emoji-free. It is not.** Find them with `grep -oE '&#x?[0-9A-Fa-f]+;' *.html` then decode codepoints above `0x2000`. This produced a confidently wrong "there are no emoji on this site" audit in July 2026.
- **Netlify post-processing breaks markup greps.** See deployment step 3. This is the single most repeated debugging trap on this site.
- **`git ls-files` beats a bare glob** for any sweep, because of `.claude/worktrees/`.
- **No OverlappingMarkerSpiderfier.** It was removed from the trip builder; do not re-add it.
- Notepad++ Find in Files was the old batch-edit tool. No longer needed; just describe the batch change.
