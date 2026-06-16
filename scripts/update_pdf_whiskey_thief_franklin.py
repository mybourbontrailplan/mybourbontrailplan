#!/usr/bin/env python3
"""
One-off patch script for bourbon-trail-map.pdf.

There is no HTML/source file for this PDF, it was generated directly
(likely via a Python plotting/PDF library in an earlier session) and only
the binary survived. This script edits the existing PDF in place using
PyMuPDF rather than rebuilding it from scratch, so the original fonts,
colors, and layout are preserved exactly. All coordinates below were
read directly off the existing PDF's drawing/text objects.

Changes made:
  1. Page 1 (map): adds a new purple "Frankfort region" dot for the
     Whiskey Thief Franklin County farm distillery, near the existing
     Buffalo Trace / Castle & Key / Glenns Creek / J. Mattingly cluster.
  2. Page 2 (list):
     - Renames the Louisville "Whiskey Thief Distilling Co." row to
       "Whiskey Thief (Louisville Tasting Room)" / "Louisville (NuLu)"
       by painting over the old text with the row's own stripe color
       and inserting new text on top (not redaction, plain cover+draw,
       since redact annots rendered a visible artifact here).
     - Adds a 5th row to the Frankfort section for
       "Whiskey Thief (Franklin Co. Farm)" / "Frankfort", matching the
       existing checkbox + row pattern. Backfills the stripe rect the
       previous last row (J. Mattingly) never had (this layout only
       stripes non-last rows within a section) using overlay=False so
       it paints *behind* the existing row text instead of over it.

Run from repo root: python scripts\\update_pdf_whiskey_thief_franklin.py
"""

import os
import fitz

PDF = "bourbon-trail-map.pdf"

PRIMARY_DARK = (0x0E / 255, 0x2F / 255, 0x44 / 255)
TEXT = (0x1A / 255, 0x1A / 255, 0x2E / 255)
TEXT_SECONDARY = (0x5A / 255, 0x61 / 255, 0x78 / 255)
STRIPE = (0.9411759972572327, 0.9490200281143188, 0.9607840180397034)
PURPLE = (0.556863009929657, 0.2666670083999634, 0.67843097448349)
WHITE = (1, 1, 1)

ROW_H = 12.9
NAME_FONT, NAME_SIZE = "hebo", 6.75
LOC_FONT, LOC_SIZE = "helv", 6.375
LOC_RIGHT_EDGE = 295.502

doc = fitz.open(PDF)
page_map = doc[0]
page_list = doc[1]


def loc_origin(text, baseline_y):
    width = fitz.get_text_length(text, fontname=LOC_FONT, fontsize=LOC_SIZE)
    return (LOC_RIGHT_EDGE - width, baseline_y)


# 1. Map page: new Frankfort-region dot for the Whiskey Thief farm,
#    placed just southwest of the existing Frankfort cluster.
shape = page_map.new_shape()
shape.draw_circle(fitz.Point(352, 234), 2.54)
shape.finish(fill=PURPLE, color=WHITE, width=0.86, closePath=True)
shape.commit()

# 2a. List page: actually remove the old Louisville Whiskey Thief name +
#     location text (true redaction, not just a visual cover, so it can't
#     linger as hidden/selectable text), then paint the row's stripe
#     color back over the gap and draw the new text on top.
old_name_rect = fitz.Rect(45.0, 236.3, 182.0, 247.6)
old_loc_rect = fitz.Rect(245.0, 236.3, 297.0, 247.6)
page_list.add_redact_annot(old_name_rect)
page_list.add_redact_annot(old_loc_rect)
page_list.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

cover = page_list.new_shape()
cover.draw_rect(old_name_rect)
cover.draw_rect(old_loc_rect)
cover.finish(fill=STRIPE, color=None)
cover.commit()

page_list.insert_text((45.9, 244.7484), "Whiskey Thief (Louisville Tasting Room)",
                       fontsize=NAME_SIZE, fontname=NAME_FONT, color=TEXT)
page_list.insert_text(loc_origin("Louisville (NuLu)", 244.7414),
                       "Louisville (NuLu)", fontsize=LOC_SIZE, fontname=LOC_FONT,
                       color=TEXT_SECONDARY)

# 2b. List page: backfill the stripe the old last Frankfort row
#     (J. Mattingly) never had, since it's no longer the section's last
#     row. overlay=False so this paints behind the existing row text
#     instead of covering it.
backfill = page_list.new_shape()
backfill.draw_rect(fitz.Rect(32.400001525878906, 518.3250122070312, 297.0, 531.2250061035156))
backfill.finish(fill=STRIPE, color=None)
backfill.commit(overlay=False)

# 2c. List page: new 5th Frankfort row (Whiskey Thief Franklin farm),
#     one row-height below J. Mattingly, no stripe since it's now last.
newrow = page_list.new_shape()
cb = fitz.Rect(33.900001525878906, 521.2125244140625 + ROW_H,
               40.650001525878906, 527.9625244140625 + ROW_H)
newrow.draw_rect(cb, radius=0.15)
newrow.finish(fill=None, color=PRIMARY_DARK, width=0.9)
newrow.commit()

page_list.insert_text((45.9, 527.3484 + ROW_H), "Whiskey Thief (Franklin Co. Farm)",
                       fontsize=NAME_SIZE, fontname=NAME_FONT, color=TEXT)
page_list.insert_text(loc_origin("Frankfort", 527.3414 + ROW_H),
                       "Frankfort", fontsize=LOC_SIZE, fontname=LOC_FONT,
                       color=TEXT_SECONDARY)

doc.save("bourbon-trail-map.pdf.tmp")
doc.close()

os.replace("bourbon-trail-map.pdf.tmp", PDF)
print("Done. bourbon-trail-map.pdf updated in place.")
