# Bourbon Trail Planner — Project Context

## What This Is
Kyle is building mybourbontrailplan.com — a Kentucky Bourbon Trail trip planning website that doubles as a content marketing funnel for his Airbnb property near Bardstown/New Hope, KY. The site is live and deployed on Netlify. Monetization has begun with Booking.com affiliate links via Awin.

## Business Model
- SEO-first content site providing genuine, experience-based bourbon trail planning resources
- Lead magnet: Free 3-page PDF planning checklist captured via email signup (MailerLite — live and working)
- Revenue streams (ACTIVE): Booking.com affiliate links on all 10 named lodging properties via Awin, VRBO affiliate link for Kyle's property via CJ Affiliate (Expedia Group), direct Airbnb listing link for Kyle's property, email nurture sequence → lodging conversions
- Revenue streams (PLANNED): Featured distillery placements (paid listings with editorial independence), premium content, additional affiliate partnerships (Airbnb affiliate if available, guided tour company referral fees), direct lodging sponsorships once traffic data demonstrates click volume
- Target audience: 2.7M+ annual Kentucky Bourbon Trail visitors, especially first-timers planning multi-day trips
- Key differentiator: Opinionated, honest reviews vs. generic travel content. Kyle has real trail experience and the site reflects that.

## Design System
- Fonts: DM Sans (body) + Fraunces (display/headings)
- Colors: Primary blue #1B4F72, accent gold #D4A03C, dark #0E2F44
- Style: Modern, clean SaaS-inspired. White backgrounds, subtle shadows, rounded corners (12px), professional but warm
- CSS variables: --primary, --primary-light, --primary-dark, --accent, --accent-light, --font-display, --font-body, --text, --text-secondary, --text-light, --border, --bg-subtle
- Icons: Custom two-tone SVGs (blue + gold) inside rounded-square containers on homepage. No emojis.

## Technical Stack
- Hosting: Netlify (free tier, deploy limit resets monthly). Domain registered through Netlify, nameservers are nsone.net.
- Chromebook deploy: npx netlify-cli deploy --prod --dir=/mnt/chromeos/MyFiles/Downloads/Trail
- Windows PC deploy: netlify deploy --prod --dir=. (from inside site folder — make sure you're NOT inside the Node.js REPL; use Command Prompt)
- Analytics: Google Analytics (G-DVK4D6KJJP) on all pages
- Search Console: Verified (meta tag on all pages)
- Email marketing: MailerLite (free plan, account ID 2164831). See Email & Lead Gen section below.
- Email: hello@mybourbontrailplan.com
- Email obfuscation: Contact and About pages use JS-rendered email to prevent Cloudflare mangling
- Maps: Leaflet.js with CartoDB Light tiles (NO OverlappingMarkerSpiderfier — removed, see Trip Builder section)
- Affiliate: Awin network (Booking.com advertiser, tidd.ly short URLs), CJ Affiliate (VRBO/Expedia Group, vrbo.com/affiliate/ links)
- All pages are static HTML/CSS/JS — no build tools, no framework, no CMS

## SEO Status (Completed March 2026)
All pages have been audited and optimized:
- **Canonical URLs:** All pages point to `https://mybourbontrailplan.com/filename.html` (previously some pointed to wrong domain `bourbontrailplanner.com`)
- **Open Graph tags:** og:title, og:description, og:type, og:url on all pages (enables proper social sharing previews)
- **Title tags:** All under 85 chars (previously some were 120+ and getting truncated in Google)
- **Meta descriptions:** All under 170 chars (previously some were 200+)
- **`-webkit-text-size-adjust: 100%`:** Added to all pages (prevents iOS Safari from auto-inflating multi-line text)
- **Schema markup:** Article (content pages), TouristAttraction (distillery profiles), CollectionPage (directory), WebApplication (trip builder — pending)
- **Sitemap:** sitemap.xml with 69 URLs, all using correct mybourbontrailplan.com domain
- **Batch SEO fix method:** For the ~53 distillery profiles not individually edited, Kyle ran Notepad++ Find in Files replacements to fix canonicals, add OG tags, and add text-size-adjust across all files at once

## Complete File Inventory

### Core Pages (9)
- index.html — Homepage with hero, feature cards (custom SVG icons), popular guides, MailerLite email CTA. Gold "Build Your Trip" button links to trip-builder.html.
- 3-day-bourbon-trail-itinerary.html — Flagship SEO page. 2/3/4-day trip selector with collapsible day cards. Packing section includes portable fan for summer. MailerLite signup form before footer. Lodging cards link to Kyle's Airbnb (Booking.com affiliate + Airbnb + VRBO affiliate) and Talbott Tavern (affiliate). Transportation section includes WhiskMe Transportation, Mint Julep Experiences, and Louisville Bourbon Tours.
- distilleries.html — Directory with 55 filterable cards (region, type, booking) + sort by rating or A-Z. "Other Regions" filter included.
- map.html — Static interactive map with 56+ distilleries, region filters, 3 driving routes (older page)
- trip-builder.html — Interactive trip builder with 55 distilleries (see detailed section below)
- bourbon-trail-booking-guide.html — Step-by-step booking strategy, 10-step checklist. MailerLite signup form before footer. Transportation section mentions WhiskMe and Mint Julep.
- bourbon-trail-budget-guide.html — Per-person cost breakdown for budget and premium trips
- where-to-stay-bourbon-trail.html — Lodging guide with Booking.com affiliate links on ALL 10 named properties + VRBO affiliate on Kyle's property
- guides.html — Blog/guides index page with card layout linking to all content pages and blog posts. "Guides" link in nav across all site pages.

### Content Pages (4)
- eat-and-drink-bourbon-trail.html — Restaurant/bar guide by region. Includes Evergreen Liquors (Bardstown), La Bodeguita de Mima (Louisville NuLu). No day numbers in headers.
- about.html — Monetization disclosure. JS email rendering.
- contact.html — JS email rendering.
- sitemap.xml — XML sitemap with all 56 distillery profiles + core pages + blog posts (69 URLs total)

### Blog Posts (2)
- best-time-to-visit-bourbon-trail.html — Month-by-month seasonal guide covering weather, crowds, warehouse temperatures, bourbon releases. Targets "best time to visit bourbon trail" keywords.
- bourbon-trail-non-bourbon-drinkers.html — Guide for couples where one partner doesn't drink bourbon. Recommends Castle & Key (gin), Copper & Kings (brandy), Michter's (cocktails), Chicken Cock (bar). Includes sample 3-day couples itinerary.

### Distillery Profiles (56 total)
Each has: rating, tour options/prices, booking difficulty, gift shop tips, verdict, nearby pairings with links, GA tracking, mobile menu, MailerLite universal script, OG tags, correct canonical URL. **ALL profiles now use the standardized "good" template** (white frosted nav, snapshot cards, tour card headers, rating bars, verdict box, sidebar with quick details). **All href="#" placeholder links have been fixed** — distillery nearby cards link to real profiles, restaurant cards link to eat-and-drink page, sidebar region guides link to guides.html.

**Louisville (9):** Angel's Envy (8.8), Old Forester (8.9), Evan Williams (8.7), Rabbit Hole (7.9), Michter's (8.6), Kentucky Peerless (8.2), Whiskey Thief (7.5), Copper & Kings (8.3), Stitzel-Weller (8.6)

**Bardstown (11):** Maker's Mark (9.0), Heaven Hill (8.5), Willett (8.2), Bardstown Bourbon Co. (8.5), Lux Row (8.0), Preservation (7.5), Log Still (7.8), Barton 1792 (7.6 — NO LONGER OFFERING TOURS, gift shop only), Jim Beam (8.4), The Bard (7.4), Chicken Cock Whiskey (7.8 — Circa 1856 bar/tasting room/micro-distillery, 103 E Stephen Foster Ave, books via Resy)

**Frankfort (4):** Buffalo Trace (9.2), Castle & Key (8.3), Glenns Creek (7.6), J. Mattingly 1845 (7.9)

**Lexington (8):** Woodford Reserve (8.5), Wild Turkey (8.1), Four Roses (8.3), Town Branch (7.4), James E. Pepper (7.8), Barrel House (7.5), Fresh Bourbon (8.2), RD1 Spirits (8.4)

**Central (5):** Bulleit (8.0), Jeptha Creed (8.0), Kentucky Artisan (8.0), Bluegrass Distillers (7.7), Larrikin (7.3)

**Northern (8):** New Riff (8.4), Boone County (7.8), Second Sight (7.5), Neeley Family (7.2), Old Pogue (7.4), Hartfield & Co. (7.6), Wenzel (7.3), Becker & Bird (7.5)

**Western (8):** Wilderness Trail (8.3), Green River (8.1), Casey Jones (7.5), MB Roland (7.4), Dueling Grounds (7.3), B.H. James (7.2), Golden Pond (7.1), Jackson Purchase (7.3)

**Other (3):** Limestone Branch (7.9), Boundary Oak (7.3)

### Lead Magnet
- bourbon-trail-planning-checklist.pdf — 3-page PDF: booking timeline, schedule, packing list, budget worksheet. Hosted on Netlify at mybourbontrailplan.com/bourbon-trail-planning-checklist.pdf. Delivered via MailerLite welcome automation.

## Monetization — Affiliate Links (LIVE)

### Awin / Booking.com Setup
- **Network:** Awin (affiliate.booking.com routes through Awin)
- **Advertiser:** Booking.com (search "Booking" in Awin advertiser directory)
- **Link format:** tidd.ly short URLs generated via Awin Link Builder
- **Commission:** Earned on ANY Booking.com property booked through the affiliate link (not just the linked property). Cookie window ~30 days.

### Active Affiliate Links
**where-to-stay-bourbon-trail.html (10 links):**
- The New Hope Bourbon Stop (Kyle's property): `https://tidd.ly/4scCPU3` + direct Airbnb + direct VRBO
- Hotel Distil (Louisville): `https://tidd.ly/4rmKbD4`
- Omni Louisville: `https://tidd.ly/4utpUPh`
- 21c Museum Hotel Louisville: `https://tidd.ly/4bfe16C`
- Hampton Inn Downtown Louisville: `https://tidd.ly/4rq4qzZ`
- Bardstown Motor Lodge: `https://tidd.ly/4bixMds`
- Old Talbott Tavern & Inn: `https://tidd.ly/4blCaIQ`
- Capital Plaza Hotel (Frankfort): `https://tidd.ly/46U1lRk`
- 21c Museum Hotel Lexington: `https://tidd.ly/4lvKDh9`
- Hilton Lexington Downtown: `https://tidd.ly/4cFuH9U`

**3-day-bourbon-trail-itinerary.html (2 links):**
- New Hope Bourbon Stop: Booking.com affiliate + Airbnb + VRBO
- Old Talbott Tavern: Booking.com affiliate

**trip-builder.html (itinerary export):**
- Multi-day trips include lodging callout with Booking.com affiliate link + Airbnb + VRBO for Kyle's property

### Kyle's Direct Property Links
- **Airbnb:** https://www.airbnb.com/rooms/1133406907482529297
- **VRBO (affiliate):** https://vrbo.com/affiliate/VD0a4b2
- **Booking.com (affiliate):** https://tidd.ly/4scCPU3

### CJ Affiliate / VRBO Setup
- **Network:** CJ Affiliate (formerly Commission Junction)
- **Advertiser:** Expedia Group (VRBO)
- **Link format:** vrbo.com/affiliate/ URLs generated via CJ link builder
- **Active on:** where-to-stay-bourbon-trail.html (Kyle's property), 3-day-bourbon-trail-itinerary.html, trip-builder.html (mailto export)
- **Cookie window:** ~7 days (shorter than Booking.com's ~30 days)

### Lodging Link Button Styles
```css
.lodging-link-btn.btn-booking { background: rgba(0,53,128,0.06); color: #003580; } /* Booking.com blue */
.lodging-link-btn.btn-airbnb { background: rgba(255,56,92,0.08); color: #FF385C; }  /* Airbnb pink */
.lodging-link-btn.btn-vrbo { background: rgba(0,42,130,0.06); color: #002A82; }     /* VRBO navy */
```

## Email & Lead Gen (MailerLite — LIVE)

Switched from Mailchimp (free plan couldn't do automations) to MailerLite (free plan, 500 subscribers, 12,000 emails/month, automations included).

### Current Setup
- **Platform:** MailerLite, account ID `2164831`
- **Subscriber group:** Bourbon Trail Planners
- **Custom fields:** `itinerary` (text), `signup_source` (text — "source" was reserved by MailerLite)
- **Domain:** Authenticated via DNS (DKIM CNAME + TXT records added in Netlify DNS panel)
- **Embedded form ID:** `WD5yKI`
- **Universal script:** Installed on ALL HTML pages (inserted after GA script). Script: `ml('account','2164831')`
- **Welcome automation:** Live and tested. Triggers on group join, sends email with PDF download link.
- **Nurture sequence (LIVE):** 3 follow-up emails in MailerLite automation after welcome:
  - Email 2 (Day 3): "The 5 distilleries you shouldn't skip" — Buffalo Trace, Maker's Mark, Heaven Hill, Peerless, Preservation
  - Email 3 (Day 6): "Where to stay on the Bourbon Trail" — features Kyle's Airbnb with Booking.com affiliate, Airbnb, and VRBO affiliate links
  - Email 4 (Day 10): "Before you go: 3 booking mistakes" — Buffalo Trace timing, pacing advice, seasonal tips
  - Creates passive conversion path: email signup → nurture → lodging booking (affiliate revenue)

### Form Placements
- **index.html** — MailerLite embed in CTA section (replaced old dead input/button)
- **trip-builder.html** — MailerLite embed inside email capture modal (user clicks "Email Me This Itinerary" → clipboard copy + modal with signup form)
- **3-day-bourbon-trail-itinerary.html** — MailerLite embed section before footer
- **bourbon-trail-booking-guide.html** — MailerLite embed section before footer

### Trip Builder Email Flow
1. User clicks "Email Me This Itinerary" (in sidebar header on mobile, footer on desktop)
2. User's default email app opens via mailto: link with subject "My Bourbon Trail Itinerary" and full itinerary pre-filled in body
3. Itinerary also copies to clipboard as fallback (iOS-safe hidden textarea + execCommand)
4. After 800ms delay, MailerLite signup modal appears offering free checklist
5. Modal contains MailerLite embedded form (form ID WD5yKI)
6. If user signs up → welcome automation delivers PDF → nurture sequence begins
7. If user dismisses → they still have itinerary in their email app and on clipboard
- Tested with 15 distilleries across 3 days — no mailto truncation issues

### Itinerary Export Format
The clipboard export now includes: day-by-day stops with region/cost/booking info, drive times between stops, booking lead time warnings for moderate/hard bookings, smart tips (pairing suggestions, pacing warnings), trip summary with total cost, lodging suggestion with affiliate links for multi-day trips, and site URL.

### MailerLite Free Plan Limits
- 500 subscribers max
- 12,000 emails/month
- MailerLite logo on emails (can't remove on free plan)
- No email templates (design from scratch)
- Automations included (up to 100 steps)

## Trip Builder (trip-builder.html) — Flagship Feature

Three-panel layout on desktop. Mobile-optimized with floating Browse/Your Trip buttons. Differentiates from KDA's tool: no account needed, opinionated ratings, smart tips, cost tracking.

### Current State (Rollout 2 Complete + Mobile Optimization + Chicken Cock)
The trip builder contains **55 distilleries** across 8 regions: Louisville (9), Bardstown (11), Frankfort (4), Lexington (9), Central (4), Northern (7), Western (7), Other (4). All 55 have profile page links.

### Mobile Experience (Updated March 2026)
- **Breakpoint:** 900px (not 768px — needed for iPhone Pro models)
- **Top action bar** (replaces old floating bottom buttons): Fixed bar below nav at `top: 56px` containing "Browse" and "Your Trip (N)" buttons side by side. Uses `position: fixed` with frosted glass background. This approach eliminates all Safari bottom toolbar / safe area issues that plagued the previous floating bottom button design across different iPhone models.
- **Old floating buttons (`mobile-browse-btn`, `mobile-trip-toggle`)** are set to `display:none!important` on mobile — kept in HTML for desktop fallback but never shown on mobile.
- **`.mobile-action-bar`** is `display:none` by default (desktop), `display:flex` inside `@media(max-width:900px)`. z-index 800.
- **`.app` margin-top** changes from 56px (desktop) to 100px (mobile) to account for nav + action bar height.
- **Browse panel:** Full-screen overlay with × close button in header. Tapping a distillery flies to it on map and closes panel.
- **Your Trip panel:** Slides up from bottom (max-height 90vh), scrollable with `-webkit-overflow-scrolling:touch`. Has × close button and "Tap to close" drawer handle.
- **"Email Me This Itinerary" and "Clear" buttons** are in the **sidebar header** on mobile (not footer), so they're always visible at the top of the Your Trip panel regardless of scroll position or safe area. The desktop footer buttons are hidden on mobile via CSS.
- **Hamburger menu:** z-index 1001 with 44×44px touch target, dropdown at z-index 1100
- **Email modal:** z-index 2000 (above everything)
- **viewport meta:** includes `viewport-fit=cover`
- **Trip badge count** updates in both the top action bar (`tripBadgeTop`) and the old toggle button (`tripBadge`) via `updateTripBadge()`

### Key Mobile z-index Stack (IMPORTANT)
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
Previous approach used `bottom: calc(120px + env(safe-area-inset-bottom))` to position floating Browse/Your Trip buttons above the iPhone home indicator. This failed on iPhone 16 Pro where Safari's dynamic bottom toolbar height wasn't accounted for by `env(safe-area-inset-bottom)`. Buttons were hidden behind the toolbar on initial load, only becoming visible after a tap collapsed the toolbar. Multiple attempts with increased `bottom` values, `dvh` units, and `@supports` fallbacks all failed to work consistently across iPhone 16 Pro and 17 Pro simultaneously. Moving buttons to a fixed top bar eliminates all bottom-edge positioning issues permanently.

### Navigation
Trip Builder is linked from: homepage hero button ("Build Your Trip"), plus a "Trip Builder" link in the nav/footer across all site pages. The main nav bar across the site is: Itineraries | Distilleries | Where to Stay | Eat & Drink | Guides | Booking Guide (CTA button). Trip Builder links appear as secondary nav elements and the homepage hero CTA.

### LEFT PANEL — Browse & Search
- Searchable/filterable list of distilleries, sorted by rating
- Region filter pills: All, Louisville, Bardstown, Frankfort, Lexington, Central, Northern, Western, Other
- Each row: name, region, cost, booking lead time, rating, color-coded dot (green=easy, orange=moderate, red=hard)
- Click row to zoom on map (flies to zoom 16). Click + to add to current day.
- Booking legend at bottom
- Mobile: × close button in header to return to map

### CENTER PANEL — Map
- Leaflet.js with CartoDB Light tiles
- Starts zoomed out (zoom 8) with 7 clickable region cards showing distillery counts
- Click region to zoom in, see individual pins, auto-filter browse list
- "All Regions" button zooms back out
- Trip stops always visible with colored numbered markers (Day1=blue #2980B9, Day2=gold #D4A03C, Day3=green #2E8B57, Day4=purple #8E44AD)
- Dashed route lines between stops, color-coded by day

### CENTER PANEL — Map Pin Architecture (IMPORTANT FOR FUTURE WORK)

**How markers work:**
- Markers are created once during `initMap()` but NOT added to the map initially (`_onMap: false`)
- `_addPin(id)` / `_removePin(id)` physically add/remove markers from the map (not opacity toggling)
- `handleZoom()` fires on `zoomend` and `moveend` (debounced 200ms) and decides which pins to show
- Uses pre-computed Set of trip IDs for performance (avoids re-flattening trip object per pin)
- When zoom >= 10: all pins are added to map. When zoom < 10: only trip stops remain visible.
- Region cards use inverse logic: visible when zoomed out, hidden when zoomed in

**Pin colors by booking difficulty:**
- Easy (green): #2E8B57
- Moderate (orange): #E67E22
- Hard (red): #C0392B

**Why OverlappingMarkerSpiderfier was removed:**
OMS caused persistent click issues — bottom markers in overlapping pairs would "shake" on click but never open popups. The root cause is Leaflet's DOM z-index event handling: when two markers overlap in pixel space, only the topmost marker receives click events regardless of any workaround.

**Current solution — separation by zoom level:**
All region zoom levels are set to 14 (except Lexington at 11), where all pins are physically separated by 28px+ in every region. No clustering library or logic is needed.

**Critical constraint for adding new distilleries:**
When adding new distilleries, their coordinates MUST be verified against the real physical address. Bad coordinates were the #1 source of bugs in this build.

**Before adding any new distillery to the trip builder, verify:**
1. Look up the actual street address
2. Convert to lat/lng coordinates (Google Maps, geocoding API, or historical marker databases)
3. Calculate pixel distance to ALL nearby pins at zoom 14: `pixelDist = sqrt((dlat*ppd*cos(lat))^2 + (dlng*ppd)^2)` where `ppd = 256 * (2^14) / 360`
4. If any pair is < 28px at zoom 14, either adjust coordinates slightly or bump that region's zoom to 15

**Pin coordinate adjustments made:**
- Preservation Distillery: nudged from (37.8090, -85.4670) to (37.8065, -85.4690) to increase separation from Heaven Hill. Was 44.5px apart, now 79px at zoom 14.

**Bugs fixed (March 2026):**
1. `refreshIcons()` referenced undefined `id` variable — should have been `s.id`. Caused trip markers to silently fail on re-pinning after move/clear operations.
2. `bindPopup()` stacking — every click added a new popup binding without unbinding the old one. Fixed by calling `unbindPopup()` before `bindPopup()`.
3. `handleZoom()` performance — was doing `Object.values(trip).flat().some()` inside a loop over all 54 distilleries. Optimized with a pre-computed `Set` of trip IDs.
4. `highlightOnMap` ghost popups — rapid browse list clicks could fire stale `setTimeout` callbacks. Added a target guard (`_hlTarget`).

### RIGHT PANEL — Your Trip
- Day 1/2/3 tabs + Day 4 option
- Stop cards with drive times (Haversine, 1.3x straight line, 45mph avg)
- Move-to-day dropdown and remove button
- Smart tips engine:
  - Pairing suggestions (21 coded pairs with proximity info)
  - Pacing warnings at 4+ stops/day
  - Booking alerts for hard-to-book distilleries
  - Region-mixing warnings at 3+ regions/day
- Stats footer: stops, drive time, tour cost, active days
- "Email Me This Itinerary" → opens mailto: with itinerary pre-filled + clipboard copy + MailerLite signup modal
- Onboarding overlay for first-time visitors (localStorage)

### Smart Tip Pairings (21 total):
- Buffalo Trace + Castle & Key (10 min, Frankfort)
- Old Forester + Evan Williams (2 min walk, Whiskey Row)
- Old Forester + Michter's (neighbors, Whiskey Row)
- Michter's + Peerless (3 min walk, closest in Louisville)
- Heaven Hill + Preservation (minutes apart, Bardstown)
- Heaven Hill + Willett (down the road)
- Woodford + Wild Turkey (20 min, horse country)
- Woodford + Four Roses (close, natural pairing)
- Maker's Mark + Heaven Hill (30 min, Bardstown day)
- Glenns Creek + Buffalo Trace (15 min, Frankfort)
- Glenns Creek + Castle & Key (same road)
- J. Mattingly + Buffalo Trace (5 min, downtown Frankfort)
- James E. Pepper + Barrel House (neighbors, Distillery District)
- Copper & Kings + Rabbit Hole (Butchertown/NuLu walk)
- Boone County + Second Sight (Northern KY day)
- New Riff + Second Sight (5 min, Northern KY)
- Casey Jones + Dueling Grounds (TN border combo)
- MB Roland + Casey Jones (Western KY craft day)
- Green River + B.H. James (Owensboro area)
- Bulleit + Jeptha Creed (Shelbyville, 15 min)
- Chicken Cock + The Bard (3-min walk, downtown Bardstown)

### Booking Warnings: Buffalo Trace (6-8 wks), Angel's Envy (4-6 wks), Maker's Mark (4-6 wks)

### Region Zoom Configuration:
```
Louisville:  lat:38.257, lng:-85.755, zoom:14
Bardstown:   lat:37.81,  lng:-85.47,  zoom:14
Frankfort:   lat:38.210, lng:-84.871, zoom:14
Lexington:   lat:38.035, lng:-84.76,  zoom:11
Central:     lat:38.05,  lng:-85.15,  zoom:10
Northern:    lat:38.85,  lng:-84.55,  zoom:9
Western:     lat:37.2,   lng:-87.2,   zoom:8
```

### Region Grouping (RG map):
Cities map to display regions via the `grp()` function. Current mappings:
```
Louisville→Louisville, Bardstown→Bardstown, Loretto→Bardstown, Clermont→Bardstown,
Frankfort→Frankfort, Versailles→Lexington, Lawrenceburg→Lexington, Lexington→Lexington,
Midway→Lexington, Shelbyville→Central, Crestwood→Central, Independence→Northern,
Ludlow→Northern, Sparta→Northern, Maysville→Northern, Paris→Northern, Burlington→Northern,
Augusta→Northern, Owensboro→Western, Hopkinsville→Western, Pembroke→Western,
Franklin→Western, Whitesville→Western, Eddyville→Western, Murray→Western,
Lebanon→Other, Radcliff→Other, Newport→Other, Danville→Other,
Central→Central, Northern→Northern, Western→Western
```

## Cross-Linking Structure
- Consistent nav on all pages: Itineraries, Distilleries, Where to Stay, Eat & Drink, Guides, Booking Guide (CTA)
- Trip Builder linked from homepage hero and nav/footer across all pages
- Guides page links to both blog posts + all core content pages
- Blog posts cross-link to each other and to core pages (itinerary, booking guide, where-to-stay, budget guide, distillery profiles)
- Distillery profiles link to nearby profiles in "Nearby & Pair With" sections (all href="#" placeholders fixed)
- Distillery profiles link to nearby profiles in "Nearby & Pair With" sections
- Michter's and Peerless cross-reference each other (3-min walk)
- Directory cards link to all 54 profiles
- Trip builder map pins link to profiles via popup "Read full guide" links
- All "Keep Planning" sections at page bottoms now link to actual pages (no more href="#" placeholders on core pages)

## Key Content Details to Maintain
- Penelope Bourbon is the highlight at Lux Row (not Ezra Brooks)
- Buffalo Trace gift shop: Weller Special Reserve usually available now. Weekly rotation of Blanton's, Weller Antique 107, Eagle Rare, EH Taylor Small Batch. Occasional special allocated bottles.
- Preservation on Day 2 in itinerary (moved from Day 3)
- Visitor numbers: "Record 2.7 million annual visitors and growing" (evergreen)
- Budget guide uses per-person pricing
- Bardstown taxi services in itinerary
- Louisville bonus distilleries section in itinerary
- Portable fan in packing section for summer visits
- About page: distilleries CAN pay for featured listings, CANNOT change ratings
- Three Boys Farm Distillery is now Whiskey Thief Distilling Co.
- Whiskey Thief has two locations: Frankfort farm (distillery) and Louisville NuLu (tasting room at 610 Nanny Goat Strut). The site lists the Louisville NuLu location. Standout experience is barrel "thieving" — draw bourbon from barrels and bottle your own.
- **Barton 1792 no longer offers tours** — gift shop and grounds only. Profile page, trip builder, and distilleries directory all updated.
- **Log Still is in New Haven, KY** (NOT New Hope). Kyle's Airbnb "New Hope Bourbon Stop" IS in New Hope — these are different places. Log Still also has The Amp, an on-site concert venue.
- Transportation options mention WhiskMe Transportation (Bardstown-based, whiskmetransportation.com), Mint Julep Experiences, and Louisville Bourbon Tours
- Wild Turkey has tasting-only options and one of the best bars on the trail
- Jim Beam has a notable on-site restaurant worth building into your schedule
- Distilleries page has sort by rating and A-Z functionality

## Recent Content Updates (Completed This Session — March 2026)

### Template Standardization (COMPLETED)
All 30 "bad format" distillery profile pages converted to the "good" Buffalo Trace format via Python conversion script. All 56 profiles now use consistent template.

### Dead Link Cleanup (COMPLETED)
All 236 href="#" placeholder links fixed across all distillery profiles: 207 nearby cards (distillery cards → real profile pages, restaurant cards → eat-and-drink-bourbon-trail.html), 25 sidebar links (region guides → guides.html), plus 4 miscellaneous on core pages.

### New Distillery: Chicken Cock Whiskey Circa 1856 (Bardstown)
- Profile page: distillery-chicken-cock.html (7.8 rating, bar/tasting room/micro-distillery)
- Address: 103 E Stephen Foster Ave, Bardstown, KY 40004 (across from Talbott Tavern)
- Hours: Mon–Wed 11–6, Thu–Sat 11–8, Sun 1–5. Books via Resy.
- Added to distilleries.html (55 cards), trip builder (55 distilleries), sitemap
- Trip builder coordinates: lat 37.8095, lng -85.4658. Smart pairing: Chicken Cock + The Bard (3-min walk)

### Email Nurture Sequence (LIVE in MailerLite)
3 follow-up emails added to automation after welcome email (Day 3, Day 6, Day 10).

### Blog/Guides Section (NEW)
- guides.html hub page, "Guides" link added to nav across all pages
- best-time-to-visit-bourbon-trail.html — seasonal guide
- bourbon-trail-non-bourbon-drinkers.html — couples/non-drinker guide
- Blog content strategy: 1–2 posts per month targeting long-tail SEO keywords

### VRBO Affiliate (LIVE)
- CJ Affiliate (Expedia Group). Link: https://vrbo.com/affiliate/VD0a4b2
- Replaced direct VRBO links on where-to-stay, itinerary, and trip builder export

### Trip Builder Updates
- mailto: link now opens user's email app with itinerary pre-filled (replaces clipboard-only)
- Mobile Browse/Your Trip buttons moved from floating bottom position to **fixed top action bar** below nav — eliminates Safari bottom toolbar issues across all iPhone models
- Mobile "Email Me This Itinerary" and "Clear" buttons moved to sidebar header (always visible, no safe area clipping)
- Fresh Bourbon coordinates nudged from (38.037, -84.748) to (38.035, -84.750) to fix pin overlap with Woodford Reserve at zoom 10

### Bug Fixes
- Dueling Grounds website link fixed → duelinggroundsdistillery.com
- Buffalo Trace fake Google Maps link fixed → real Google Maps search URL
- gtag visibility bug fixed by Kyle via Notepad++

### Prior Session Content Updates (Still Current)
- **Buffalo Trace** — Gift shop: Weller Special Reserve usually available, weekly rotation of Blanton's/Weller Antique 107/Eagle Rare/EH Taylor Small Batch
- **Heaven Hill** — Book link fixed → heavenhilldistillery.com
- **Wild Turkey** — Added tasting-only option, on-site bar mention
- **Jim Beam** — Added restaurant mention
- **Log Still** — Location fixed to New Haven, added The Amp
- **Peerless** — Book link fixed
- **Town Branch** — Book link fixed
- **Whiskey Thief** — Added barrel thieving experience
- **Barton 1792** — No longer offering tours, gift shop only

## Pending Items

### Medium Priority — Remaining Cleanup
- Email forwarding: Set up ImprovMX or Cloudflare for hello@mybourbontrailplan.com so replies work

### Medium Priority — SEO & Content Growth
- **Google Search Console:** Check indexing status, request indexing for top pages
- **Backlink building:** Share guides in bourbon subreddits/Facebook groups, reach out to distilleries about linking to their profile pages
- **Google Business Profile:** Set up for New Hope Bourbon Stop property with link to site
- **Upcoming blog post ideas:** Buffalo Trace gift shop guide (allocated bottles), Bourbon Trail packing list, bourbon trail with kids, bourbon trail in winter, best free tours on the bourbon trail
- Satellite tasting room profiles (Bardstown Bourbon Co. Louisville, Monk's Road Louisville) — lower priority
- Heaven's Door Distillery (Pleasureville) — watch for opening
- Approach lodging properties for direct sponsorship once traffic demonstrates click volume

### Future Features
- Trip builder V3: shareable URLs, social sharing
- Trip builder V4: booking links, affiliate partnerships within trip builder UI
- Trip builder V5: restaurant/lodging suggestions by route region
- Premium trip builder features (personalized itinerary generation, availability alerts)
- Group planning tools

## Deployment Notes
- Site: mybourbontrailplan.com on Netlify (domain registered through Netlify)
- DNS managed via Netlify (nameservers: dns1-4.p09.nsone.net)
- Single flat folder, no subdirectories
- Chromebook: npx netlify-cli deploy --prod --dir=/mnt/chromeos/MyFiles/Downloads/Trail
- Windows: netlify deploy --prod --dir=. (from site folder, in Command Prompt, NOT Node.js REPL)
- Trail folder must be shared with Linux on Chromebook
- Batch changes to minimize deploys (free tier)
- JS email rendering on about/contact to prevent Cloudflare mangling
- MailerLite universal script is on every HTML page (after GA script)
