# CLAUDE.md updates for the rebuilt PDF map

The printable map is no longer edited in place. It is generated from the live
site data by `scripts/generate_pdf_map.py`. Two spots in CLAUDE.md reference the
old fragile workflow and should be replaced.

---

## 1. Replace the `bourbon-trail-map.pdf` file description (around line 111)

**Old text:**

> `bourbon-trail-map.pdf` - Printable/downloadable bourbon trail map; linked from homepage and map.html. There is no HTML/source file for this PDF, it's edited directly in place with PyMuPDF. Use `scripts/pdf_map_add_distillery.py` to add a new distillery (map dot + checklist row) - see that script's docstring for how it works, including the row-shifting it does when a section isn't the last one in its column.

**New text:**

> `bourbon-trail-map.pdf` - Printable/downloadable bourbon trail map; linked from homepage and map.html. Generated from data by `scripts/generate_pdf_map.py`, which lays out both pages from scratch on every run. The source of truth is the live site itself: the script reads the `const D=[...]` array in `trip-builder.html` (name, lat, lng, region, type, cost, booking) and the cards in `distilleries.html` (city, Official Trail vs Craft tag), joins them on the profile filename, and assigns map numbers. Page 1 is a landscape hero map (statewide outline, region-colored numbered pins, a zoomed Central Corridor inset, region legend, QR to the Trip Builder). Page 2 is a landscape four-column reference list grouped by region (number, city, Trail/Craft, booking difficulty, tour cost) plus a drive-times table, a booking-ease index, and a second QR. There is no separate data file to maintain; `scripts/pdf_map_data.json` is written by the script as a readable snapshot of what it derived, for inspection only (not an input). Assets live in `scripts/assets/` (Kentucky outline GeoJSON, DM Sans + Fraunces TTFs). The old `scripts/pdf_map_add_distillery.py` in-place editor is obsolete and should not be used.

---

## 2. Replace step 8 of the add-a-distillery workflow (around line 264)

**Old text:**

> 8. Add it to `bourbon-trail-map.pdf` too: `python scripts\pdf_map_add_distillery.py --name "..." --location "City, KY" --region "..."` (region must exactly match one of the six section headers, e.g. `"Frankfort"`, `"Bardstown & New Hope"`)

**New text:**

> 8. Regenerate the printable map: `python scripts\generate_pdf_map.py`. No map-specific arguments are needed. Because the generator reads `trip-builder.html` and `distilleries.html`, the new distillery flows in automatically once steps above have added it to those two files (pins renumber, the checklist reflows, the region counts update). Commit the regenerated `bourbon-trail-map.pdf` with the rest of the deploy. Note: the trip-builder `region` value can be one of the legacy buckets (`Central`, `Other`); the generator remaps those to the six display regions by city. If you ever add a distillery in a brand-new city that maps to `Central`/`Other`, the script prints a one-line warning telling you to add a `_CITY_REGION` entry near the top of `generate_pdf_map.py`.

---

## Quick reference: editing the map later

- **Add or edit a distillery:** make the normal site edits (`trip-builder.html`, `distilleries.html`, etc.), then run `python scripts/generate_pdf_map.py`.
- **Change a drive time, the booking-ease descriptions, or the QR target:** edit the `drives` list, the `gloss` list, or `TRIP_BUILDER_URL` near the top of `build_page2` / the script header.
- **Change brand colors, region colors, or fonts:** the palette and `REGION_COLORS` dict are at the top of the script; fonts are in `scripts/assets/fonts/`.
- **Move a town to a different region:** two dicts near the top of the script control this, and both feed the map pin color and the page-2 list section. Use `_CITY_REGION` for legacy `Central`/`Other` towns (e.g. Shelbyville's Bulleit + Jeptha Creed are mapped to Louisville, the I-64 corridor, rather than Lexington/Lawrenceburg). Use `_REGION_OVERRIDE` when the site already tags a real region but it is geographically misleading for planning (e.g. Paris is tagged Northern KY on the site but sits ~17 mi from the Lexington distilleries, so it is overridden to Lexington/Lawrenceburg). Geographic outliers that sit apart from their region's other pins (Shelbyville, Danville, Paris) get a small town label in the inset so they read clearly; that list is in `build_page1`.
- **Page orientation:** both pages are currently US Letter landscape. Page sizes are set at the top of `build_page1` and `build_page2` (`W,H = 792,612`) if you ever want page 2 back in portrait.
