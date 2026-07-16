# CLAUDE.md — mybourbontrailplan.com

## What This Is
Kyle's Kentucky Bourbon Trail trip planning website. Static HTML/CSS/JS site deployed on Netlify via GitHub auto-deploy. Also serves as a content marketing funnel for Kyle's Airbnb property (New Hope Bourbon Stop) near Bardstown, KY.

## Deployment
- **Repo:** github.com/mybourbontrailplan/mybourbontrailplan
- **Hosting:** Netlify with GitHub auto-deploy on push to `main`
- **Workflow:** `git pull` → make changes → `git add .` → `git commit -m "message"` → `git push`
- **No build tools, no framework, no CMS** — every page is a standalone HTML file at root level, with an `images/` subfolder for distillery photos

## Deployment Workflow

### Step 1 — Regenerate sitemap (if any HTML pages were added, removed, or noindex-toggled)

```
python scripts\generate_sitemap.py
```

This scans root-level HTML files, applies the blocklist and noindex exclusions, and writes a fresh `sitemap.xml`. Run it before deploying so the updated sitemap ships in the same deploy. Skip if the deploy contains no HTML page additions or removals (e.g. CSS-only or content-only edits to existing pages).

If the sitemap changed, stage and commit it with the rest of the deploy files so it ships in the same push.

### Step 2 — Deploy (push to `main`)

**Deploying is just pushing.** Netlify auto-builds from GitHub on every push to `main`; there is no separate deploy command to run.

```
git add <the files you changed>
git commit -m "message"
git push origin main
```

The site goes live within roughly a minute. Confirm it actually landed before moving on, by fetching the changed page and grepping for something the edit introduced:

```
$r = Invoke-WebRequest -Uri "https://mybourbontrailplan.com/{page}.html?cachebust=$(Get-Random)" -UseBasicParsing
$r.Content -match '{a string your change added}'
```

**Verify against VISIBLE TEXT, not markup.** Netlify post-processes the HTML it serves, so the deployed source is not byte-identical to the repo. Confirmed July 2026:
- **`.html` extensions are stripped** (pretty URLs): `href="distillery-green-river-louisville.html"` is served as `href='/distillery-green-river-louisville'`.
- **`href="index.html"` becomes `href='/'`**.
- **Double quotes become single quotes** and **attributes get reordered**: `<a href="index.html" class="logo">` is served as `<a class='logo' href='/'>`.

So `grep 'href="foo.html"'` or `grep 'class="stop-link"'` against the live site returns **zero and looks like a failed deploy when the deploy was fine**. This burned a whole debugging cycle. Grep for prose the change introduced ("Bardstown tasting room"), a rendered label, or an extension-less fragment (`green-river-louisville`) instead.

Notes:
- **Do NOT run `netlify deploy --prod --dir=.`.** The Netlify CLI is not installed on this machine (`netlify` is not on PATH), and it isn't needed. This step used to be documented here and always failed; the push had already deployed the site. The stale `.netlify/` folder is leftover state from a one-time CLI use, not an active config. There is no `netlify.toml`.
- Stage files explicitly rather than `git add .` — the working tree usually carries local-only noise (`.claude/settings.local.json`, `.claude/worktrees/`) that should not be committed.
- Wait for the live check to pass **before** running IndexNow. Pinging IndexNow tells crawlers to fetch the URL now; if the deploy hasn't finished, they'll re-index the old content.

### Step 3 — Submit to IndexNow

**IMPORTANT: After every successful deploy, immediately run the IndexNow submission script:**

```
python scripts\indexnow_submit_changed.py
```

This pings Bing (and other IndexNow-participating search engines) with the URLs of files changed in the most recent commit, triggering faster recrawl. The site relies heavily on Bing traffic, so this step is non-negotiable for deploys that include HTML changes.

### When to skip IndexNow

Skip the IndexNow ping only if:
- The deploy contains no HTML changes (CSS-only or JS-only changes that don't alter page content)
- The deploy is a rollback or no-op
- The script has already been run for this commit

### When to run the bulk submission instead

If a deploy includes 20+ changed HTML files (e.g., a site-wide template update or large refactor), use the bulk submission script instead to avoid hitting per-URL rate limits:

```
python scripts\indexnow_bulk_submit.py
```

### IndexNow response handling

HTTP 200 and HTTP 202 are both success responses. The scripts treat both as valid. If you see any other response code, surface the error to the user before continuing.

### Verification

After running the IndexNow script, paste the output back to the user so they can confirm the submission succeeded. Don't silently swallow the output.

## Tech Stack
- Static HTML/CSS/JS
- Fonts: DM Sans (body) + Fraunces (display/headings)
- Maps: Leaflet.js with CartoDB Light tiles; SortableJS 1.15.6 (trip-builder drag-to-reorder, loaded from unpkg after Leaflet)
- Analytics: Google Analytics (G-DVK4D6KJJP) on all pages; custom events: `email_signup` (MailerLite form success), `trip_builder_complete` (itinerary export), `share_link_copied` (Copy Trip Link button, includes stop count), `plan_loaded_from_link` (shared `?plan=` URL opened, includes stop count)
- Email marketing: MailerLite (account ID 2164831, universal script on every page after GA script)
- Affiliate links: CJ Affiliate/Booking.com (kqzyfj.com/anrdoezrs.net/tkqlhce.com/jdoqocy.com tracking domains), CJ Affiliate/VRBO, direct Airbnb
- Email obfuscation: Contact and About pages use JS-rendered email to prevent mangling
- Search Console verified via meta tag on all pages

## Design System
- Colors: Primary blue `#1B4F72`, accent gold `#D4A03C`, dark `#0E2F44`
- CSS variables: `--primary`, `--primary-light`, `--primary-dark`, `--accent`, `--accent-light`, `--font-display`, `--font-body`, `--text`, `--text-secondary`, `--text-light`, `--border`, `--bg-subtle`
- Style: Modern, clean, SaaS-inspired. White backgrounds, subtle shadows, rounded corners (12px)
- Icons: see the Brand Icon System section below.

## Brand Icon System

Shared two-tone SVGs (dark `#0E2F44` + gold `#D4A03C`, 64x64 viewBox) live in **`images/icons/`**. Reference them with `<img src="images/icons/icon-{name}.svg" alt="" width="N" height="N" loading="lazy">` — `alt=""` because they are always decorative next to a text label.

- **The folder is lowercase `icons`, not `Icons`.** Windows will happily serve either; Netlify is case-sensitive and will 404 the wrong casing in production. It shipped as `Icons/` once and was renamed.
- **Current icons (17):** `route`, `barrel`, `calendar`, `car`, `cost`, `eat-stay`, `lightbulb`, `city`, `hotel`, `house`, `star`, `badge`, `building`, `clock`, `park`, `pin`, `trophy`.
- **Meaning is fixed, do not merge these two:** `badge` (shield+check) = official-trail / trail designation. `trophy` = awards and honors. A distillery being *on the trail* is `badge`; a distillery *winning an award* is `trophy`. Never swap them.
- **Still no icon for:** `shuttle` (transportation uses `car`), `horse`, and the various one-off distillery flavor glyphs (corn, fire, ship, flags, crossed swords, music, family...). No warning/check-mark icon either.

### Chip style (the standard container)
Icons sit centered in a "chip": background `#F6F0E4`, border-radius ~20% of chip size, icon ~60% of chip width.
- Homepage `.feature-icon`: 56px chip, 11px radius, 34px icon.
- Where-to-stay `.lodging-icon`: 64px chip, 13px radius, 38px icon.

Keep those proportions when adding a chip elsewhere. Do not reintroduce per-card background tints (the old `.feature-icon.gold` alternating variant was removed) — every chip is `#F6F0E4`.

**Small inline chip (entity listing cards):** where-to-stay `.type-chip` is a 28px chip / 8px radius / 17px icon, sitting inline to the **left of the eyebrow label** inside `.lodging-type` (a flex row, gap 8px). These cards have **no hero panel** — the card body starts at the eyebrow row. The navy gradient panel treatment is reserved for guide cards only; entity listing cards (lodging, and restaurant cards on eat-and-drink) never get a hero panel.

**Inline badge/pill icons:** inside a pill (`.badge`, `.lodging-tag`, `.rc-tag`, `.tour-card-rec`) the icon is a bare 16px `<img>` with `style="vertical-align:-3px;margin-right:4px"` — no chip, no wrapper, no per-page CSS. Mapping: award/honor pill → `trophy`; top-pick pill → `star`; official-trail/craft/independent pill → `badge`.

### Region banner (where-to-stay `.region-header`)
Navy panel (`--primary-dark`). **No icon chip** — the text block sits at the left padding. Under each city-name `<h3>` sits a gold **inline-SVG "trail underline"**: a gentle dashed arc (`stroke-dasharray="9 8"`) with a filled dot at each end. It is `.trail-underline { display:block; margin-top:2px; max-width:100%; height:auto; }` so it scales down proportionally when the container narrows on mobile. The descriptor `<p>` follows (`margin-top:12px`). eat-and-drink's `.region-header` is a *different* component (a bordered underline header with a colored `.region-dot`) and was left alone — it is not the navy banner.

- **The SVG's `width`/`viewBox`/path/circle coordinates are per-banner and hard-coded** to that heading's rendered text width. `W` = the heading's rendered **glyph** width **plus 4**; the path is `M5,10 Q {W/2},3 {W-5},8` and the right dot is at `cx={W-5}` (SVG attributes can't do math, so the numbers are pre-computed). Current values: Louisville `W=110`, Bardstown &amp; New Hope `W=266`, Frankfort `W=112`, Lexington `W=114`.
- **Measure the glyph run, not the `<h3>` box.** The element box is wider than the letters and makes the arc overrun. Select the h3's text node and read a `Range.getBoundingClientRect().width` at desktop (22px Fraunces 700), e.g. `const r=document.createRange(); r.selectNodeContents(h3.firstChild); r.getBoundingClientRect().width`. Then `W = round(width) + 4`. The `+4` puts the end dot (`cx=W-5`) just under the last letter's right edge, mirroring the left dot (`cx=5`) under the first letter.
- **If a region banner heading's text changes, re-measure that heading and regenerate its trail-underline SVG values** (`width`, `viewBox`, the `Q {W/2},3 {W-5},8` control/end points, and the end-dot `cx`). A stale width makes the arc under- or over-run the text. The other three banners are unaffected — only re-measure the one whose text changed.

### Homepage guide card headers (`.guide-img`)
Background is `linear-gradient(135deg, #0E2F44, #1B4761)` for **all** cards (the old per-card blue/gold/teal inline gradients are gone). Each header contains, in order:
1. `.guide-img-eyebrow` — the category, gold `var(--accent)`, uppercase, `letter-spacing:1.2px`. This replaced the old body-level `.guide-category` div; the category lives in the header now, not the body.
2. `.guide-img-ghost` — a large category icon, right-aligned, `opacity:0.3`, **inlined SVG with all strokes recolored to `#D4A03C`** (the file versions are dark-on-light and vanish against the navy, so they can't be used via `<img>` here).
3. `.guide-img-trail` — a gold dashed trail curve across the bottom, `stroke-dasharray`, `opacity:0.7`, `vector-effect="non-scaling-stroke"` so the stretch to card width doesn't distort the stroke.

The old `.guide-img-label` (the ghosted "3D"/"BT"/"$$" two-character mark) is gone. Do not re-add it.

## File Structure

### Core Pages (9)
- `index.html` — Homepage
- `3-day-bourbon-trail-itinerary.html` — Flagship SEO page with 2/3/4-day trip selector
- `distilleries.html` — Directory with 59 filterable cards (region, type, booking) + sort by rating/A-Z; count is dynamically set on load via `applyFilters()`
- `map.html` — Static interactive map with 59+ distilleries; height is `calc(100vh - 120px)` so content below is visible on scroll. PDF map CTA card opens a modal (no `#pdf-signup` inline section — that was removed). Features: distillery search box in sidebar (dropdown autocomplete, fly-to on click), collapsible region legend on mobile (collapsed by default), Kentucky state border rendered via `L.geoJSON()` fetched from PublicaMundi US states GeoJSON (fails silently if unavailable), pin labels visible at zoom 9+. **URL deep-link support** via `applyDeepLink()` at end of script — supports `?region=` (fits bounds to region, activates filter button) and `?distillery=` (flies to marker at zoom 14, opens popup); both params together apply region filter then highlight distillery (falls back to distillery-only if distillery isn't in that region). Region param values: `louisville`, `bardstown`, `frankfort`, `lexington`, `other`; `northern`/`central`/`western` all normalize to `other`. Distillery slug matches the `distillery-{slug}.html` filename pattern. Note: map.html uses `marker.addTo(map)` / `map.removeLayer()` for filter toggling. trip-builder.html also uses `marker.addTo(map)` / `marker.removeFrom(map)` via `_addPin()`/`_removePin()` (not setOpacity).
- `trip-builder.html` — Interactive trip builder (see Trip Builder section below)
- `bourbon-trail-booking-guide.html` — 10-step booking checklist
- `bourbon-trail-budget-guide.html` — Per-person cost breakdown
- `where-to-stay-bourbon-trail.html` — Lodging guide with affiliate links
- `guides.html` — Blog/guides index page

### Content Pages
- `eat-and-drink-bourbon-trail.html` — Restaurant/bar guide by region
- `about.html` — Monetization disclosure, JS email rendering
- `contact.html` — JS email rendering

### Blog Posts / Guides
- `best-time-to-visit-bourbon-trail.html` — Month-by-month seasonal guide
- `bourbon-trail-non-bourbon-drinkers.html` — Guide for non-bourbon-drinking partners
- `louisville-whiskey-row-walking-guide.html` — Louisville Whiskey Row self-guided walking tour
- `bourbon-trail-transportation-guide.html` — How to get around: DIY driving, guided tours, designated driver strategies
- `kentucky-bourbonfest.html` — Kentucky BourbonFest guide: dates, tickets, 60+ distilleries, 200+ bourbons, what to expect
- `kentucky-whiskey-trail.html` — Whiskey Trail vs Bourbon Trail explainer; same destinations, why both names exist, Jun 2026
- `bourbon-trail-bachelor-party-guide.html` — Bachelor party planning: best distilleries for groups, 2-day itinerary, budget, May 2026
- `buffalo-trace-gift-shop-guide.html` — Honest guide to what's in stock, allocated rotation, purchase limits, timing tips, Apr 2026

### Distillery Profiles (60 active)
All named `distillery-{name}.html`. All use the standardized template (white frosted nav, snapshot cards, tour card headers, rating bars, verdict box, sidebar with quick details). Each has: rating, tour options/prices, booking difficulty, gift shop tips, verdict, nearby pairings with links, GA tracking, mobile menu, MailerLite universal script, OG tags, correct canonical URL.
- 62 distillery HTML files exist in repo, but `distillery-garrard-county.html` (shut down) and `distillery-barton-1792.html` (not open to public) are intentionally excluded. Do NOT add either to `distilleries.html`, `trip-builder.html`, `map.html`, or `sitemap.xml`.

### Other
- `sitemap.xml` — URL count changes as pages are added; regenerate with `python scripts\generate_sitemap.py` when adding/removing pages. All URLs use `mybourbontrailplan.com` domain.
- `bourbon-trail-planning-checklist.pdf` — Lead magnet delivered via MailerLite
- `bourbon-trail-map.pdf` — Printable/downloadable bourbon trail map; linked from homepage and map.html. Generated from data by `scripts/generate_pdf_map.py`, which lays out both pages from scratch on every run. The source of truth is the live site itself: the script reads the `const D=[...]` array in `trip-builder.html` (name, lat, lng, region, type, cost, booking) and the cards in `distilleries.html` (city, Official Trail vs Craft tag), joins them on the profile filename, and assigns map numbers. Page 1 is a landscape hero map (statewide outline, region-colored numbered pins, a zoomed Central Corridor inset, region legend, QR to the Trip Builder). Page 2 is a landscape four-column reference list grouped by region (number, city, Trail/Craft, booking difficulty, tour cost) plus a drive-times table, a booking-ease index, and a second QR. There is no separate data file to maintain; `scripts/pdf_map_data.json` is written by the script as a readable snapshot of what it derived, for inspection only (not an input). Assets live in `scripts/assets/` (Kentucky outline GeoJSON, DM Sans + Fraunces TTFs). The old `scripts/pdf_map_add_distillery.py` in-place editor is obsolete and should not be used.
- `images/` — Distillery photos, named `{distillery}-1.jpg`, `{distillery}-2.jpg`, etc. All photos are EXIF-rotation-fixed and optimized for web (max 1200px, ~80% JPEG quality)

### Quick reference: editing the PDF map later
- **Add or edit a distillery:** make the normal site edits (`trip-builder.html`, `distilleries.html`, etc.), then run `python scripts/generate_pdf_map.py`.
- **Change a drive time, the booking-ease descriptions, or the QR target:** edit the `drives` list, the `gloss` list, or `TRIP_BUILDER_URL` near the top of `build_page2` / the script header.
- **Change brand colors, region colors, or fonts:** the palette and `REGION_COLORS` dict are at the top of the script; fonts are in `scripts/assets/fonts/`.
- **Header logo:** both PDF pages embed the raster brand lockup `images/nav-2x.png` via the `logo()` function (`LOGO_PNG` / `_LOGO_AR` constants). If the brand lockup art changes, re-export `nav-2x.png` (keep it a wide transparent PNG) and re-run the generator — no code change needed unless the aspect ratio changes.
- **Move a town to a different region:** two dicts near the top of the script control this, and both feed the map pin color and the page-2 list section. Use `_CITY_REGION` for legacy `Central`/`Other` towns (e.g. Shelbyville's Bulleit + Jeptha Creed are mapped to Louisville, the I-64 corridor, rather than Lexington/Lawrenceburg). Use `_REGION_OVERRIDE` when the site already tags a real region but it is geographically misleading for planning (e.g. Paris is tagged Northern KY on the site but sits ~17 mi from the Lexington distilleries, so it is overridden to Lexington/Lawrenceburg). Geographic outliers that sit apart from their region's other pins (Shelbyville, Danville, Paris) get a small town label in the inset so they read clearly; that list is in `build_page1`.
- **Page orientation:** both pages are currently US Letter landscape. Page sizes are set at the top of `build_page1` and `build_page2` (`W,H = 792,612`) if you ever want page 2 back in portrait.

## Nav & Footer Template (ALL pages)
- **Top nav links (in order):** Plan Your Trip → Distilleries → Map → Where to Stay → Eat & Drink → Trip Builder → Guides → Booking Guide (CTA style)
- Map must be a nav item on every new page created

### Header logo (ALL pages)
- **Brand assets** live in `images/`: `bourbon-trail-planner-nav.svg` (wide lockup, ~1020×136, renders ~300px at height 40px), `bourbon-trail-planner-icon.svg` (pin-only mark, square `viewBox="74 88 364 364"`, renders 40×40 at height 40px), plus `-nav-reversed.svg` / `-lockup*.svg` variants. The homepage footer uses `-nav-reversed.svg` at height 36px — leave it alone when batch-editing the header.
- **Hamburger breakpoint is `900px` site-wide (HB=900).** Every page collapses the nav to the hamburger at `max-width:900px`. When adding a page, match this: the nav must show the hamburger (and hide `.nav-links`) at ≤900px. (Historically most pages used 640px; they were unified to 900px so the icon-only tier never has to share the header with the full link row below ~940px, where the 8 links wrapped.) On most pages the collapse rules live in the same `@media (max-width:900px)` block as the mobile logo rule below; some pages also retain an older `@media (max-width:640px)` block with redundant (harmless, subset) `.nav-links{display:none}` / `.mobile-menu-btn{display:block}` lines plus that page's content rules — leave those content rules at their breakpoint.
- **Responsive logo swap (three tiers):** the header logo is wrapped in a `<picture>` with two `<source>`s (first match wins). Exact structure:
  ```html
  <a href="index.html" class="logo"><picture><source media="(max-width:900px)" srcset="images/bourbon-trail-planner-nav.svg?v=4"><source media="(max-width:1199px)" srcset="images/bourbon-trail-planner-icon.svg?v=4"><img src="images/bourbon-trail-planner-nav.svg" alt="Bourbon Trail Planner" class="logo-lockup" style="height:40px;width:auto;display:block"></picture></a>
  ```
  Plus a mobile rule appended to the `<style>` block that also drives the collapse: `@media (max-width:900px){.nav-links{display:none;}.mobile-menu-btn{display:block;}.logo-lockup{width:min(72vw,300px)!important;height:auto!important;}}` (the `!important` is required to beat the inline `height:40px`). Tiers:
  - **≥1200px** → full lockup at height 40px (the `<img>` default; no `<source>` matches).
  - **901 … 1199px** → 40px pin icon with the full link row. The lockup would blow past the `max-width:1200px` `.nav-inner` cap here; the icon frees ~260px so the nav stays on one line (verified one-line at 1024). (A ~40px sliver just above 900 can still wrap the 8 links; negligible and rarely hit.)
  - **≤900px (hamburger shown)** → full lockup again, sized `width:min(72vw,300px);height:auto` so the wordmark is legible and clears the hamburger on a 375px phone (~17px gap). Verified 375/414/768/850/1024/1280: hamburger opens/closes correctly, no logo/hamburger collision, wordmark visible at mobile widths.
- **`.nav-links` gap is `26px` (not 32px)** site-wide. This was tightened from 32px specifically so the wide lockup + all 8 links clear one line inside the 1200px cap with ~38px of slack at 1280/1440/1920. Do NOT bump it back to 32px — the lockup nav wraps to two lines above ~1200px if you do.
- **Favicon chain** (in every page `<head>`, SVG primary + PNG fallbacks, versioned with `?v=`):
  ```html
  <link rel="icon" type="image/svg+xml" href="/images/bourbon-trail-planner-icon.svg?v=4">
  <link rel="icon" type="image/png" sizes="32x32" href="images/favicon-32.png?v=4">
  <link rel="apple-touch-icon" sizes="180x180" href="images/apple-touch-icon-180.png?v=4">
  ```
  Bump the `?v=` query on all three (and the `<picture>` srcset) together when the icon art changes, to bust caches.

### Footer variants
Two footer patterns exist — use the one that matches the page type:

**Homepage footer** (`index.html` only): Multi-column grid with Plan / Explore / Resources sections, inline brand description, and a `.footer-bottom` bar. Uses custom CSS classes (`.footer-inner`, `.footer-col`, etc.).

**Interior page footer** (all other pages): Single-row flexbox with all nav links inline, Instagram handle line, and standard copyright. No custom footer CSS needed — uses inline styles:
```html
<footer>
  <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:8px 20px;margin-bottom:16px;font-size:13px;">
    <a href="index.html">Home</a>
    <a href="3-day-bourbon-trail-itinerary.html">Plan Your Trip</a>
    <a href="distilleries.html">Distilleries</a>
    <a href="map.html">Map</a>
    <a href="trip-builder.html">Trip Builder</a>
    <a href="guides.html">Guides</a>
    <a href="where-to-stay-bourbon-trail.html">Where to Stay</a>
    <a href="bourbon-trail-booking-guide.html">Booking Guide</a>
    <a href="about.html">About</a>
    <a href="contact.html">Contact</a>
  </div>
  <div style="margin-bottom:12px;font-size:13px;"><a href="https://www.instagram.com/mybourbontrailplan" target="_blank" rel="noopener">@mybourbontrailplan on Instagram</a></div>
  <p>&copy; 2026 <a href="index.html">Bourbon Trail Planner</a>. Not affiliated with the Kentucky Distillers' Association.</p>
</footer>
```
The footer element itself needs the background/color styles from the page's CSS (`.footer` or `footer` selector). Copy from any interior page like `distilleries.html`.

## Distillery Profile Template Rules
When creating or editing distillery profiles:
- Use an existing profile like `distillery-buffalo-trace.html` as the canonical template reference
- All profiles MUST have: correct canonical URL (`https://mybourbontrailplan.com/filename.html`), OG tags (og:title, og:description, og:type, og:url), GA script, MailerLite universal script, `-webkit-text-size-adjust: 100%`, and `TouristAttraction` JSON-LD schema (see `scripts/add_schema.py` for the standard structure)
- **Do NOT add a `review` or `reviewRating` block to TouristAttraction schemas** — self-authored ratings violate Google's review snippet policy and cause Rich Results Test critical errors
- **`@type` must be an array: `["TouristAttraction", "LocalBusiness"]`** — `openingHours` is a `LocalBusiness` property; using a single string type `"TouristAttraction"` causes a schema.org validator warning
- Photo gallery section goes between "What to Expect" and "Tour Options", using the `.photo-gallery` / `.gallery-grid` classes
- Photos are referenced as `images/{distillery}-1.jpg` etc. — always use `loading="lazy"` on gallery images
- Gallery uses `aspect-ratio: 4/3` with `object-fit: cover` (NOT fixed height) to avoid cropping important content
- Use `repeat(3, 1fr)` grid for 3 photos, `repeat(2, 1fr)` for 4 photos
- Lightbox: each gallery page includes a `.gallery-lightbox` div and click-to-expand JS before `</body>` — tap any photo to see it full-screen
- Distilleries with photos so far: Willett (3), Heaven Hill (3), Chicken Cock (4), Lux Row (4), Larrikin (3), Preservation (3), Four Roses (4), Peerless (3), Wild Turkey (4), Maker's Mark (4), Old Forester (4), Buffalo Trace (4), Stitzel-Weller (4), Buzzard's Roost (3), Evan Williams (2), Log Still (3), Michter's (2)
- Buffalo Trace gift shop guide also has a 4-photo gallery (photos 6, 9, 10, 11 from the buffalo-trace-*.jpeg set)
- Nearby pairing cards must link to real profile pages (never `href="#"`)
- Restaurant cards link to `eat-and-drink-bourbon-trail.html`
- Sidebar region guides link to `guides.html`
- After creating a new profile: add it to `distilleries.html`, `trip-builder.html`, `map.html`, and `sitemap.xml`

### Rating Categories — always six bars, two label sets (DO NOT otherwise deviate)
Every profile's "Our Honest Ratings" block uses **exactly six bars, in this order**. Bars 2, 4, 5, 6 are identical everywhere; **only bars 1 and 3 change** depending on the venue class:

| # | Working distillery | Urban tasting room |
|---|---|---|
| 1 | Tour Quality | **Experience Quality** |
| 2 | Value for Money | Value for Money |
| 3 | Campus &amp; Grounds | **Space &amp; Atmosphere** |
| 4 | Gift Shop | Gift Shop |
| 5 | Booking Ease | Booking Ease |
| 6 | Crowd Level | Crowd Level |

- **Which set to use is an editorial judgment, NOT `data-production`.** Use the tasting-room labels only for an **urban room with no grounds and no tour** (a bar, lounge, or tasting counter). `data-production="tasting"` is *not* the trigger: `distillery-stitzel-weller.html` is tagged `tasting` but is a historic campus with real grounds and real tours, so it correctly keeps the **distillery** labels. Currently on the tasting-room labels: Dark Arts, Whiskey Thief (Louisville), Fresh Bourbon, Chicken Cock.
- **Why two sets (July 2026).** The old rule forced all six distillery labels onto every venue and told you to silently reinterpret them ("score Campus &amp; Grounds on the interior space"). That produced Dark Arts scoring **9.0 for "Campus &amp; Grounds"** at a blending house with no campus: the number was right, the label was lying. Relabeling bars 1 and 3 makes the label say what the score already meant. Four of six bars stay identical **on purpose** so headline ratings stay comparable across all venues and readers don't have to learn two systems. Do not widen this into a fully separate tasting-room scale.
- **Relabeling does not mean re-rating.** When the two label sets were introduced, the four existing urban rooms had their labels changed and their **scores left untouched**, because the scores already encoded the reinterpreted meaning. If you move a venue between label sets, change the label and leave the number alone unless you have a real reason.
- **Ratings score the VISIT, never the whiskey.** Do not add a "Whiskey Quality" bar, and do not grade how the bourbon tastes in the body copy or the verdict either. We rate every venue on the visitor experience; singling one out for a taste knock is unfair to it and inconsistent with the rest. If the whiskey is genuinely the story (a signature pour, a flight worth ordering), mention it as a *recommendation* ("the old fashioned flight is the thing to order"), not as a score or a criticism. Buzzard's Roost and Dark Arts both had a "Whiskey Quality" bar; a reader emailed to point out the inconsistency and both were normalized in July 2026.
- **Never invent a rating.** Every card carries a numeric rating and every profile carries six bars plus a verdict; these are Kyle's editorial judgments from real visits and are the entire premise of the site. If Kyle has not visited a venue, do not ship a guessed score, do not average other venues, and do not infer one from press coverage. Leave it as an explicit TODO and ask him.
- **Known exception:** `distillery-pensive.html` uses "Food &amp; Dining" in place of "Gift Shop" because the award-winning on-site kitchen is the actual reason to go. This is a deliberate one-off, not a precedent.
- The headline rating in the snapshot card (`Our Rating`, e.g. `7.5 / 10`) is **editorial, not the average of the six bars**. Changing the bars does not require changing the headline. Changing the headline *does* require updating the matching rating on the card in `distilleries.html`.

### Sidebar Contact Section — Standard Structure
All 60 active profiles have a standardized Contact section. Order must be:
1. `<a href="map.html?distillery={slug}" class="sidebar-link">See on Map &rarr;</a>` — always first
2. Phone row (`<div class="sidebar-row">`) — in Contact only, NOT in Quick Details
3. Official Website link
- **No Google Maps link** — the "See on Map" deep-link replaces it; do not add `google.com/maps` links to the sidebar
- Phone goes in Contact section only (removed from Quick Details to eliminate duplication)

### Internal Linking Conventions
- Every distillery profile links to `map.html?distillery={slug}` via the "See on Map" sidebar link
- Guide pages link to `map.html?region={region}` in context: `where-to-stay`, `3-day-bourbon-trail-itinerary`, `eat-and-drink-bourbon-trail`, `louisville-whiskey-row-walking-guide`, `kentucky-bourbonfest`, `bourbon-trail-non-bourbon-drinkers`
- Use `style="color:var(--primary-light);font-weight:500;"` for inline region map links in guide page body copy

## Trip Builder — Critical Technical Notes

### Architecture
- 60 distilleries with Leaflet.js markers, region filters, smart pairing tips
- **Distillery dots** are managed via `_addPin(id)` / `_removePin(id)`, which call `marker.addTo(map)` and `marker.removeFrom(map)`. A `_onMap` boolean flag prevents duplicate adds/removes. Click handlers survive DOM recreation because they're attached to the Leaflet marker object, not the DOM element. Trip stop dots (added to the trip) are always kept on the map — `_addPin` is called for them regardless of zoom.
- **Region overlay markers** are always on the map. When zoomed in (`show=true`), they're hidden by setting `opacity:0` and `pointer-events:none` on **both** the Leaflet icon wrapper (`m._icon`) **and** the inner `.region-overlay` child element — setting it on the wrapper alone is not sufficient because CSS `pointer-events:auto` on the child overrides the parent's inline `none` in HTML. Regions where this matters: Louisville (Old Forester, Evan Williams, Buzzard's Roost), Bardstown (Chicken Cock), Frankfort (Buffalo Trace, Castle & Key), Lexington (Fresh Bourbon).

### Mobile Layout
- Breakpoint: 900px
- Browse and Your Trip buttons are in a **fixed top action bar below the nav** (not floating bottom buttons — bottom positioning was abandoned due to iPhone Safari toolbar conflicts)
- All mobile interactive elements use z-index 800+ to stay above Leaflet layers

### Mobile z-index Stack (DO NOT violate this order)
```
2000  — Email overlay modal
1100  — Nav dropdown menu
1001  — Hamburger button
1000  — Nav bar
 850  — Browse panel, sidebar/trip panel
 800  — Mobile action bar (top)
 700  — Leaflet popup pane (DO NOT go below this for interactive elements)
 600  — Leaflet marker pane
 400  — Leaflet overlay pane
 200  — Leaflet tile pane
```

### Map Label Behavior
- Distillery name labels are hidden by default (`display:none`) and shown via `#map.show-labels` class
- Label threshold is **filter-aware**: `Math.min(10, RD[aRF].zoom)` when a region is active, 12 when "All" — so Western at zoom 8 shows labels, Northern at zoom 10 shows labels, "All" requires zoom 12
- Desktop hover shows label on mouseover at any zoom (`@media (hover:hover)` so it doesn't fire on touch)
- `filterRegion()` calls `handleZoom()` at the end so labels update immediately when the filter changes

### handleZoom() vs updateZoomUI() — Important Split
Two functions handle zoom-level changes:
- **`updateZoomUI()`** — fires **immediately** on every `zoomend` and `moveend` event. Updates: back button visibility, region overlay opacity/pointer-events, map label class (`show-labels`). No debounce. This ensures UI elements never lag behind map movement.
- **`handleZoom()`** — debounced 200ms after each `zoomend`/`moveend`. Calls `updateZoomUI()` first, then runs the expensive `_addPin`/`_removePin` loop over all 60 distilleries. The debounce prevents thrashing during fast zooming.
- `filterRegion()` calls `handleZoom()` directly (not debounced) at the end so dots and labels update immediately when a region is selected.

### handleZoom() Thresholds (all filter-aware)
- **Dot threshold** (`showThr`): `Math.min(10, RD[aRF].zoom)` when filtered, `10` when "All" — dots appear at the region's flyTo zoom
- **Label threshold** (`labelZoom`): same formula as dot threshold — labels and dots appear together
- **Back button** ("← All Regions"): shows at `z >= showThr` — visible as soon as dots appear
- **Region overlay buttons** (e.g. "Western 8 distilleries"): hidden when `show=true`, visible when `show=false`

### RG City-to-Region Mapping (trip-builder.html)
- `Newport:'Northern'` — New Riff and Pensive are both in Newport; they appear under the Northern filter
- Most other Northern KY cities (Independence, Ludlow, Sparta, Maysville, Burlington, Augusta) also map to `Northern`
- `Paris:'Lexington'` — Paris is 17 mi from Lexington distilleries, a natural Lexington-day add-on (closer to Lexington than to the Northern KY cluster)
- `Danville:'Lexington'`, `Lawrenceburg:'Lexington'` — these towns sit in the Lexington/Lawrenceburg corridor and appear under the Lexington filter
- `Shelbyville:'Louisville'`, `Crestwood:'Louisville'` — I-64/I-71 corridor distilleries grouped with Louisville per the PDF map regions
- `Lebanon:'Bardstown'`, `Radcliff:'Bardstown'` — grouped with Bardstown per the PDF map regions

### Region Data (RD) — flyTo destinations
- `Louisville`, `Bardstown`, `Frankfort`: zoom 14
- `Lexington`: zoom 11
- `Northern`: zoom 10
- **`Western`: lat 37.13, lng -87.59, zoom 8** — spans 2+ degrees of longitude; zoom 10 is too close for mobile to see all 8 distilleries; center is midpoint of extremes (not geographic mean) for best viewport fit
- `Central` region was removed — all formerly-Central distilleries (Bulleit, Jeptha Creed, Kentucky Artisan, Larrikin) are now in Louisville or Lexington per PDF regions

### Western Button Mobile Repositioning
- On desktop the Western button marker sits at the `RD` flyTo center (–87.59), which is visible in the wide desktop viewport
- On mobile (< 900px), the initial overview viewport only spans ~2 degrees of longitude and the Western center is off-screen to the left
- **Mobile fix**: Western button marker is placed at `lat 37.3, lng -86.2` with `iconAnchor [0,28]` (left-aligned) so the button sits near the left edge of the initial mobile view and extends rightward into full view
- Clicking the button still `flyTo`s `RD.Western` (37.13, -87.59, zoom 8) — marker position and flyTo destination are separate
- Detection: `const isMobile = window.innerWidth < 900` at map init time

### Mobile Back Button ("← All Regions")
- `position:absolute; top:24px; left:54px` — `top:24px` clears the fixed action bar; `left:54px` clears the Leaflet zoom controls (~36px wide at left edge). Previous `left:12px` placed it directly behind the zoom control.
- `z-index:600` — stays below the action bar (800); the extra `top` clearance keeps it visually below, not z-fighting above

### Trip State Persistence (localStorage)
- Key: `btp-plan`; stores `{trip, tDays, aDay}` as JSON
- `saveState()` is called by every mutator (add stop, remove stop, drag reorder, clear, switch day, change day count)
- `loadState()` returns `true` if valid saved data was found and applied
- Both use a try/catch wrapper matching the existing `btp-seen` pattern — localStorage failure (private mode, quota) is always silent
- On restore, `fitBounds()` zooms the map to fit all trip markers: `{padding:[60,60], maxZoom:13, animate:false}`. For a single stop, `setView` at zoom 13. This is required because the back button only appears at the region zoom threshold — restoring a trip at the default overview zoom would otherwise hide it.
- `rebuildDayTabs()` handles 4-day restored plans: removes any tabs > 3 then recreates them up to `tDays`. Uses IIFE closures in `onclick` to correctly capture day number.

### Shareable Trip URL (`?plan=` parameter)
- Encoding: slugs comma-joined per day, days semicolon-separated. Example: `day1slug1,day1slug2;day2slug1;day3slug1,day3slug2`
- `getShareURL()` builds the full URL; `getPlanString()` produces just the encoded plan portion
- `importPlan(str)` decodes and populates `trip[]`; unknown slugs are silently skipped (forward-compatible)
- After import, `history.replaceState` strips the `?plan=` param so subsequent edits don't re-import the original on refresh
- Plan is immediately saved to localStorage after import so it persists if the user refreshes
- `rebuildDayTabs()` is called after import to support shared 4-day plans
- GA4 event `plan_loaded_from_link` fires on import (with stop count)

### Copy Trip Link Button
- Element: `.share-btn#shareBtn` in sidebar footer, between the email button and clear button
- Disabled alongside `#exportBtn` when no stops are added (`updateStats()` drives both)
- `copyShareLink()` tries `navigator.clipboard.writeText()` first, falls back to `fallbackCopy()` (textarea select/exec)
- On success, shows a non-blocking fixed toast (`#shareToast`, z-index 1900) with a 5s auto-dismiss and an inline link to open the email modal
- GA4 event `share_link_copied` fires on copy (with stop count)

### Drag-to-Reorder Stops
- SortableJS 1.15.6 is loaded from unpkg after the Leaflet script tag
- Drag handle: `.drag-handle` div at the start of each `.stop-card` (six-dot SVG icon)
- `Sortable.create(area, {...})` is called at the end of `renderStops()` after `innerHTML` is set. If a Sortable already exists on the element (`area._sortable`), it's destroyed first to prevent double-init
- `delay:150` + `delayOnTouchOnly:true` — prevents drag from firing during normal scroll on touch; desktop drag starts immediately
- `onEnd` handler reads the DOM order of `.stop-card[data-id]` elements, rebuilds `trip[aDay]` from that order, then calls `refreshIcons(); renderStops(); drawRoutes(); updateStats(); saveState()`
- Do NOT use `delayOnTouchOnly:false` or remove `delay` — this causes the drag handle to intercept vertical scroll on mobile

### Onboarding and Empty-State Copy
- **Never hardcode distillery counts or region counts** in the onboarding badge or empty-state subhead — these numbers change as distilleries are added and become stale immediately.
- Current onboarding badge: "Explore Kentucky distilleries · free to use" (no count)
- Current empty-state subhead: "across Kentucky's best distilleries" (no count)

### Why Bottom Buttons Were Abandoned
iPhone Safari's dynamic bottom toolbar height isn't accounted for by `env(safe-area-inset-bottom)`. Multiple attempts with increased bottom values, dvh units, and @supports fallbacks all failed across iPhone 16 Pro and 17 Pro simultaneously. Top action bar eliminates all bottom-edge issues permanently.

### Urban tasting rooms are DIRECTORY-ONLY (no trip builder, no map, no PDF)
New urban tasting rooms get a **profile page + a card in `distilleries.html` only**. Do **not** add them to `trip-builder.html` or `map.html`, and therefore they never reach `bourbon-trail-map.pdf` (the generator iterates the trip-builder `D` array and looks up `distilleries.html` by profile filename, so a card with no `D` entry is simply skipped — no code change, no warning).

- **Why:** the map and trip builder plan a *driving* route between destinations. These rooms are walk-up sub-stops of a block that is already pinned, and they physically cannot be pinned. Measured at zoom 14: Green River (714 W Main), Pursuit (722), and Bardstown Bourbon Co. (730) fall **3.5–7px apart**, against the 28px minimum in the section below. Big Bat (800) is ~12px from BBC. They would render as one unreadable blob, and OverlappingMarkerSpiderfier was deliberately removed and must not come back. The 700 block is already represented on the map by Buzzard's Roost (624) and Michter's Fort Nelson (801).
- **This is not a blanket "tasting rooms are excluded" rule.** The five older tasting venues (Stitzel-Weller, Dark Arts, Fresh Bourbon, Chicken Cock, Whiskey Thief Louisville) **are** in the trip builder and map and should stay there: they are spaced fine (Whiskey Thief Louisville sits 37px from Angel's Envy) and are drive-to destinations. Do not "consistency-fix" them by removing their pins.
- If a *future* tasting room is a genuine drive-to destination and clears 28px from every existing pin, it can have a pin. The test is spacing and routability, not `data-production`.
- Known pre-existing violation: Evan Williams and Buzzard's Roost already sit 22.3px apart. Left alone; don't make it worse.

### Adding a New Distillery to Trip Builder
1. Verify coordinates on Google Maps (right-click → copy coordinates)
2. Check for pin overlap with nearby distilleries at zoom 14 — pins must be 28px+ apart
3. Add to the distilleries array in trip-builder.html
4. Add smart pairing tip if there's a nearby distillery within 5 min drive
5. Update the region count in the relevant region overlay button HTML (e.g. "Western · 8 distilleries")
6. Also add to `distilleries.html` and `sitemap.xml`
7. Add `TouristAttraction` JSON-LD schema to the new profile's `<head>` — include `address`, `geo`, `telephone`, `openingHours`, `url`, `sameAs` (see `scripts/add_schema.py` for the exact structure). Do NOT include a `review` block.
8. Regenerate the printable map: `python scripts\generate_pdf_map.py`. No map-specific arguments are needed. Because the generator reads `trip-builder.html` and `distilleries.html`, the new distillery flows in automatically once steps above have added it to those two files (pins renumber, the checklist reflows, the region counts update). Commit the regenerated `bourbon-trail-map.pdf` with the rest of the deploy. Note: the trip-builder `region` value can be one of the legacy buckets (`Other`); the generator remaps those to the six display regions by city. If you ever add a distillery in a brand-new city that maps to `Other`, the script prints a one-line warning telling you to add a `_CITY_REGION` entry near the top of `generate_pdf_map.py`.

## SEO Notes
- All canonical URLs must point to `https://mybourbontrailplan.com/filename.html`
- All pages need OG tags (og:title, og:description, og:type, og:url)
- Title tags under 85 characters
- Meta descriptions under 170 characters
- Schema markup: fully comprehensive JSON-LD across all page types:
  - Distillery profiles: `["TouristAttraction", "LocalBusiness"]` (array type) with `address`, `geo`, `telephone`, `openingHours`, `isAccessibleForFree`, `url`, `sameAs` — **no `review` block** (violates Google policy, causes Rich Results errors); array type required so `openingHours` is valid per schema.org
  - Guide/article pages: `Article` with `url`, `mainEntityOfPage`, `author`, `publisher`, `datePublished`, `dateModified`
  - Directory pages (`distilleries.html`, `guides.html`, `map.html`): `CollectionPage` with `url`, `publisher`
  - Homepage: `WebSite` + `Organization` (two separate schema blocks)
  - Trip builder: `WebApplication`; About: `AboutPage`; Contact: `ContactPage`
- **author/publisher**: always `{"@type": "Organization", "name": "Bourbon Trail Planner"}` — never `Person`, never a different name string
- **datePublished/dateModified**: always ISO 8601 with Eastern offset, e.g. `2026-02-22T00:00:00-05:00` — never bare `YYYY-MM-DD`. The site stamps `-05:00` year-round for consistency, including summer dates that are technically EDT (`-04:00`). Match the existing convention; do not "fix" some to `-04:00` and leave a mixed pattern.
- `scripts/add_schema.py` — bulk schema utility; use as the reference template when writing TouristAttraction schema for a new distillery profile
- Sitemap at `sitemap.xml` — update when adding any new page

### Updating a guide's date — THREE surfaces, every time
Whenever you make a **content change** to a guide or article page, bump **all three** of these. They live in two different files and it is easy to change one and forget the others (this has already happened twice):

1. **The JSON-LD `dateModified`** in the page's `<head>` schema block (ISO 8601, `-05:00`).
2. **The visible "Updated {Month} {Year}" line** in the page's `.article-meta` bar under the H1 (next to the calendar SVG, alongside the "N min read" item).
3. **The `.guide-date` span on that guide's card in `guides.html`** — the guides index. This is the one everyone forgets because it lives in a different file entirely. Note the existing spans are inconsistent: most show a bare **publish** month (`Jun 2026`) that matches the page's `datePublished`, while a few are prefixed `Updated `. If a card says `Updated `, keep that prefix and bump the month. If it shows a bare publish date, leave it alone unless you're deliberately converting it.

- Leave `datePublished` alone. It records original publication and never changes.
- These surfaces **drift**, and they have: in July 2026 the itinerary page had a schema `dateModified` of April while its visible line still read February, and the Whiskey Row guide shipped a full rewrite while its `guides.html` card still advertised "Updated Apr 2026". Check all three.
- **`guides.html` card copy goes stale too.** The card's `<p>` summary duplicates claims from the page (counts, "6+ distilleries", route direction). When you materially change a guide, reread its card blurb, not just its date.
- Skip the bump for pure style/markup edits with no content change (CSS tweaks, nav/footer template updates, favicon versions). Bump it for anything a reader would notice: new facts, corrections, rewritten copy, added or removed sections.
- **Distillery profiles have neither surface** — `TouristAttraction` schema carries no `dateModified` and profiles have no `.article-meta` bar. Nothing to bump there. Do not add date fields to a profile just to have them.
- Every guide's `.article-meta` bar should carry both a read-time item and an Updated item. Read time is computed at roughly **200 words per minute** over the body copy.

## Affiliate Links — DO NOT modify these URLs
- Booking.com links use CJ Affiliate tracking URLs — migrated from Awin/tidd.ly in June 2026
- **CJ link format:** `https://{cj-domain}/click-101752228-17293132?url={encoded-booking.com-url}` where `{cj-domain}` is one of: `www.kqzyfj.com`, `www.anrdoezrs.net`, `www.tkqlhce.com`, `www.jdoqocy.com` (all are valid CJ tracking domains — the specific domain is assigned per link at generation time)
- Active Booking.com links:
  - New Hope Bourbon Stop: `https://www.kqzyfj.com/click-101752228-17293132?url=https%3A%2F%2Fwww.booking.com%2Fhotel%2Fus%2Fnew-hope-bourbon-stop-new-hope.html`
  - Hotel Distil (Louisville): `https://www.anrdoezrs.net/click-101752228-17293132?url=https%3A%2F%2Fwww.booking.com%2Fhotel%2Fus%2Fautograph-collection-distil.html`
  - Omni Louisville: `https://www.tkqlhce.com/click-101752228-17293132?url=https%3A%2F%2Fwww.booking.com%2Fhotel%2Fus%2Fomni-louisville.html`
  - 21c Museum Louisville: `https://www.jdoqocy.com/click-101752228-17293132?url=https%3A%2F%2Fwww.booking.com%2Fhotel%2Fus%2F21c-museum.html`
  - Hampton Inn Louisville: `https://www.jdoqocy.com/click-101752228-17293132?url=https%3A%2F%2Fwww.booking.com%2Fhotel%2Fus%2Fhampton-inn-louisville-downtown.html`
  - Bardstown Motor Lodge: `https://www.kqzyfj.com/click-101752228-17293132?url=https%3A%2F%2Fwww.booking.com%2Fhotel%2Fus%2Fbardstown-motor-lodge.html`
  - The Trail Hotel (Bardstown): `https://www.kqzyfj.com/click-101752228-17293132?url=https%3A%2F%2Fwww.booking.com%2Fhotel%2Fus%2Fthe-trail.html`
  - Old Talbott Tavern: `https://www.jdoqocy.com/click-101752228-17293132?url=https%3A%2F%2Fwww.booking.com%2Fhotel%2Fus%2Fthe-old-talbott-tavern.html`
  - Capital Plaza (Frankfort): `https://www.jdoqocy.com/click-101752228-17293132?url=https%3A%2F%2Fwww.booking.com%2Fhotel%2Fus%2Fcapital-plaza.html`
  - 21c Museum Lexington: `https://www.jdoqocy.com/click-101752228-17293132?url=https%3A%2F%2Fwww.booking.com%2Fhotel%2Fus%2F21c-museum-lexington.html`
  - Hilton Lexington Downtown: `https://www.anrdoezrs.net/click-101752228-17293132?url=https%3A%2F%2Fwww.booking.com%2Fhotel%2Fus%2Fhilton-lexington-downtown.html`
- VRBO link: `https://vrbo.com/affiliate/VD0a4b2`
- Kyle's Airbnb: direct link (no affiliate network)
- Commission is earned on ANY Booking.com booking through the affiliate link, not just the linked property

## Email Marketing (MailerLite)
- Account ID: 2164831
- Universal script is on every HTML page (placed after GA script)
- Signup forms on: homepage (modal), itinerary page (modal), trip builder (inline), booking guide (inline)
- 3-email nurture sequence active (Day 3: top distilleries, Day 6: where to stay featuring Kyle's property, Day 10: booking mistakes)
- Lead magnet: PDF checklist delivered via welcome automation

### MailerLite Form IDs
- `CliYpr` — Printable PDF map (delivered via email); triggers from PDF map modal on homepage, itinerary page, and map.html
- `WD5yKI` — Planning checklist lead magnet; triggers from checklist modal on homepage and itinerary page; also inline on trip builder and booking guide

### GA4 Event Tracking on MailerLite Forms
The 5 pages with embedded MailerLite forms (index.html, 3-day-bourbon-trail-itinerary.html, map.html, trip-builder.html, bourbon-trail-booking-guide.html) each have a MutationObserver in their GA4 init `<script>` block (trip-builder has it in its own `<script>` block immediately after the MailerLite script). The observer watches for `.ml-form-successBody` changing from `display:none` to visible — the exact DOM transition MailerLite makes on confirmed subscription. It fires `gtag('event', 'email_signup', {'method': ...})` at most once per form per page load.

- `CliYpr` → `method: 'pdf_map'`
- `WD5yKI` → `method: 'checklist'`

**If adding a new page with a MailerLite form**, copy the observer one-liner from any existing form page's GA4 init block and add it there. The dataLayer.push interception approach was tried first and confirmed broken — MailerLite does not push `form_submit` to the dataLayer for `ml-embedded` forms. Ensure the `gtag` call inside the observer is guarded with `if(typeof gtag==='function'){...}`.

`trip_builder_complete` fires in `openEmailModal()` in trip-builder.html with the stop count as `{'stops': N}`.

### Free Resources Modal Pattern
Homepage and itinerary page have a unified "Free Trip Planning Resources" section with two gold-border cards side by side (stacking on mobile). Each card opens its own modal containing the MailerLite form — no inline embedded widgets in the page flow. Modal functions: `openPdfModal()` / `closePdfModal()` and `openChecklistModal()` / `closeChecklistModal()`. Both modals share z-index 2000 and close on outside click or Escape. map.html has the PDF map modal only (no checklist modal).

## Google Drive Artifact Files
The repo contains files named with ` (1)` suffixes (e.g., `distillery-chicken-cock (1).html`, `guides (1).html`). These are Google Drive sync duplicates — identical to the originals, not separate pages. Also `.tmp.driveupload/` folder accumulates Google Drive temp files. Neither should be edited or referenced; they can be cleaned up by deleting them, but they're harmless if left in place.

## Copy Style

### Em Dashes
Do not use em dashes (`—` or `&mdash;`) anywhere in site content. The site was fully de-em-dashed in June 2026 (1,018 instances). Use context-appropriate punctuation instead:

| Context | Replacement |
|---|---|
| `<title>`, `og:title`, JSON-LD `headline` (Title — Subtitle) | `: ` |
| H1–H6 heading with no existing colon | `: ` |
| H1–H6 heading that already contains `: ` | `, ` |
| `<strong>Label</strong> — Description` (itinerary/day-stop lists, trip builder instructions) | `: ` |
| Body copy, card descriptions, meta descriptions | `, ` |
| Short connective phrases where comma reads awkwardly | ` - ` (regular hyphen with spaces) |

If a batch of em dashes ever needs removing (e.g. after importing copy from another source), run `python scripts/remove_em_dashes.py` from the project root.

### Other Punctuation
- Regular hyphens (` - `) are acceptable when a comma would create an awkward run-on in body copy
- No smart/curly quotes in HTML — use straight quotes or HTML entities

## Known Gotchas
- **Notepad++ Find in Files** was previously used for batch changes — with Claude Code, this is no longer needed. Just describe the batch change and Claude Code will handle it.
- **MailerLite universal script** must be on every new page (after GA script, before closing body tag)
- **GA script** must be on every new page (in head) — use exactly two separate `<script>` tags: (1) `<script async src="https://www.googletagmanager.com/gtag/js?id=G-DVK4D6KJJP"></script>` and (2) `<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','G-DVK4D6KJJP');</script>`. Never embed one `<script>` tag inside another — the HTML parser will misread it, the JS will throw a syntax error, and `gtag` will be undefined on the whole page.
- **All `gtag(...)` calls must be guarded** — always wrap as `if(typeof gtag==='function'){gtag(...)}` so a tracker failure can never abort a user-facing action (e.g. opening a modal or firing a mailto link)
- **iOS Safari text inflation** — all pages need `-webkit-text-size-adjust: 100%` in the html CSS rule
- **No OverlappingMarkerSpiderfier** — was removed from the trip builder, don't re-add it
- **Barton 1792** — not open to the public; profile file exists (`distillery-barton-1792.html`) but is intentionally excluded from the site. Do NOT add to `distilleries.html`, `trip-builder.html`, `map.html`, or `sitemap.xml`
- **Log Still is in New Haven, KY** (not New Hope) — Kyle's Airbnb is in New Hope, these are different places
- **Site emoji are HTML numeric entities, not raw characters.** They are written as `&#128197;` / `&#9201;`, so grepping for the literal glyph (or a Unicode-range regex) returns **zero hits and looks like the site is emoji-free. It is not.** To find them, grep for the entity form: `grep -oE '&#x?[0-9A-Fa-f]+;' *.html`, then decode codepoints above `0x2000`. This exact trap produced a confidently wrong "there are no emoji on this site" audit in July 2026. The old CLAUDE.md line claiming "No emojis" reinforced it — it described the homepage icon style, not the site.

## Emoji-to-Icon Migration (in progress)

Migrating emoji UI icons to the brand icon system.

**Done:** homepage feature cards (6) and guide card headers (3); where-to-stay lodging cards (hero slots removed, 28px inline `.type-chip` at the eyebrow); where-to-stay region banners (icon chip removed, trail-underline city name); where-to-stay's two lightbulb callouts (`icon-lightbulb`); the **site-wide badge-pill sweep** — official/craft/independent `badge-trail` pills → `icon-badge` (58), `badge-landmark` award pills → `icon-trophy` (4), `tour-card-rec rec-top` and `rc-tag tag-must` top-pick pills → `icon-star` (69), all inline 16px `<img>`; and the **distillery snapshot/tour-meta pass** across all 60 profiles (see below).

**Distillery snapshot + tour-meta (done, all 60 profiles).**
- `.snap-icon` (the 4 centered snapshot-card icons): calendar→`icon-calendar` (Book Ahead), stopwatch→`icon-clock` (Tour Length), trophy→`icon-trophy` (Our Rating; one profile used a glowing-star for the same slot, also → trophy), pin→`icon-pin` (Region). Rendered as a **bare 26px `<img>`** with `style="display:block;margin:0 auto"` (the card is `text-align:center`; no chip — matches the bare emoji it replaced).
- `.tour-meta-item` (the inline meta row): money→`icon-cost`, stopwatch→`icon-clock`, calendar→`icon-calendar`, as a **bare 16px `<img>`** (the row is `display:flex;align-items:center;gap:5px`, which handles spacing/alignment — no vertical-align hack needed).
- **Glyphs with no matching icon were stripped to text, not left as emoji** (a raw emoji next to line-art SVGs in the same row looks broken): group-size busts 👤/👥 ("Small groups", "Up to 10 people", etc., 10 instances) and dark-arts's one-off flavor glyphs (globe/bottle/pushpin/cocktail, 4 instances). The text label alone carries the meaning.
- Do **not** force-map onto near-miss icons (stopwatch→calendar, pin→route); duration and location must stay visually distinct.

**Deliberately left as emoji (survivors):**
- ~30 one-off `badge-trail` **flavor** glyphs, one per distillery (horse, corn, crossed swords, ship, fire, palette, bridge, family, AU/US flags...). No counterpart in a trip-planning icon set; mapping them would destroy the meaning.
- Callout/status glyphs with no mapped icon: warning `⚠` in `.warning-box` headers (9), check marks `✓` in booking checklists (16), and assorted inline content emoji in guide body copy (thermometer, fork-and-knife, bottle, etc.).
- Lightbulb `💡` callouts on pages **other than** where-to-stay (12, same `.tip-box-header` pattern) — trivially convertible to `icon-lightbulb` in a follow-up, just not in the named scope of this pass.

## Content Accuracy Notes
- **KDA Passport program ended July 2025** — do NOT reference the Kentucky Bourbon Trail Passport, stamp program, or KDA companion app anywhere on the site. The program is discontinued. If a page mentions it, remove the reference.
- Kyle has real bourbon trail experience — the site reflects honest, opinionated reviews
- Distilleries CAN pay for featured listings but CANNOT change ratings (disclosed on About page)
- Visitor stat: "Record 2.7 million annual visitors and growing" (use as evergreen)
- Budget guide uses per-person pricing
- Three Boys Farm Distillery is now Whiskey Thief Distilling Co.
- **Chicken Cock rating is 7.0** — bar is smaller than expected, accessible area limited to bar + two front gift shop rooms. Old fashioned flight is a highlight worth mentioning.
- **Green River has TWO venues, both Official Trail.** (1) **Owensboro**, 10 Distillery Rd, the working distillery (`distillery-green-river.html`). (2) **Louisville tasting room**, 714 W Main St on Whiskey Row, opened 2025 (`distillery-green-river-louisville.html`), phone (502) 804-5383, Tue-Sat 11-7, **closed Sunday and Monday**. Kyle verified against the KDA/KBT site in July 2026 that **both locations are listed on the official trail**, so both carry the Official Trail badge. Nothing is distilled in Louisville. Do not reuse Owensboro's phone ((270) 691-9001) or hours (We-Sa 9-5) on the Louisville page: they are different venues. Signature experience in Louisville is Fill-Your-Spirits, $15 per person plus the cost of a bottle, and which barrel is open varies.
- **Chicken Cock has TWO venues, and they get confused.** (1) **Circa 1856 Bardstown**, 103 E Stephen Foster Ave, Bardstown — the main venue and the one `distillery-chicken-cock.html` covers; opened 2024. (2) **"The Coupe"**, NuLu, Louisville — a speakeasy/cocktail destination, relaunched March 2026, a separate venue that is *not* the Bardstown one. The main venue is in **Bardstown, not Lawrenceburg** (Lawrenceburg is Wild Turkey); the Whiskey Row guide asserted "the Lawrenceburg tasting room" and was corrected July 2026. Nothing is distilled at either: Chicken Cock is "crafted in partnership with Bardstown Bourbon Company", which is why the Bardstown venue is `data-production="tasting"` despite the card calling it a micro-distillery.
- **Heaven's to Betsy Bakery** added to eat-and-drink page (On the Road section) and Wild Turkey nearby cards — Lawrenceburg, outstanding Reuben sandwich
- **Becker & Bird Distillery** (file: `distillery-baker-bird.html`) — the distillery's official KBT name is Becker & Bird; the winery on the same property is called Baker-Bird. File name stays as-is for URL continuity.
- **Augusta Distillery** (file: `distillery-augusta.html`) — separate from Becker & Bird, also in Augusta, KY at 207 Seminary Ave. Produces Buckner's bourbon (Best Bourbon at 2023 SFWSC). Wed–Sat 11–5 only. Rating 8.1. River Proof Barrel Experience ($29) is their signature tour. Trip builder pin: lat 38.7731, lng -83.9968. Smart pairing: Augusta + Becker & Bird (5-min walk).
- **General George Stillhouse & Distillery** (file: `distillery-general-george.html`) — Western KY craft distillery in Falls of Rough (Grayson County) at 1867 Junction Rd. Land once owned by George Washington. Joined KBT January 2026. Produces Founding Fox bourbon, gin, vodka; also Shakertown Spirits and Bluefield Bourbon. Three tour options: Ambassador's Tour + Thieving (1 hr, top pick), Founding Fox Tasting & Tour (40 min), Tasting in the Fox Den (30 min). Pricing not published — book via generalgeorgestillhouse.setmore.com. Rating 7.0. Phone: (702) 505-9481. Trip builder pin: lat 37.5546, lng -86.5132 (corrected July 2026 to the geocoded 1867 Junction Rd address; was 37.5607, -86.5326). Smart pairing: General George + Green River (~50 min).
- **Garrard County Distilling Co.** — SHUT DOWN. File `distillery-garrard-county.html` remains in repo but must NOT be added to the site anywhere.
- **Pensive Distilling Co.** (file: `distillery-pensive.html`) — Newport, KY craft distillery in a historic Prohibition-era building. Speakeasy tasting room requires a password (provided at booking). Named after Pensive, the 1944 Kentucky Derby/Preakness winner. On-site kitchen is award-winning (City Beat Top 10 NKY Restaurants); every menu item named after a racehorse. Live music Fridays. Tours $15–$25, easy booking via Peek. Rating 8.0. Pair with New Riff (5 min, same city). Trip builder pin: lat 39.09, lng -84.4923 (corrected July 2026 to the 720 Monmouth St, Newport address; was 38.9928, -84.4969, which sat ~6.7 mi south of Newport). Region: Northern (Newport maps to Northern in RG).
- **Stitzel-Weller gift shop accuracy** — Old Fitzgerald is now a Heaven Hill brand (produced in Bardstown); it is NOT available at Stitzel-Weller. Gift shop reliably carries Blade & Bow, I.W. Harper, and Bulleit. Orphan Barrel releases show up occasionally but cannot be counted on — do not present as a reliable find. The Old Fitz history is fine to mention as historical context (it was produced there), but don't imply visitors can buy it there.
- **WhistlePig The Vault** — Louisville tasting room at 403 E Market St (NuLu, near Angel's Envy), opened 2026. Vermont-based brand (rye-focused, not a KY distillery). **Now in scope for a tasting-room profile + card** (decision reversed July 2026). It was previously excluded on the grounds that it's "a brand experience room, not a production facility" — but that is exactly what `data-production="tasting"` now encodes, so the reason for excluding it expired once the directory could represent the distinction. Directory-only, like every urban tasting room: no trip-builder or map pin. Also covered as a callout card in the "Speakeasies & New Openings" section of `louisville-whiskey-row-walking-guide.html`. Key detail: original 1911 bank pneumatic tube system is used to mix and deliver drinks — visibly in action from your seat. Tasting tiers: $50 hosted (groups 4–10), $250 Vault Collection, $300 Vault Experience (up to 6 guests). Hours: Tue–Sat 10am–5pm. Cocktail bar is walk-in; seated tastings require reservation.
- **The Rickhouse Restaurant & Lounge** — is in BARDSTOWN at 112 Xavier Dr. Dinner only, closed Mondays. It is a legitimate bourbon-forward dinner spot. NEVER present it as a Frankfort option.
- **Rick's White Light Diner (Frankfort)** — appears closed as of late 2025. Do not recommend.
- **Bourbon on Main (Frankfort)** — verified Frankfort lunch option, bourbon-focused. Used as the Day 3 lunch recommendation replacing the nonexistent "Rick House" in Frankfort. Appears in itinerary, eat-and-drink, where-to-stay, and castle-key nearby card.
- **General George Stillhouse** — distillery card badge is "Official Trail" (joined KBT January 2026). The CLAUDE.md entry above this one predates that badge change; both are accurate: it is a craft producer AND on the official trail.
- **Pensive Distilling Co.** — distillery card badge is "Official Trail" (confirmed July 2026, not a craft-only listing). data-type stays "craft" in distilleries.html since it's a small producer; only the display badge is "Official Trail".
- **Region taxonomy decision (July 2026):** Public-facing copy on the site uses SIX regions: Louisville, Bardstown, Frankfort, Lexington/Lawrenceburg, Northern Kentucky, Western Kentucky. However, `map.html` filter buttons are Louisville/Bardstown/Frankfort/Lexington/Other (Northern and Western both normalize to "Other" on the map). `trip-builder.html` has more granular region buttons. Do NOT write copy telling users to "tap Western" or "tap Northern" on the map — those buttons do not exist there. Reference the Trip Builder instead for those regions.
- **Buffalo Trace is NOT an official Kentucky Bourbon Trail member** — Sazerac left the KDA in 2009 and never rejoined. Its profile badge and any card/label must say "Independent" / "Independent Distillery", never "Official Trail" or "Official Bourbon Trail". (A leftover official badge on the profile was caught and fixed July 2026.)
- **Booking data provenance (July 2026):** Booking tiers and lead times for the ten majors (Buffalo Trace, Angel's Envy, Maker's Mark, Woodford Reserve, Old Forester, Wild Turkey, Four Roses, Heaven Hill, Evan Williams, Jim Beam) were verified against official distillery reservation pages in July 2026. Tier definitions are now standardized site-wide: **Easy = walk-up or same-week, Moderate = book 1-3 weeks ahead, Hard = book 4+ weeks ahead** (calendars often open 2-3 months out). Buffalo Trace releases new dates weekly on Wednesdays at 10:00 AM Eastern, each release covering a 7-day window ~8 weeks out; never describe it as "no drop day" or "Monday mornings". Jim Beam main-line distillation at Clermont is paused for 2026 (tours/tastings/Kitchen Table all still operating). Hours blocks on distillery-wild-turkey.html, distillery-wilderness-trail.html, distillery-hartfield.html, and distillery-kentucky-artisan.html still carry the unverified copy-pasted template pattern and remain unverified. Next verification pass due before the 2027 index refresh.
- **Hardcoded distillery count policy:** Prefer removing hardcoded counts from all copy (onboarding, meta descriptions, etc.). Where a number is unavoidable, use the rounded "60+" form. Never hardcode exact counts in onboarding or empty-state copy in trip-builder.html — those numbers change when distilleries are added and go stale immediately.
