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
- `distilleries.html` — Directory with 56 filterable cards (region, type, booking) + sort by rating/A-Z
- `map.html` — Static interactive map with 56+ distilleries
- `trip-builder.html` — Interactive trip builder (see Trip Builder section below)
- `bourbon-trail-booking-guide.html` — 10-step booking checklist
- `bourbon-trail-budget-guide.html` — Per-person cost breakdown
- `where-to-stay-bourbon-trail.html` — Lodging guide with affiliate links
- `guides.html` — Blog/guides index page

### Content Pages
- `eat-and-drink-bourbon-trail.html` — Restaurant/bar guide by region
- `about.html` — Monetization disclosure, JS email rendering
- `contact.html` — JS email rendering

### Blog Posts
- `best-time-to-visit-bourbon-trail.html` — Month-by-month seasonal guide
- `bourbon-trail-non-bourbon-drinkers.html` — Guide for non-bourbon-drinking partners
- `louisville-whiskey-row-walking-guide.html` — Louisville Whiskey Row self-guided walking tour

### Distillery Profiles (56 total)
All named `distillery-{name}.html`. All use the standardized template (white frosted nav, snapshot cards, tour card headers, rating bars, verdict box, sidebar with quick details). Each has: rating, tour options/prices, booking difficulty, gift shop tips, verdict, nearby pairings with links, GA tracking, mobile menu, MailerLite universal script, OG tags, correct canonical URL.

### Other
- `sitemap.xml` — 70 URLs, all using `mybourbontrailplan.com` domain
- `bourbon-trail-planning-checklist.pdf` — Lead magnet delivered via MailerLite
- `images/` — Distillery photos, named `{distillery}-1.jpg`, `{distillery}-2.jpg`, etc. All photos are EXIF-rotation-fixed and optimized for web (max 1200px, ~80% JPEG quality)

## Distillery Profile Template Rules
When creating or editing distillery profiles:
- Use an existing profile like `distillery-buffalo-trace.html` as the canonical template reference
- All profiles MUST have: correct canonical URL (`https://mybourbontrailplan.com/filename.html`), OG tags (og:title, og:description, og:type, og:url), GA script, MailerLite universal script, `-webkit-text-size-adjust: 100%`
- Photo gallery section goes between "What to Expect" and "Tour Options", using the `.photo-gallery` / `.gallery-grid` classes
- Photos are referenced as `images/{distillery}-1.jpg` etc. — always use `loading="lazy"` on gallery images
- Gallery uses `aspect-ratio: 4/3` with `object-fit: cover` (NOT fixed height) to avoid cropping important content
- Use `repeat(3, 1fr)` grid for 3 photos, `repeat(2, 1fr)` for 4 photos
- Lightbox: each gallery page includes a `.gallery-lightbox` div and click-to-expand JS before `</body>` — tap any photo to see it full-screen
- Distilleries with photos so far: Willett (3), Heaven Hill (3), Chicken Cock (4), Lux Row (4), Larrikin (3), Preservation (3), Four Roses (4), Peerless (3), Wild Turkey (4), Maker's Mark (4), Old Forester (4), Buffalo Trace (4), Stitzel-Weller (4), Buzzard's Roost (3), Evan Williams (2)
- Nearby pairing cards must link to real profile pages (never `href="#"`)
- Restaurant cards link to `eat-and-drink-bourbon-trail.html`
- Sidebar region guides link to `guides.html`
- After creating a new profile: add it to `distilleries.html`, `trip-builder.html`, and `sitemap.xml`

## Trip Builder — Critical Technical Notes

### Architecture
- 56 distilleries with Leaflet.js markers, region filters, smart pairing tips
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
- Signup forms on: homepage, trip builder, itinerary page, booking guide
- 3-email nurture sequence active (Day 3: top distilleries, Day 6: where to stay featuring Kyle's property, Day 10: booking mistakes)
- Lead magnet: PDF checklist delivered via welcome automation

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
- **Chicken Cock rating lowered to 7.0** (from 7.8) — bar is smaller than expected, accessible area limited to bar + two front gift shop rooms. Old fashioned flight is a highlight worth mentioning.
- **Heaven's to Betsy Bakery** added to eat-and-drink page (On the Road section) and Wild Turkey nearby cards — Lawrenceburg, outstanding Reuben sandwich
