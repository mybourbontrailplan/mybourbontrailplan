# CLAUDE.md — mybourbontrailplan.com

## What This Is
Kyle's Kentucky Bourbon Trail trip planning website. Static HTML/CSS/JS site deployed on Netlify via GitHub auto-deploy. Also serves as a content marketing funnel for Kyle's Airbnb property (New Hope Bourbon Stop) near Bardstown, KY.

## Deployment
- **Repo:** github.com/mybourbontrailplan/mybourbontrailplan
- **Hosting:** Netlify with GitHub auto-deploy on push to `main`
- **Workflow:** `git pull` → make changes → `git add .` → `git commit -m "message"` → `git push`
- **No build tools, no framework, no CMS** — every page is a standalone HTML file at root level, with an `images/` subfolder for distillery photos

## Tech Stack
- Static HTML/CSS/JS
- Fonts: DM Sans (body) + Fraunces (display/headings)
- Maps: Leaflet.js with CartoDB Light tiles
- Analytics: Google Analytics (G-DVK4D6KJJP) on all pages
- Email marketing: MailerLite (account ID 2164831, universal script on every page after GA script)
- Affiliate links: Awin/Booking.com (tidd.ly short URLs), CJ Affiliate/VRBO, direct Airbnb
- Email obfuscation: Contact and About pages use JS-rendered email to prevent mangling
- Search Console verified via meta tag on all pages

## Design System
- Colors: Primary blue `#1B4F72`, accent gold `#D4A03C`, dark `#0E2F44`
- CSS variables: `--primary`, `--primary-light`, `--primary-dark`, `--accent`, `--accent-light`, `--font-display`, `--font-body`, `--text`, `--text-secondary`, `--text-light`, `--border`, `--bg-subtle`
- Style: Modern, clean, SaaS-inspired. White backgrounds, subtle shadows, rounded corners (12px)
- Icons: Custom two-tone SVGs (blue + gold) inside rounded-square containers on homepage. No emojis.

## File Structure

### Core Pages (9)
- `index.html` — Homepage
- `3-day-bourbon-trail-itinerary.html` — Flagship SEO page with 2/3/4-day trip selector
- `distilleries.html` — Directory with 59 filterable cards (region, type, booking) + sort by rating/A-Z; count is dynamically set on load via `applyFilters()`
- `map.html` — Static interactive map with 59+ distilleries; height is `calc(100vh - 120px)` so content below is visible on scroll. PDF map CTA card opens a modal (no `#pdf-signup` inline section — that was removed). Features: distillery search box in sidebar (dropdown autocomplete, fly-to on click), collapsible region legend on mobile (collapsed by default), Kentucky state border rendered via `L.geoJSON()` fetched from PublicaMundi US states GeoJSON (fails silently if unavailable), pin labels visible at zoom 9+. **URL deep-link support** via `applyDeepLink()` at end of script — supports `?region=` (fits bounds to region, activates filter button) and `?distillery=` (flies to marker at zoom 14, opens popup); both params together apply region filter then highlight distillery (falls back to distillery-only if distillery isn't in that region). Region param values: `louisville`, `bardstown`, `frankfort`, `lexington`, `other`; `northern`/`central`/`western` all normalize to `other`. Distillery slug matches the `distillery-{slug}.html` filename pattern. Note: map.html uses `marker.addTo(map)` / `map.removeLayer()` for filter toggling (unlike trip-builder.html which uses setOpacity).
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

### Distillery Profiles (59 active)
All named `distillery-{name}.html`. All use the standardized template (white frosted nav, snapshot cards, tour card headers, rating bars, verdict box, sidebar with quick details). Each has: rating, tour options/prices, booking difficulty, gift shop tips, verdict, nearby pairings with links, GA tracking, mobile menu, MailerLite universal script, OG tags, correct canonical URL.
- 60 HTML files exist in repo, but `distillery-garrard-county.html` is intentionally excluded — Garrard County Distilling Co. is shut down. Do NOT add it to `distilleries.html`, `trip-builder.html`, `map.html`, or `sitemap.xml`.

### Other
- `sitemap.xml` — 77 URLs, all using `mybourbontrailplan.com` domain
- `bourbon-trail-planning-checklist.pdf` — Lead magnet delivered via MailerLite
- `bourbon-trail-map.pdf` — Printable/downloadable bourbon trail map; linked from homepage and map.html
- `images/` — Distillery photos, named `{distillery}-1.jpg`, `{distillery}-2.jpg`, etc. All photos are EXIF-rotation-fixed and optimized for web (max 1200px, ~80% JPEG quality)

## Nav & Footer Template (ALL pages)
- **Top nav links (in order):** Plan Your Trip → Distilleries → Map → Where to Stay → Eat & Drink → Trip Builder → Guides → Booking Guide (CTA style)
- **Footer links (in order):** Home, Plan Your Trip, Distilleries, Map, Trip Builder, Guides, Where to Stay, Booking Guide, About, Contact — plus Instagram handle line and copyright
- Map must be a nav item on every new page created

## Distillery Profile Template Rules
When creating or editing distillery profiles:
- Use an existing profile like `distillery-buffalo-trace.html` as the canonical template reference
- All profiles MUST have: correct canonical URL (`https://mybourbontrailplan.com/filename.html`), OG tags (og:title, og:description, og:type, og:url), GA script, MailerLite universal script, `-webkit-text-size-adjust: 100%`
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

### Sidebar Contact Section — Standard Structure
All 59 profiles have a standardized Contact section. Order must be:
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
- Markers are added to the map ONCE and never removed from the DOM
- Visibility is controlled via `setOpacity(1/0)` and `pointerEvents` toggling
- **NEVER use `marker.addTo(map)` / `marker.removeFrom(map)` for showing/hiding** — this destroys DOM elements and breaks click handlers after repeated interactions

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

### handleZoom() Thresholds (all filter-aware)
- **Dot threshold** (`showThr`): `Math.min(10, RD[aRF].zoom)` when filtered, `10` when "All" — dots appear at the region's flyTo zoom
- **Label threshold** (`labelZoom`): same formula as dot threshold — labels and dots appear together
- **Back button** ("← All Regions"): shows at `z >= showThr` — visible as soon as dots appear
- **Region overlay buttons** (e.g. "Western 8 distilleries"): hidden when `show=true`, visible when `show=false`

### RG City-to-Region Mapping (trip-builder.html)
- `Newport:'Northern'` — New Riff and Pensive are both in Newport; they appear under the Northern filter
- Most other Northern KY cities (Independence, Ludlow, Sparta, Maysville, Paris, Burlington, Augusta) also map to `Northern`
- `Danville`, `Lebanon`, `Radcliff` map to `Other` (no dedicated region flyTo — shown only in "All" view)

### Region Data (RD) — flyTo destinations
- `Louisville`, `Bardstown`, `Frankfort`: zoom 14
- `Lexington`: zoom 11
- `Central`, `Northern`: zoom 10
- **`Western`: lat 37.13, lng -87.59, zoom 8** — spans 2+ degrees of longitude; zoom 10 is too close for mobile to see all 8 distilleries; center is midpoint of extremes (not geographic mean) for best viewport fit

### Western Button Mobile Repositioning
- On desktop the Western button marker sits at the `RD` flyTo center (–87.59), which is visible in the wide desktop viewport
- On mobile (< 900px), the initial overview viewport only spans ~2 degrees of longitude and the Western center is off-screen to the left
- **Mobile fix**: Western button marker is placed at `lat 37.3, lng -86.2` with `iconAnchor [0,28]` (left-aligned) so the button sits near the left edge of the initial mobile view and extends rightward into full view
- Clicking the button still `flyTo`s `RD.Western` (37.13, -87.59, zoom 8) — marker position and flyTo destination are separate
- Detection: `const isMobile = window.innerWidth < 900` at map init time

### Mobile Back Button ("← All Regions")
- `position:absolute; top:24px; left:12px` on mobile (bumped from 12px to 24px)
- The fixed action bar (`top:56px`, ~58px tall) bottoms out at ~114px; `.app` starts at 100px; old `top:12px` put the button at 112px — directly under the action bar
- `z-index:600` — stays below the action bar (800); the extra `top` clearance keeps it visually below, not z-fighting above

### Why Bottom Buttons Were Abandoned
iPhone Safari's dynamic bottom toolbar height isn't accounted for by `env(safe-area-inset-bottom)`. Multiple attempts with increased bottom values, dvh units, and @supports fallbacks all failed across iPhone 16 Pro and 17 Pro simultaneously. Top action bar eliminates all bottom-edge issues permanently.

### Adding a New Distillery to Trip Builder
1. Verify coordinates on Google Maps (right-click → copy coordinates)
2. Check for pin overlap with nearby distilleries at zoom 14 — pins must be 28px+ apart
3. Add to the distilleries array in trip-builder.html
4. Add smart pairing tip if there's a nearby distillery within 5 min drive
5. Update region counts in the code if applicable
6. Also add to `distilleries.html` and `sitemap.xml`

## SEO Notes
- All canonical URLs must point to `https://mybourbontrailplan.com/filename.html`
- All pages need OG tags (og:title, og:description, og:type, og:url)
- Title tags under 85 characters
- Meta descriptions under 170 characters
- Schema markup: Article (content pages), TouristAttraction (distillery profiles), CollectionPage (directory)
- Sitemap at `sitemap.xml` — update when adding any new page

## Affiliate Links — DO NOT modify these URLs
- Booking.com links use `tidd.ly` short URLs generated via Awin
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

### Free Resources Modal Pattern
Homepage and itinerary page have a unified "Free Trip Planning Resources" section with two gold-border cards side by side (stacking on mobile). Each card opens its own modal containing the MailerLite form — no inline embedded widgets in the page flow. Modal functions: `openPdfModal()` / `closePdfModal()` and `openChecklistModal()` / `closeChecklistModal()`. Both modals share z-index 2000 and close on outside click or Escape. map.html has the PDF map modal only (no checklist modal).

## Google Drive Artifact Files
The repo contains files named with ` (1)` suffixes (e.g., `distillery-chicken-cock (1).html`, `guides (1).html`). These are Google Drive sync duplicates — identical to the originals, not separate pages. Also `.tmp.driveupload/` folder accumulates Google Drive temp files. Neither should be edited or referenced; they can be cleaned up by deleting them, but they're harmless if left in place.

## Known Gotchas
- **Notepad++ Find in Files** was previously used for batch changes — with Claude Code, this is no longer needed. Just describe the batch change and Claude Code will handle it.
- **MailerLite universal script** must be on every new page (after GA script, before closing body tag)
- **GA script** must be on every new page (in head)
- **iOS Safari text inflation** — all pages need `-webkit-text-size-adjust: 100%` in the html CSS rule
- **No OverlappingMarkerSpiderfier** — was removed from the trip builder, don't re-add it
- **Barton 1792** no longer offers tours — gift shop and grounds only
- **Log Still is in New Haven, KY** (not New Hope) — Kyle's Airbnb is in New Hope, these are different places

## Content Accuracy Notes
- Kyle has real bourbon trail experience — the site reflects honest, opinionated reviews
- Distilleries CAN pay for featured listings but CANNOT change ratings (disclosed on About page)
- Visitor stat: "Record 2.7 million annual visitors and growing" (use as evergreen)
- Budget guide uses per-person pricing
- Three Boys Farm Distillery is now Whiskey Thief Distilling Co.
- **Chicken Cock rating is 7.0** — bar is smaller than expected, accessible area limited to bar + two front gift shop rooms. Old fashioned flight is a highlight worth mentioning.
- **Heaven's to Betsy Bakery** added to eat-and-drink page (On the Road section) and Wild Turkey nearby cards — Lawrenceburg, outstanding Reuben sandwich
- **Becker & Bird Distillery** (file: `distillery-baker-bird.html`) — the distillery's official KBT name is Becker & Bird; the winery on the same property is called Baker-Bird. File name stays as-is for URL continuity.
- **Augusta Distillery** (file: `distillery-augusta.html`) — separate from Becker & Bird, also in Augusta, KY at 207 Seminary Ave. Produces Buckner's bourbon (Best Bourbon at 2023 SFWSC). Wed–Sat 11–5 only. Rating 8.1. River Proof Barrel Experience ($29) is their signature tour. Trip builder pin: lat 38.7731, lng -83.9968. Smart pairing: Augusta + Becker & Bird (5-min walk).
- **General George Stillhouse & Distillery** (file: `distillery-general-george.html`) — Western KY craft distillery in Falls of Rough (Grayson County) at 1867 Junction Rd. Land once owned by George Washington. Joined KBT January 2026. Produces Founding Fox bourbon, gin, vodka; also Shakertown Spirits and Bluefield Bourbon. Three tour options: Ambassador's Tour + Thieving (1 hr, top pick), Founding Fox Tasting & Tour (40 min), Tasting in the Fox Den (30 min). Pricing not published — book via generalgeorgestillhouse.setmore.com. Rating 7.0. Phone: (702) 505-9481. Trip builder pin: lat 37.5607, lng -86.5326. Smart pairing: General George + Green River (~50 min).
- **Garrard County Distilling Co.** — SHUT DOWN. File `distillery-garrard-county.html` remains in repo but must NOT be added to the site anywhere.
- **Pensive Distilling Co.** (file: `distillery-pensive.html`) — Newport, KY craft distillery in a historic Prohibition-era building. Speakeasy tasting room requires a password (provided at booking). Named after Pensive, the 1944 Kentucky Derby/Preakness winner. On-site kitchen is award-winning (City Beat Top 10 NKY Restaurants); every menu item named after a racehorse. Live music Fridays. Tours $15–$25, easy booking via Peek. Rating 8.0. Pair with New Riff (5 min, same city). Trip builder pin: lat 38.9928, lng -84.4969. Region: Northern (Newport maps to Northern in RG).
- **Stitzel-Weller gift shop accuracy** — Old Fitzgerald is now a Heaven Hill brand (produced in Bardstown); it is NOT available at Stitzel-Weller. Gift shop reliably carries Blade & Bow, I.W. Harper, and Bulleit. Orphan Barrel releases show up occasionally but cannot be counted on — do not present as a reliable find. The Old Fitz history is fine to mention as historical context (it was produced there), but don't imply visitors can buy it there.
- **WhistlePig The Vault** — Louisville tasting room at 403 E Market St (NuLu, near Angel's Envy), opened 2026. Vermont-based brand (rye-focused, not a KY distillery). NOT added as a distillery profile — it's a brand experience room, not a production facility. Covered as a callout card in the "Speakeasies & New Openings" section of `louisville-whiskey-row-walking-guide.html`. Key detail: original 1911 bank pneumatic tube system is used to mix and deliver drinks — visibly in action from your seat. Tasting tiers: $50 hosted (groups 4–10), $250 Vault Collection, $300 Vault Experience (up to 6 guests). Hours: Tue–Sat 10am–5pm. Cocktail bar is walk-in; seated tastings require reservation.
