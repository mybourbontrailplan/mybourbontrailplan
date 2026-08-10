# Implementation Internals

Deep detail for specific files. **You only need the section for the file you are touching.** `CLAUDE.md` covers the rules that apply everywhere; this is the reference you open when you are inside `trip-builder.html`, `map.html`, the PDF generator, or the icon system.

---

## trip-builder.html

### Architecture
- Distilleries render as Leaflet markers with region filters and smart pairing tips. The data lives in the `const D=[...]` array.
- **Distillery dots** are managed via `_addPin(id)` / `_removePin(id)`, which call `marker.addTo(map)` and `marker.removeFrom(map)`. A `_onMap` boolean prevents duplicate adds/removes. Click handlers survive DOM recreation because they are attached to the Leaflet marker object, not the DOM element. Trip stop dots (added to the trip) are always kept on the map: `_addPin` is called for them regardless of zoom.
- **Region overlay markers** are always on the map. When zoomed in (`show=true`) they are hidden by setting `opacity:0` and `pointer-events:none` on **both** the Leaflet icon wrapper (`m._icon`) **and** the inner `.region-overlay` child. Setting it on the wrapper alone is not sufficient, because CSS `pointer-events:auto` on the child overrides the parent's inline `none`. Regions where this matters: Louisville (Old Forester, Evan Williams, Buzzard's Roost), Bardstown (Chicken Cock), Frankfort (Buffalo Trace, Castle & Key), Lexington (Fresh Bourbon).

### Mobile layout
- Breakpoint 900px.
- Browse and Your Trip buttons live in a **fixed top action bar below the nav**, not floating bottom buttons.
- All mobile interactive elements use z-index 800+ to stay above Leaflet layers.

**Why bottom buttons were abandoned:** iPhone Safari's dynamic bottom toolbar height is not accounted for by `env(safe-area-inset-bottom)`. Multiple attempts with increased bottom values, dvh units and `@supports` fallbacks all failed on iPhone 16 Pro and 17 Pro simultaneously. The top action bar eliminates all bottom-edge issues permanently. Do not revisit.

### Mobile z-index stack (DO NOT violate this order)
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

### Map label behaviour
- Labels are hidden by default (`display:none`) and shown via the `#map.show-labels` class.
- The label threshold is **filter-aware**: `Math.min(10, RD[aRF].zoom)` when a region is active, 12 when "All". So Western at zoom 8 shows labels, Northern at zoom 10 shows labels, "All" requires zoom 12.
- Desktop hover shows a label on mouseover at any zoom, inside `@media (hover:hover)` so it does not fire on touch.
- `filterRegion()` calls `handleZoom()` at the end so labels update immediately when the filter changes.

### handleZoom() vs updateZoomUI() — important split
- **`updateZoomUI()`** fires **immediately** on every `zoomend` and `moveend`. Updates back-button visibility, region overlay opacity and pointer-events, and the `show-labels` class. No debounce, so UI never lags behind map movement.
- **`handleZoom()`** is debounced 200ms after each `zoomend`/`moveend`. It calls `updateZoomUI()` first, then runs the expensive `_addPin`/`_removePin` loop over every distillery. The debounce prevents thrashing during fast zooming.
- `filterRegion()` calls `handleZoom()` directly (not debounced) so dots and labels update immediately on region selection.

### handleZoom() thresholds (all filter-aware)
- **Dot threshold** (`showThr`): `Math.min(10, RD[aRF].zoom)` when filtered, `10` when "All". Dots appear at the region's flyTo zoom.
- **Label threshold** (`labelZoom`): same formula, so labels and dots appear together.
- **Back button** ("← All Regions"): shows at `z >= showThr`, visible as soon as dots appear.
- **Region overlay buttons**: hidden when `show=true`, visible when `show=false`.

### RG city-to-region mapping
- `Newport:'Northern'` — New Riff and Pensive are both in Newport and appear under the Northern filter.
- Most other Northern KY cities (Independence, Ludlow, Sparta, Maysville, Burlington, Augusta) also map to `Northern`.
- `Paris:'Lexington'` — Paris is 17 mi from the Lexington distilleries, a natural Lexington-day add-on, and closer to Lexington than to the Northern KY cluster.
- `Danville:'Lexington'`, `Lawrenceburg:'Lexington'` — these sit in the Lexington/Lawrenceburg corridor.
- `Shelbyville:'Louisville'`, `Crestwood:'Louisville'` — I-64/I-71 corridor, grouped with Louisville per the PDF map regions.
- `Lebanon:'Bardstown'`, `Radcliff:'Bardstown'` — grouped with Bardstown per the PDF map regions.

### Region data (RD) — flyTo destinations
- `Louisville`, `Bardstown`, `Frankfort`: zoom 14
- `Lexington`: zoom 11
- `Northern`: zoom 10
- **`Western`: lat 37.13, lng -87.59, zoom 8.** It spans more than 2 degrees of longitude; zoom 10 is too close for mobile to see the whole region. The centre is the midpoint of the extremes, not the geographic mean, for best viewport fit.
- The `Central` region was removed. All formerly-Central distilleries (Bulleit, Jeptha Creed, Kentucky Artisan, Larrikin) are now Louisville or Lexington per the PDF regions.

### Western button mobile repositioning
- On desktop the Western button marker sits at the `RD` flyTo centre (-87.59), visible in a wide viewport.
- On mobile (<900px) the initial overview spans only ~2 degrees of longitude, so that centre is off-screen to the left.
- **Fix:** on mobile the Western button marker is placed at lat 37.3, lng -86.2 with `iconAnchor [0,28]` (left-aligned), so the button sits near the left edge and extends rightward into view.
- Clicking still `flyTo`s `RD.Western` (37.13, -87.59, zoom 8). Marker position and flyTo destination are deliberately separate.
- Detection: `const isMobile = window.innerWidth < 900` at map init.

### Mobile back button ("← All Regions")
- `position:absolute; top:24px; left:54px`. `top:24px` clears the fixed action bar; `left:54px` clears the Leaflet zoom controls (~36px wide at the left edge). A previous `left:12px` put it directly behind the zoom control.
- `z-index:600` keeps it below the action bar (800); the extra `top` clearance keeps it visually below rather than z-fighting.

### Trip state persistence (localStorage)
- Key `btp-plan`, storing `{trip, tDays, aDay}` as JSON.
- `saveState()` is called by every mutator: add stop, remove stop, drag reorder, clear, switch day, change day count.
- `loadState()` returns `true` if valid saved data was found and applied.
- Both use a try/catch wrapper matching the existing `btp-seen` pattern. localStorage failure (private mode, quota) is always silent.
- On restore, `fitBounds()` zooms to fit all trip markers with `{padding:[60,60], maxZoom:13, animate:false}`; a single stop uses `setView` at zoom 13. This is required because the back button only appears at the region zoom threshold, so restoring at the default overview zoom would hide it.
- `rebuildDayTabs()` handles 4-day restored plans: it removes tabs above 3, then recreates up to `tDays`. It uses IIFE closures in `onclick` to capture the day number correctly.

### Shareable trip URL (`?plan=`)
- Encoding: slugs comma-joined per day, days semicolon-separated, e.g. `day1a,day1b;day2a;day3a,day3b`.
- `getShareURL()` builds the full URL; `getPlanString()` produces just the encoded plan.
- `importPlan(str)` decodes and populates `trip[]`. Unknown slugs are silently skipped, which keeps old links forward-compatible.
- After import, `history.replaceState` strips `?plan=` so later edits do not re-import the original on refresh.
- The plan is saved to localStorage immediately after import so it survives a refresh.
- `rebuildDayTabs()` is called after import to support shared 4-day plans.
- GA4 `plan_loaded_from_link` fires on import, with stop count.

### Copy Trip Link button
- Element `.share-btn#shareBtn` in the sidebar footer, between the email button and the clear button.
- Disabled alongside `#exportBtn` when no stops are added; `updateStats()` drives both.
- `copyShareLink()` tries `navigator.clipboard.writeText()` first and falls back to `fallbackCopy()` (textarea select/exec).
- On success it shows a non-blocking fixed toast (`#shareToast`, z-index 1900) with a 5s auto-dismiss and an inline link to open the email modal.
- GA4 `share_link_copied` fires on copy, with stop count.

### Drag-to-reorder stops
- SortableJS 1.15.6 loads from unpkg **after** the Leaflet script tag.
- Drag handle is a `.drag-handle` div at the start of each `.stop-card` (six-dot SVG).
- `Sortable.create(area, {...})` runs at the end of `renderStops()` after `innerHTML` is set. If a Sortable already exists on the element (`area._sortable`) it is destroyed first to prevent double-init.
- `delay:150` plus `delayOnTouchOnly:true` stops drag firing during normal scroll on touch, while desktop drag starts immediately.
- `onEnd` reads the DOM order of `.stop-card[data-id]`, rebuilds `trip[aDay]` from it, then calls `refreshIcons(); renderStops(); drawRoutes(); updateStats(); saveState()`.
- **Do NOT** use `delayOnTouchOnly:false` or remove `delay` — the handle then intercepts vertical scroll on mobile.

---

## map.html

- Height is `calc(100vh - 120px)` so content below is visible on scroll.
- The PDF map CTA card opens a modal. There is no `#pdf-signup` inline section; it was removed.
- Features: distillery search box in the sidebar (dropdown autocomplete, fly-to on click), collapsible region legend on mobile (collapsed by default), Kentucky state border via `L.geoJSON()` fetched from the PublicaMundi US states GeoJSON (fails silently if unavailable), pin labels visible at zoom 9+.
- Filter toggling uses `marker.addTo(map)` / `map.removeLayer()`. (Trip builder uses `marker.addTo(map)` / `marker.removeFrom(map)` via `_addPin()`/`_removePin()`, not `setOpacity`.)
- **`applyFilter()` sets the sidebar count and must run once at init.** It used to be wired only to filter-button clicks, so the sidebar read "Showing 0 distilleries" on load until you touched a region button. Fixed August 2026.
- **Pin labels use `direction:'auto'`, not `'right'`.** Leaflet flips the label to the left of pins in the right half of the map, which stops long names being sliced mid-word at the container edge. Changed August 2026 while fixing the embed at phone widths; it improves the full map too.
- **Container-size re-frame.** An iframed map often initialises before the browser has given the iframe its final dimensions, and `loading="lazy"` makes that the normal case. Leaflet then runs `fitBounds` against a zero-size container and ignores `?region=`. A ResizeObserver re-measures and re-applies the intended view during a **3-second settle window** after load; after that, resizes only re-measure and never move the visitor's view. `dragstart` cuts the window short because it is the one dependable user-intent signal (unlike `zoomstart`, which programmatic `fitBounds` also fires). **Do not replace the time window with a "has the user touched anything" guard** — a visitor scrolling the host page past the widget trips pointer and wheel events without meaning to interact, which cancels the correction and leaves them on a world map. That was the first attempt and it failed.

### URL deep-link support (`applyDeepLink()`, end of script)
- `?region=` fits bounds to the region and activates the filter button. Values: `louisville`, `bardstown`, `frankfort`, `lexington`, `other`. `northern`, `central` and `western` all normalise to `other`.
- `?distillery=` flies to the marker at zoom 14 and opens its popup. The slug matches the `distillery-{slug}.html` filename.
- Both together apply the region filter then highlight the distillery, falling back to distillery-only if that distillery is not in the region.

### Embed mode (`?embed=1`)
See the "Embeddable map widget" section in `CLAUDE.md` for the rules. Implementation detail:
- The flag is set by an inline script in `<head>` **before anything else**, so CSS can branch on `html.embed-mode` before first paint and nothing flashes.
- MailerLite is not loaded at all in embed mode.
- GA runs in **Consent Mode with `analytics_storage: 'denied'`** so the widget writes no cookies and no storage on a partner's guests. `client_storage:'none'` was tried first and GA recreated `_ga_*` regardless.
- Links are forced to open in a new tab via a **delegated** click handler, so it also catches Leaflet popup links built later.
- `embed_load` fires with `embed_host` (from `location.ancestorOrigins` first, `document.referrer` second), `embed_region` and `framed`.
- Below 800px the control stack is tightened (padding, no filter label, single-line CTA) so the map keeps roughly two thirds of a phone-width frame instead of half.

---

## Brand icon system

Shared two-tone SVGs (dark `#0E2F44` + gold `#D4A03C`, 64x64 viewBox) live in **`images/icons/`**. Reference them as `<img src="images/icons/icon-{name}.svg" alt="" width="N" height="N" loading="lazy">`. `alt=""` because they are always decorative next to a text label.

- **The folder is lowercase `icons`, not `Icons`.** Windows serves either; Netlify is case-sensitive and will 404 the wrong casing in production. It shipped as `Icons/` once and was renamed.
- **Available icons:** `route`, `barrel`, `calendar`, `car`, `cost`, `eat-stay`, `lightbulb`, `city`, `hotel`, `house`, `star`, `badge`, `building`, `clock`, `park`, `pin`, `trophy`. (Run `ls images/icons/` for the live list rather than trusting a count here.)
- **Meaning is fixed, never merge these two:** `badge` (shield+check) = official-trail / trail designation. `trophy` = awards and honours. A distillery being *on the trail* is `badge`; a distillery *winning an award* is `trophy`.
- **No icon exists for:** `shuttle` (transportation uses `car`), `horse`, warning, check-mark, or the one-off distillery flavour glyphs (corn, fire, ship, flags, crossed swords, music, family). Do not force a near-miss: stopwatch→calendar and pin→route both destroy the distinction.

### Chip style (the standard container)
Icons sit centred in a "chip": background `#F6F0E4`, border-radius about 20% of chip size, icon about 60% of chip width.
- Homepage `.feature-icon`: 56px chip, 11px radius, 34px icon.
- Where-to-stay `.lodging-icon`: 64px chip, 13px radius, 38px icon.

Keep those proportions when adding a chip elsewhere. Do not reintroduce per-card background tints; the old `.feature-icon.gold` alternating variant was removed and every chip is `#F6F0E4`.

**Small inline chip (entity listing cards):** where-to-stay `.type-chip` is a 28px chip / 8px radius / 17px icon, inline to the **left of the eyebrow label** inside `.lodging-type` (a flex row, gap 8px). These cards have **no hero panel** — the body starts at the eyebrow row. The navy gradient panel is reserved for guide cards; entity listing cards (lodging, and restaurant cards on eat-and-drink) never get one.

**Inline badge/pill icons:** inside a pill (`.badge`, `.lodging-tag`, `.rc-tag`, `.tour-card-rec`) the icon is a bare 16px `<img>` with `style="vertical-align:-3px;margin-right:4px"`. No chip, no wrapper, no per-page CSS. Mapping: award/honour pill → `trophy`; top-pick pill → `star`; official-trail/craft/independent pill → `badge`.

### Region banner (where-to-stay `.region-header`)
Navy panel (`--primary-dark`), **no icon chip** — the text block sits at the left padding. Under each city-name `<h3>` sits a gold inline-SVG "trail underline": a gentle dashed arc (`stroke-dasharray="9 8"`) with a filled dot at each end, styled `.trail-underline { display:block; margin-top:2px; max-width:100%; height:auto; }` so it scales down on mobile. The descriptor `<p>` follows at `margin-top:12px`.

eat-and-drink's `.region-header` is a **different component** (a bordered underline header with a coloured `.region-dot`) and was deliberately left alone.

- **The SVG's `width`, `viewBox`, path and circle coordinates are per-banner and hard-coded** to that heading's rendered text width. `W` = the heading's rendered **glyph** width **plus 4**. The path is `M5,10 Q {W/2},3 {W-5},8` and the right dot is at `cx={W-5}`; SVG attributes cannot do maths, so the numbers are pre-computed. Current values: Louisville `W=110`, Bardstown & New Hope `W=266`, Frankfort `W=112`, Lexington `W=114`.
- **Measure the glyph run, not the `<h3>` box.** The element box is wider than the letters and makes the arc overrun. Select the h3's text node and read `Range.getBoundingClientRect().width` at desktop (22px Fraunces 700): `const r=document.createRange(); r.selectNodeContents(h3.firstChild); r.getBoundingClientRect().width`. Then `W = round(width) + 4`. The `+4` puts the end dot just under the last letter's right edge, mirroring the left dot under the first letter.
- **If a banner heading's text changes, re-measure that heading and regenerate its SVG values** (`width`, `viewBox`, the `Q` control/end points, the end-dot `cx`). A stale width makes the arc under- or over-run. Only the changed heading needs re-measuring.

### Homepage guide card headers (`.guide-img`)
Background is `linear-gradient(135deg, #0E2F44, #1B4761)` for **all** cards; the old per-card blue/gold/teal inline gradients are gone. Each header contains, in order:
1. `.guide-img-eyebrow` — the category, gold `var(--accent)`, uppercase, `letter-spacing:1.2px`. This replaced the old body-level `.guide-category` div; the category lives in the header now.
2. `.guide-img-ghost` — a large category icon, right-aligned, `opacity:0.3`, **inlined SVG with all strokes recoloured to `#D4A03C`**. The file versions are dark-on-light and vanish against the navy, so they cannot be used via `<img>` here.
3. `.guide-img-trail` — a gold dashed trail curve across the bottom, with `vector-effect="non-scaling-stroke"` so stretching to card width does not distort the stroke.

The old `.guide-img-label` (the ghosted "3D"/"BT"/"$$" two-character mark) is gone. Do not re-add it.

---

## PDF map generator (`scripts/generate_pdf_map.py`)

`bourbon-trail-map.pdf` is linked from the homepage and `map.html`. The script lays out both pages from scratch on every run.

**The source of truth is the live site.** The script reads the `const D=[...]` array in `trip-builder.html` (name, lat, lng, region, type, cost, booking) and the cards in `distilleries.html` (city, Official Trail vs Craft tag), joins them on the profile filename, and assigns map numbers. There is no separate data file to maintain. `scripts/pdf_map_data.json` is written by the script as a readable snapshot of what it derived, for inspection only, never an input.

Page 1 is a landscape hero map: statewide outline, region-coloured numbered pins, a zoomed Central Corridor inset, region legend, QR to the trip builder. Page 2 is a landscape four-column reference list grouped by region (number, city, Trail/Craft, booking difficulty, tour cost) plus a drive-times table, a booking-ease index and a second QR.

Assets are in `scripts/assets/`: Kentucky outline GeoJSON, DM Sans and Fraunces TTFs.

`scripts/pdf_map_add_distillery.py` is an obsolete in-place editor. Do not use it.

### Editing the PDF map
- **Add or edit a distillery:** make the normal site edits, then run `python scripts/generate_pdf_map.py`. It flows in automatically once the distillery is in `trip-builder.html` and `distilleries.html`.
- **Change a drive time, the booking-ease descriptions, or the QR target:** edit the `drives` list, the `gloss` list, or `TRIP_BUILDER_URL` near the top of `build_page2` / the script header.
- **Change brand colours, region colours, or fonts:** the palette and `REGION_COLORS` dict are at the top of the script; fonts are in `scripts/assets/fonts/`.
- **Header logo:** both pages embed the raster brand lockup `images/nav-2x.png` via the `logo()` function (`LOGO_PNG` / `_LOGO_AR`). If the brand art changes, re-export `nav-2x.png` as a wide transparent PNG and re-run. No code change is needed unless the aspect ratio changes.
- **Move a town to a different region:** two dicts near the top control this and both feed the pin colour and the page-2 list section. Use `_CITY_REGION` for legacy `Central`/`Other` towns (Shelbyville's Bulleit and Jeptha Creed map to Louisville, the I-64 corridor, rather than Lexington/Lawrenceburg). Use `_REGION_OVERRIDE` when the site tags a real region that is geographically misleading for planning (Paris is tagged Northern KY but sits about 17 mi from the Lexington distilleries, so it is overridden to Lexington/Lawrenceburg). Geographic outliers that sit apart from their region's other pins (Shelbyville, Danville, Paris) get a small town label in the inset; that list is in `build_page1`.
- **Page orientation:** both pages are US Letter landscape. Page sizes are set at the top of `build_page1` and `build_page2` (`W,H = 792,612`).

**[STALE] The booking-ease glossary in the script does not match CLAUDE.md.** The `gloss` list still reads "Easy: Walk-up or same-week reservation" and "Moderate: Book 1 to 3 weeks ahead", which is the wording CLAUDE.md replaced in August 2026 (see the booking tier definitions there). It will ship wrong on the next PDF regeneration. Fix the `gloss` list when you next touch the generator.

---

## Emoji-to-icon migration status

A migration from emoji UI icons to the brand icon system, partially complete. This is a status log, not a rule: the rule is simply "use the icon system for UI icons where an icon exists".

**Done:** homepage feature cards and guide card headers; where-to-stay lodging cards (hero slots removed, 28px inline `.type-chip` at the eyebrow); where-to-stay region banners (icon chip removed, trail-underline city name); where-to-stay's two lightbulb callouts; the **site-wide badge-pill sweep** (official/craft/independent `badge-trail` pills → `icon-badge`, `badge-landmark` award pills → `icon-trophy`, `tour-card-rec rec-top` and `rc-tag tag-must` top-pick pills → `icon-star`, all inline 16px `<img>`); and the **distillery snapshot and tour-meta pass** across every profile.

**Snapshot and tour-meta detail:**
- `.snap-icon` (the four centred snapshot-card icons): calendar→`icon-calendar` (Book Ahead), stopwatch→`icon-clock` (Tour Length), trophy→`icon-trophy` (Our Rating), pin→`icon-pin` (Region). Rendered as a **bare 26px `<img>`** with `style="display:block;margin:0 auto"`; the card is `text-align:center` and there is no chip, matching the bare emoji it replaced.
- `.tour-meta-item` (the inline meta row): money→`icon-cost`, stopwatch→`icon-clock`, calendar→`icon-calendar`, as a **bare 16px `<img>`**. The row is `display:flex;align-items:center;gap:5px`, which handles spacing, so no vertical-align hack is needed.
- **Glyphs with no matching icon were stripped to text, not left as emoji**, because a raw emoji beside line-art SVGs in the same row looks broken. That covered the group-size busts ("Small groups", "Up to 10 people") and Dark Arts's one-off flavour glyphs. The text label alone carries the meaning.

**Deliberately left as emoji:**
- The one-off `badge-trail` **flavour** glyphs, one per distillery (horse, corn, crossed swords, ship, fire, palette, bridge, family, flags). No counterpart exists in a trip-planning icon set and mapping them would destroy the meaning.
- Callout and status glyphs with no mapped icon: the warning `⚠` in `.warning-box` headers, check marks `✓` in booking checklists, and assorted inline content emoji in guide body copy (thermometer, fork-and-knife, bottle).
- Lightbulb `💡` callouts on pages **other than** where-to-stay, same `.tip-box-header` pattern. Trivially convertible in a follow-up, just outside the named scope of that pass.

**Finding emoji is harder than it looks.** See the entity-encoding gotcha in `CLAUDE.md`.
