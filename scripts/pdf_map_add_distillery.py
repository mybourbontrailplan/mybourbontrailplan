#!/usr/bin/env python3
"""
Adds a new distillery to bourbon-trail-map.pdf (both the map dot on page 1
and the checklist row on page 2), in place, preserving the existing PDF's
fonts/colors/layout. Written after manually reverse-engineering the PDF's
structure once (see git history of update_pdf_whiskey_thief_franklin.py
for that process); this script generalizes it so future additions don't
require redoing that archaeology.

Design notes:
  - The map dot is placed near the centroid of the region's *existing*
    dots, not from real lat/lng. The original map isn't a true geographic
    projection (a 7-point affine fit against real city coordinates had
    ~15-20pt residuals), so region-bucket placement is both simpler and
    more honest about the map's actual precision. This matches how the
    site already buckets every distillery into one of the same six
    regions for trip-builder.html / map.html / distilleries.html.
  - The list page's six sections are packed tightly against each other
    (no reserved slack), so adding a row to a section that ISN'T last in
    its column would collide with the next section's header. To handle
    that, this script shifts that header and everything below it (in the
    same column only) down by one row-height first. The shift works by
    capturing every vector drawing and text span in that region of the
    page (raw PDF drawing ops + text/font/color), redacting the area
    (which removes both the text and the underlying vector paths, not
    just the visible ink, confirmed empirically: redacted vector shapes
    don't linger as hidden content), then redrawing everything translated
    down. Re-inserted text uses PyMuPDF's built-in Helvetica/Times
    fonts rather than the original embedded TeX-Gyre-Heros/DejaVu-Serif,
    since those aren't easily reusable by name, visually indistinguishable
    at this size.
  - This list layout only draws a stripe rect behind non-last rows in a
    section (the original generator's quirk, not ours to fix). Adding a
    row means: backfill the stripe the previous last row never had, then
    add the new row with no stripe of its own.

Usage:
  python scripts\\pdf_map_add_distillery.py \\
      --name "Some Distillery" --location "Some City, KY" \\
      --region "Frankfort"

  --region must exactly match one of the six section headers:
  "Louisville", "Bardstown & New Hope", "Frankfort",
  "Lexington / Lawrenceburg", "Northern Kentucky", "Western Kentucky"
"""

import argparse
import math
import os
import fitz

PDF = "bourbon-trail-map.pdf"

PRIMARY_DARK = (0x0E / 255, 0x2F / 255, 0x44 / 255)
TEXT = (0x1A / 255, 0x1A / 255, 0x2E / 255)
TEXT_SECONDARY = (0x5A / 255, 0x61 / 255, 0x78 / 255)
STRIPE = (0.9411759972572327, 0.9490200281143188, 0.9607840180397034)
WHITE = (1, 1, 1)

DOT_RADIUS = 2.54
DOT_MIN_GAP = 1.5  # minimum clearance, in addition to both dots' radii

ROW_H = 12.9
HEADER_TO_ROW1_GAP = 20.84  # header bbox.y0 -> first row's checkbox.y0
CB_TO_NAME_BASELINE = 6.1359  # checkbox.y0 -> name text baseline y
HEADER_BASELINE_OFFSET = 9.155  # header bbox.y0 -> header text baseline y
CB_SIZE = 6.75
BULLET_SIZE = 7.5
HEADER_FONT, HEADER_SIZE = "tibo", 9.75
NAME_FONT, NAME_SIZE = "hebo", 6.75
LOC_FONT, LOC_SIZE = "helv", 6.375
Y_BOTTOM_SAFE = 700  # below all real list content, above the CTA banner (~708)

REGIONS = {
    "Louisville":               {"color": (0.160784, 0.501961, 0.725490), "column": "left"},
    "Bardstown & New Hope":      {"color": (0.831373, 0.627451, 0.235294), "column": "left"},
    "Frankfort":                 {"color": (0.556863, 0.266667, 0.678431), "column": "left"},
    "Lexington / Lawrenceburg":  {"color": (0.180392, 0.545098, 0.341176), "column": "right"},
    "Northern Kentucky":         {"color": (0.905882, 0.298039, 0.235294), "column": "right"},
    "Western Kentucky":          {"color": (0.901961, 0.494118, 0.133333), "column": "right"},
}

COLUMN_LAYOUT = {
    "left":  {"cb_x0": 33.900001525878906, "name_x0": 45.9, "loc_right": 295.502,
              "bullet_x0": 32.400001525878906, "stripe_x0": 32.400001525878906, "stripe_x1": 297.0},
    "right": {"cb_x0": 316.5, "name_x0": 328.5, "loc_right": 578.10,
              "bullet_x0": 315.0, "stripe_x0": 315.0, "stripe_x1": 579.6},
}

# Original embedded font -> nearest PyMuPDF built-in, used only when an
# element has to be redrawn after a shift (its text content is unchanged).
FONT_SUBSTITUTE = {
    "DejaVu-Serif-Bold": "tibo",
    "TeX-Gyre-Heros-Bold": "hebo",
    "TeX-Gyre-Heros": "helv",
}


def close(a, b, tol=0.6):
    return abs(a - b) < tol


def find_map_dots(page, color):
    """All small filled circles on the map matching a region's color,
    excluding the legend swatches (which sit at y > 400, well below the
    Kentucky outline)."""
    dots = []
    for d in page.get_drawings():
        r = d.get("rect")
        fill = d.get("fill")
        if not r or not fill or r.height > 250:
            continue
        if close(r.width, r.height, 1.0) and 4 < r.width < 7 and r.y1 < 400:
            if all(close(a, b, 0.02) for a, b in zip(fill, color)):
                dots.append(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2))
    return dots


def pick_dot_position(existing_dots):
    cx = sum(p[0] for p in existing_dots) / len(existing_dots)
    cy = sum(p[1] for p in existing_dots) / len(existing_dots)
    min_dist = 2 * DOT_RADIUS + DOT_MIN_GAP
    for radius in (0, 6, 9, 12, 16, 20, 26):
        steps = 1 if radius == 0 else 10
        for i in range(steps):
            angle = 2 * math.pi * i / steps
            cand = (cx + radius * math.cos(angle), cy + radius * math.sin(angle))
            if all(math.hypot(cand[0] - p[0], cand[1] - p[1]) >= min_dist for p in existing_dots):
                return cand
    return (cx, cy)  # fallback, shouldn't happen in practice


def find_all_headers(page):
    """(region_name, column, header_y0) for every section header, sorted
    top-to-bottom within each column."""
    found = []
    d = page.get_text("dict")
    for block in d["blocks"]:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                if "Serif-Bold" in span["font"] and span["size"] > 9 and span["text"] in REGIONS:
                    col = "left" if span["bbox"][0] < 300 else "right"
                    found.append((span["text"], col, span["bbox"][1]))
    return found


def find_section(page, region_name):
    """Returns (column, header_y0, next_header_y0_or_None) for a region's
    list section, located live by searching for its header text."""
    column = REGIONS[region_name]["column"]
    headers = [h for h in find_all_headers(page) if h[1] == column]
    headers.sort(key=lambda h: h[2])
    target_y0, next_y0 = None, None
    for i, (text, _col, y0) in enumerate(headers):
        if text == region_name:
            target_y0 = y0
            if i + 1 < len(headers):
                next_y0 = headers[i + 1][2]
            break
    if target_y0 is None:
        raise ValueError(f"Could not find section header for region {region_name!r}")
    return column, target_y0, next_y0


def count_existing_rows(page, column, header_y0, next_header_y0):
    layout = COLUMN_LAYOUT[column]
    row1_y0 = header_y0 + HEADER_TO_ROW1_GAP
    limit = next_header_y0 if next_header_y0 else 1e9
    count = 0
    for d in page.get_drawings():
        r = d.get("rect")
        if not r or not close(r.width, r.height, 0.5) or not (5 < r.width < 9):
            continue
        if not close(r.x0, layout["cb_x0"], 1.5):
            continue
        if r.y0 >= row1_y0 - 1 and r.y0 < limit:
            count += 1
    return count


def shift_column_below(page, column, y_threshold, dy):
    """Moves every vector drawing and text span in `column`, at or below
    `y_threshold`, down by `dy` points. Used to make room for a new row
    in a section that isn't the last one in its column."""
    layout = COLUMN_LAYOUT[column]
    x0, x1 = layout["stripe_x0"] - 1, layout["stripe_x1"] + 1
    region = fitz.Rect(x0, y_threshold, x1, Y_BOTTOM_SAFE)

    drawings_to_move = []
    for d in page.get_drawings():
        r = d.get("rect")
        if r and region.contains(r):
            drawings_to_move.append(d)

    spans_to_move = []
    text_dict = page.get_text("dict")
    for block in text_dict["blocks"]:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                ox, oy = span["origin"]
                if x0 <= ox <= x1 and y_threshold <= oy <= Y_BOTTOM_SAFE:
                    spans_to_move.append(span)

    if not drawings_to_move and not spans_to_move:
        return  # nothing below the threshold in this column

    page.add_redact_annot(region)
    page.apply_redactions()

    shape = page.new_shape()
    for d in drawings_to_move:
        for item in d["items"]:
            op = item[0]
            if op == "re":
                rect = item[1]
                shape.draw_rect(fitz.Rect(rect.x0, rect.y0 + dy, rect.x1, rect.y1 + dy))
            elif op == "l":
                p1, p2 = item[1], item[2]
                shape.draw_line(fitz.Point(p1.x, p1.y + dy), fitz.Point(p2.x, p2.y + dy))
            elif op == "c":
                p1, p2, p3, p4 = item[1], item[2], item[3], item[4]
                shape.draw_bezier(fitz.Point(p1.x, p1.y + dy), fitz.Point(p2.x, p2.y + dy),
                                   fitz.Point(p3.x, p3.y + dy), fitz.Point(p4.x, p4.y + dy))
        shape.finish(fill=d.get("fill"), color=d.get("color"), width=d.get("width"),
                     even_odd=d.get("even_odd", False), closePath=d.get("closePath", False))
    shape.commit()

    for span in spans_to_move:
        ox, oy = span["origin"]
        font = FONT_SUBSTITUTE.get(span["font"], "helv")
        color = tuple(int(c) / 255 for c in (
            (span["color"] >> 16) & 255, (span["color"] >> 8) & 255, span["color"] & 255))
        page.insert_text((ox, oy + dy), span["text"], fontsize=span["size"],
                          fontname=font, color=color)


def add_distillery_to_pdf(name, location, region, path=PDF):
    if region not in REGIONS:
        raise ValueError(f"region must be one of {list(REGIONS)}")
    doc = fitz.open(path)
    page_map, page_list = doc[0], doc[1]

    # 1. Map dot.
    existing_dots = find_map_dots(page_map, REGIONS[region]["color"])
    if not existing_dots:
        raise RuntimeError(f"No existing dots found for region {region!r}; "
                            "can't infer a placement.")
    x, y = pick_dot_position(existing_dots)
    shape = page_map.new_shape()
    shape.draw_circle(fitz.Point(x, y), DOT_RADIUS)
    shape.finish(fill=REGIONS[region]["color"], color=WHITE, width=0.86, closePath=True)
    shape.commit()

    # 2. List row.
    column, header_y0, next_header_y0 = find_section(page_list, region)
    layout = COLUMN_LAYOUT[column]
    row_count = count_existing_rows(page_list, column, header_y0, next_header_y0)
    row1_cb_y0 = header_y0 + HEADER_TO_ROW1_GAP

    if next_header_y0 is not None:
        # Not the last section in its column: make room by shifting the
        # next header (and everything below it, same column) down a row.
        shift_column_below(page_list, column, next_header_y0 - 1.0, ROW_H)

    if row_count > 0:
        last_cb_y0 = row1_cb_y0 + (row_count - 1) * ROW_H
        backfill = page_list.new_shape()
        backfill.draw_rect(fitz.Rect(layout["stripe_x0"], last_cb_y0,
                                      layout["stripe_x1"], last_cb_y0 + ROW_H))
        backfill.finish(fill=STRIPE, color=None)
        backfill.commit(overlay=False)

    new_cb_y0 = row1_cb_y0 + row_count * ROW_H
    cb = fitz.Rect(layout["cb_x0"], new_cb_y0, layout["cb_x0"] + CB_SIZE, new_cb_y0 + CB_SIZE)
    newrow = page_list.new_shape()
    newrow.draw_rect(cb, radius=0.15)
    newrow.finish(fill=None, color=PRIMARY_DARK, width=0.9)
    newrow.commit()

    name_baseline = new_cb_y0 + CB_TO_NAME_BASELINE
    page_list.insert_text((layout["name_x0"], name_baseline), name,
                           fontsize=NAME_SIZE, fontname=NAME_FONT, color=TEXT)
    loc_width = fitz.get_text_length(location, fontname=LOC_FONT, fontsize=LOC_SIZE)
    page_list.insert_text((layout["loc_right"] - loc_width, name_baseline - 0.007),
                           location, fontsize=LOC_SIZE, fontname=LOC_FONT,
                           color=TEXT_SECONDARY)

    tmp = path + ".tmp"
    doc.save(tmp)
    doc.close()
    os.replace(tmp, path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--name", required=True, help="Distillery name, e.g. 'Some Distillery'")
    ap.add_argument("--location", required=True, help="City label, e.g. 'Some City, KY'")
    ap.add_argument("--region", required=True, choices=list(REGIONS),
                     help="Must match a list-page section header exactly")
    args = ap.parse_args()
    add_distillery_to_pdf(args.name, args.location, args.region)
    print(f"Added {args.name!r} ({args.location}) to the {args.region} section.")
