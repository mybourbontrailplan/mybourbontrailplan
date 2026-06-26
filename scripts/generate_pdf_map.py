#!/usr/bin/env python3
"""
generate_pdf_map.py  -  Builds bourbon-trail-map.pdf from scratch, data-driven.

Source of truth:  scripts/pdf_map_data.json   (one object per distillery)
Assets:           scripts/assets/ky_outline.json, scripts/assets/fonts/*.ttf

To add / edit a distillery: edit pdf_map_data.json and re-run this script.
Pins auto-number, the checklist auto-flows, the QR + drive table are static.

    python scripts/generate_pdf_map.py

Output: bourbon-trail-map.pdf at repo root.
"""
import os, json, math, io, re
import fitz  # PyMuPDF
import qrcode

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(HERE, "assets")
# Single source of truth = the live site data. The generator derives every
# distillery from these two files, so adding one to the site flows straight
# into the PDF on the next run. Override the dir with BOURBON_SITE_DIR for testing.
SITE_DIR = os.environ.get("BOURBON_SITE_DIR", ROOT)
TRIP_BUILDER = os.path.join(SITE_DIR, "trip-builder.html")
DISTILLERIES = os.path.join(SITE_DIR, "distilleries.html")
SNAPSHOT = os.path.join(HERE, "pdf_map_data.json")   # written for inspection
OUT = os.path.join(ROOT, "bourbon-trail-map.pdf")

REGION_ORDER = ["Louisville","Bardstown & New Hope","Frankfort",
                "Lexington / Lawrenceburg","Northern KY","Western KY"]
TRIP_BUILDER_URL = ("https://mybourbontrailplan.com/trip-builder"
                    "?utm_source=pdf_map&utm_medium=qr&utm_campaign=printable_map")

# ---------- brand ----------
INK      = (0x0E/255, 0x2F/255, 0x44/255)   # dark navy  #0E2F44
PRIMARY  = (0x1B/255, 0x4F/255, 0x72/255)   # primary    #1B4F72
GOLD     = (0xD4/255, 0xA0/255, 0x3C/255)   # accent     #D4A03C
MUTED    = (0x5B/255, 0x6B/255, 0x77/255)
HAIR     = (0xD9/255, 0xDF/255, 0xE4/255)
PAPER    = (0xF7/255, 0xF9/255, 0xFA/255)
LANDFILL = (0xEE/255, 0xF2/255, 0xF5/255)
WHITE    = (1, 1, 1)

REGION_COLORS = {
    "Louisville":               (0x1B/255, 0x4F/255, 0x72/255),
    "Bardstown & New Hope":     (0xBC/255, 0x83/255, 0x2B/255),
    "Frankfort":                (0x7D/255, 0x3C/255, 0x98/255),
    "Lexington / Lawrenceburg": (0x1E/255, 0x84/255, 0x49/255),
    "Northern KY":              (0xC0/255, 0x39/255, 0x2B/255),
    "Western KY":               (0xC9/255, 0x63/255, 0x1E/255),
}
BOOK_COLORS = {"Easy": (0x1E/255,0x84/255,0x49/255),
               "Moderate": (0xD4/255,0xA0/255,0x3C/255),
               "Hard": (0xC0/255,0x39/255,0x2B/255)}

FONTS = {
    "fr-black":  os.path.join(ASSETS, "fonts", "Fraunces-Black.ttf"),
    "fr-bold":   os.path.join(ASSETS, "fonts", "Fraunces-Bold.ttf"),
    "fr-semi":   os.path.join(ASSETS, "fonts", "Fraunces-SemiBold.ttf"),
    "dm":        os.path.join(ASSETS, "fonts", "DMSans-Regular.ttf"),
    "dm-med":    os.path.join(ASSETS, "fonts", "DMSans-Medium.ttf"),
    "dm-bold":   os.path.join(ASSETS, "fonts", "DMSans-Bold.ttf"),
}

_FONTOBJ = {k: fitz.Font(fontfile=v) for k, v in FONTS.items()}

# ---------- data: derived from the live site files ----------
# trip-builder.html holds the canonical `const D=[...]` array (name, lat, lng,
# region, type, cost, booking, profile). distilleries.html supplies the city
# and the Trail/Craft tag. We join on the profile filename.
_DISPLAY = {"Louisville":"Louisville","Bardstown":"Bardstown & New Hope",
            "Frankfort":"Frankfort","Lexington":"Lexington / Lawrenceburg",
            "Northern":"Northern KY","Western":"Western KY"}
# legacy "Central"/"Other" regions resolve to a display region by city
_CITY_REGION = {"Shelbyville":"Louisville","Crestwood":"Louisville",
                "Lawrenceburg":"Lexington / Lawrenceburg","Danville":"Lexington / Lawrenceburg",
                "Lebanon":"Bardstown & New Hope","Radcliff":"Bardstown & New Hope"}
# override the site's region for towns where its grouping is geographically
# misleading for a trip planner. Paris is tagged Northern KY on the site but
# sits ~17 mi from the Lexington distilleries, a natural Lexington-day add-on.
_REGION_OVERRIDE = {"Paris":"Lexington / Lawrenceburg"}
# distilleries that are official KBT members but lack the tag in the cards markup
_TRAIL_FIX = {"stitzel-weller":"Trail"}

def _js_array(html, varname):
    i = html.find(f"const {varname}=[")
    if i < 0: i = html.find(f"const {varname} =[")
    if i < 0: i = html.find(f"{varname}=[")
    a = html.find("[", i)
    depth=0
    for k in range(a, len(html)):
        if html[k]=="[": depth+=1
        elif html[k]=="]":
            depth-=1
            if depth==0:
                raw=html[a:k+1]; break
    js=re.sub(r'([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:', r'\1"\2":', raw)
    return json.loads(js)

def _cards(html):
    out={}
    for href,body in re.findall(r'<a href="(distillery-[^"]+\.html)" class="dist-card"[^>]*>(.*?)</a>', html, re.S):
        loc=re.search(r'dist-card-region">([^<]+)<', body)
        meta=re.findall(r'<span[^>]*>([^<]+)</span>', body)
        trail=None
        for m in meta:
            if m.strip()=="Official Trail": trail="Trail"
            elif m.strip()=="Craft": trail="Craft"
        city=loc.group(1).split(",")[0].strip() if loc else None
        out[href]={"city":city,"trail":trail}
    return out

def load():
    tb=open(TRIP_BUILDER, encoding="utf-8", errors="replace").read()
    ds=open(DISTILLERIES, encoding="utf-8", errors="replace").read()
    D=_js_array(tb, "D")
    cards=_cards(ds)
    recs=[]
    for d in D:
        card=cards.get(d.get("profile"), {})
        city=card.get("city") or d["region"]
        if city in _REGION_OVERRIDE:
            region=_REGION_OVERRIDE[city]
        elif d["region"] in _DISPLAY:
            region=_DISPLAY[d["region"]]
        else:
            region=_CITY_REGION.get(city)
            if not region:
                region="Lexington / Lawrenceburg"
                print(f"  [warn] {d['name']} has region '{d['region']}' / city '{city}' "
                      f"with no mapping; defaulting to {region}. Add a _CITY_REGION entry.")
        trail=_TRAIL_FIX.get(d["id"]) or card.get("trail") or "Craft"
        recs.append({"id":d["id"],"name":d["name"],"city":city,"region":region,
                     "lat":d["lat"],"lng":d["lng"],"trail":trail,
                     "booking":d.get("booking"),"cost":(d.get("cost") or "").strip()})
    recs.sort(key=lambda r:(REGION_ORDER.index(r["region"]), r["name"].lower()))
    for i,r in enumerate(recs,1): r["num"]=i
    data={"meta":{"trip_builder_url":TRIP_BUILDER_URL,"region_order":REGION_ORDER},
          "distilleries":recs}
    try:
        json.dump(data, open(SNAPSHOT,"w"), indent=2, ensure_ascii=False)
    except Exception:
        pass
    ky = json.load(open(os.path.join(ASSETS, "ky_outline.json")))
    return data, ky

def reg_font(page):
    for name, path in FONTS.items():
        page.insert_font(fontname=name, fontfile=path)

def rrect(page, rect, rad_pt, color=None, fill=None, width=1.0):
    frac = min(0.5, rad_pt / min(rect.width, rect.height))
    page.draw_rect(rect, color=color, fill=fill, width=width, radius=frac)

# ---------- text helpers ----------
def _tl(page, s, font, size):
    return _FONTOBJ[font].text_length(s, fontsize=size)

def text(page, x, y, s, font="dm", size=10, color=INK, align="left", tracking=0):
    """Draw a single baseline string. align: left|center|right (x is anchor)."""
    s = str(s)
    if tracking == 0:
        w = _tl(page, s, font, size)
        tx = x - (w/2 if align=="center" else w if align=="right" else 0)
        page.insert_text((tx, y), s, fontname=font, fontsize=size, color=color)
    else:
        widths = [_tl(page, ch, font, size) for ch in s]
        total = sum(widths) + tracking*(len(s)-1)
        tx = x - (total/2 if align=="center" else total if align=="right" else 0)
        for ch, wch in zip(s, widths):
            page.insert_text((tx, y), ch, fontname=font, fontsize=size, color=color)
            tx += wch + tracking

# ---------- projection ----------
class Proj:
    def __init__(self, lat0, lat1, lng0, lng1, box):
        self.latm = math.radians((lat0+lat1)/2)
        self.k = math.cos(self.latm)
        x0 = lng0*self.k; x1 = lng1*self.k
        self.lng0, self.lng1 = lng0, lng1
        self.lat0, self.lat1 = lat0, lat1
        bx, by, bw, bh = box
        sx = bw/((x1-x0)); sy = bh/((lat1-lat0))
        self.s = min(sx, sy)
        # center within box
        mw = (x1-x0)*self.s; mh = (lat1-lat0)*self.s
        self.ox = bx + (bw-mw)/2 - x0*self.s
        self.oy = by + (bh-mh)/2 + lat1*self.s   # y flips
    def __call__(self, lng, lat):
        x = self.ox + lng*self.k*self.s
        y = self.oy - lat*self.s
        return x, y

def bounds_of(points, pad=0.0):
    lats=[p[1] for p in points]; lngs=[p[0] for p in points]
    dlat=(max(lats)-min(lats))*pad; dlng=(max(lngs)-min(lngs))*pad
    return (min(lats)-dlat, max(lats)+dlat, min(lngs)-dlng, max(lngs)+dlng)

def ky_points(ky):
    g = ky["geometry"] if "geometry" in ky else ky
    rings=[]
    if g["type"]=="Polygon":
        rings=[g["coordinates"][0]]
    else:
        for poly in g["coordinates"]:
            rings.append(poly[0])
    return rings

def draw_outline(page, rings, proj, fill=LANDFILL, stroke=PRIMARY, width=0.9):
    for ring in rings:
        pts=[fitz.Point(*proj(lng,lat)) for lng,lat,*_ in ring]
        page.draw_polyline(pts, color=stroke, fill=fill, width=width,
                           closePath=True, lineJoin=1)

# ---------- de-overlap (spider on paper) ----------
def relax(anchors, r, iters=260, box=None, pull=0.05, max_up=None, clampfn=None):
    """anchors: list of [x,y]; push apart by >=2r, keep near anchor.
    box clamps inside a rect; clampfn(p) adjusts a single [x,y] in place each
    iteration (e.g. keep inside a map outline). pull = anchor attraction.
    Returns new positions."""
    pos=[list(a) for a in anchors]
    min_d = 2*r + 1.4
    for _ in range(iters):
        moved=False
        for i in range(len(pos)):
            for j in range(i+1,len(pos)):
                dx=pos[j][0]-pos[i][0]; dy=pos[j][1]-pos[i][1]
                d=math.hypot(dx,dy)
                if d < min_d:
                    if d < 1e-6:
                        dx, dy, d = 0.7, 0.5, 0.86
                    push=(min_d-d)/2
                    ux,uy=dx/d,dy/d
                    pos[i][0]-=ux*push; pos[i][1]-=uy*push
                    pos[j][0]+=ux*push; pos[j][1]+=uy*push
                    moved=True
        for i,(ax,ay) in enumerate(anchors):
            pos[i][0]+=(ax-pos[i][0])*pull
            pos[i][1]+=(ay-pos[i][1])*pull
        if max_up is not None:
            for i,(ax,ay) in enumerate(anchors):
                if pos[i][1] < ay-max_up: pos[i][1]=ay-max_up
        if box:
            for p in pos:
                p[0]=min(max(p[0], box[0]+r), box[2]-r)
                p[1]=min(max(p[1], box[1]+r), box[3]-r)
        if clampfn:
            for p in pos: clampfn(p)
        if not moved: break
    return pos

def draw_pin(page, x, y, num, color, r=7.2, fs=7.2, anchor=None):
    if anchor and math.hypot(anchor[0]-x, anchor[1]-y) > 1.6:
        page.draw_line(fitz.Point(*anchor), fitz.Point(x,y), color=color, width=0.5)
        page.draw_circle(fitz.Point(*anchor), 1.1, color=None, fill=color)
    page.draw_circle(fitz.Point(x,y), r, color=WHITE, fill=color, width=0.9)
    text(page, x, y+fs*0.34, str(num), font="dm-bold", size=fs, color=WHITE, align="center")

# ---------- header / footer ----------
def logo(page, x, y, scale=1.0):
    s=14*scale
    rrect(page, fitz.Rect(x, y-s, x+s, y), 3, fill=PRIMARY)
    text(page, x+s/2, y-s*0.27, "B", font="fr-black", size=10*scale, color=WHITE, align="center")
    text(page, x+s+6, y-s*0.18, "Bourbon Trail", font="fr-bold", size=12*scale, color=INK)
    w=_tl(page, "Bourbon Trail", "fr-bold", 12*scale)
    text(page, x+s+6+w, y-s*0.18, "Planner", font="fr-bold", size=12*scale, color=GOLD)

def header(page, W, right_label):
    M=40
    logo(page, M, 52)
    text(page, W-M, 40, right_label, font="dm-bold", size=9.5, color=INK, align="right")
    text(page, W-M, 52, "mybourbontrailplan.com", font="dm", size=8.5, color=MUTED, align="right")
    page.draw_line(fitz.Point(M,62), fitz.Point(W-M,62), color=GOLD, width=1.6)

# ===================================================================
# PAGE 1  -  hero map (landscape)
# ===================================================================
def build_page1(doc, data, ky):
    W,H = 792,612
    page = doc.new_page(width=W, height=H)
    reg_font(page); M=40
    page.draw_rect(fitz.Rect(0,0,W,H), color=None, fill=WHITE)
    header(page, W, "Printable Trail Map")

    # title
    text(page, M, 92, "KENTUCKY BOURBON TRAIL", font="dm-bold", size=9.5,
         color=GOLD, tracking=2.4)
    text(page, M, 122, "The Complete Distillery Map", font="fr-black", size=27, color=INK)
    text(page, M, 142, "Every distillery, every region. Official trail and craft producers, all on one map.",
         font="dm", size=10.5, color=MUTED)

    dists = data["distilleries"]
    central_regs = {"Louisville","Bardstown & New Hope","Frankfort","Lexington / Lawrenceburg"}
    central = [d for d in dists if d["region"] in central_regs]
    outer   = [d for d in dists if d["region"] not in central_regs]

    rings = ky_points(ky)
    # keep only substantial rings (drop tiny river-island slivers)
    rings = [r for r in rings if len(r) >= 6]
    allpts=[p for r in rings for p in r]
    kb = bounds_of(allpts)

    # ---- statewide map (left) ----
    smap = (M, 176, 384, 250)   # x,y,w,h
    proj = Proj(kb[0],kb[1],kb[2],kb[3], smap)
    draw_outline(page, rings, proj)

    # inset window = bounds of central pins (padded)
    cb = bounds_of([(d["lng"],d["lat"]) for d in central], pad=0.12)
    p_tl=proj(cb[2],cb[1]); p_br=proj(cb[3],cb[0])
    page.draw_rect(fitz.Rect(p_tl[0],p_tl[1],p_br[0],p_br[1]),
                   color=INK, width=0.9, dashes="[2.5 2] 0")
    text(page, p_tl[0], p_tl[1]-4, "see inset", font="dm-bold", size=6.6, color=INK)

    # central pins on statewide = small dots at TRUE position (no number)
    for d in central:
        x,y=proj(d["lng"],d["lat"])
        page.draw_circle(fitz.Point(x,y), 2.2, color=WHITE, fill=REGION_COLORS[d["region"]], width=0.5)
    # outer-region pins on statewide = numbered, de-overlapped, no north drift
    anchors=[list(proj(d["lng"],d["lat"])) for d in outer]
    # Border profile via polygon edge-crossings so de-overlap keeps pins inside
    # the KY outline. River-edge towns (Newport's New Riff, etc.) sit on the
    # northern line; the clamp nudges their pins just inside, off Ohio.
    edges=[]
    for ring in rings:
        pp=[proj(lng,lat) for lng,lat,*_ in ring]
        for k in range(len(pp)):
            edges.append((pp[k], pp[(k+1)%len(pp)]))
    pxs=[p[0] for e in edges for p in e]
    xlo,xhi=int(min(pxs)),int(max(pxs))
    top_prof={}; bot_prof={}
    for xi in range(xlo, xhi+1):
        ys=[]
        for (x1,y1),(x2,y2) in edges:
            if (x1-xi)*(x2-xi)<=0 and x1!=x2:
                ys.append(y1+(y2-y1)*(xi-x1)/(x2-x1))
        if len(ys)>=2: top_prof[xi]=min(ys); bot_prof[xi]=max(ys)
    R=6.6
    def border_clamp(p):
        xi=int(round(p[0]))
        xi=min(max(xi,xlo),xhi)
        if xi in top_prof:
            t,b=top_prof[xi],bot_prof[xi]
            if p[1] < t+R+2.8: p[1]=t+R+2.8
            if p[1] > b-R-1.4: p[1]=b-R-1.4
    pos = relax(anchors, r=R, pull=0.08, clampfn=border_clamp)
    for d,a,p in zip(outer, anchors, pos):
        draw_pin(page, p[0],p[1], d["num"], REGION_COLORS[d["region"]],
                 r=R, fs=6.2, anchor=a)
    for label,(lng,lat),dx in [("Paducah",(-88.75,37.05),4),
                               ("Bowling Green",(-86.55,36.93),4)]:
        x,y=proj(lng,lat)
        page.draw_circle(fitz.Point(x,y),1.4,color=None,fill=INK)
        text(page, x+dx, y+2.5, label, font="dm-med", size=6.8, color=MUTED)

    # ---- inset (right) ----
    ibox = fitz.Rect(448, 168, W-M, 452)
    rrect(page, ibox, 9, color=HAIR, fill=PAPER, width=1)
    text(page, ibox.x0+16, ibox.y0+24, "THE CENTRAL CORRIDOR",
         font="dm-bold", size=8.5, color=PRIMARY, tracking=1.6)
    text(page, ibox.x0+16, ibox.y0+38,
         "Where most of the trail lives, zoomed for clarity.",
         font="dm", size=8.3, color=MUTED)
    inner = fitz.Rect(ibox.x0+16, ibox.y0+50, ibox.x1-16, ibox.y1-16)
    imap = (inner.x0, inner.y0, inner.width, inner.height)
    iproj = Proj(cb[0],cb[1],cb[2],cb[3], imap)
    ianch=[list(iproj(d["lng"],d["lat"])) for d in central]
    ipos = relax(ianch, r=6.4, box=(inner.x0,inner.y0,inner.x1,inner.y1), pull=0.12)
    for d,a,p in zip(central, ianch, ipos):
        draw_pin(page, p[0],p[1], d["num"], REGION_COLORS[d["region"]],
                 r=6.4, fs=6.0, anchor=a)
    # label only the geographically isolated towns, placed clear below their pins
    TOWN=(0x8C/255,0x9A/255,0xA6/255)
    bycity={}
    for d,p in zip(central, ipos): bycity.setdefault(d["city"], []).append(p)
    for town in ("Shelbyville","Danville","Paris"):
        if town in bycity:
            pts=bycity[town]
            cx=sum(p[0] for p in pts)/len(pts)
            by=max(p[1] for p in pts)+13
            text(page, cx, by, town, font="dm-med", size=6.2, color=TOWN, align="center")
    # region labels placed above each cluster centroid (clear of pins)
    clusters={}
    for d,p in zip(central, ipos):
        clusters.setdefault(d["region"], []).append(p)
    short={"Louisville":"LOUISVILLE","Bardstown & New Hope":"BARDSTOWN",
           "Frankfort":"FRANKFORT","Lexington / Lawrenceburg":"LEXINGTON / LAWRENCEBURG"}
    place={"Louisville":"above","Bardstown & New Hope":"above",
           "Frankfort":"above","Lexington / Lawrenceburg":"below"}
    for reg,pts in clusters.items():
        cx=sum(p[0] for p in pts)/len(pts)
        if place[reg]=="above":
            ly=max(inner.y0+9, min(p[1] for p in pts)-12)
        else:
            ys=sorted(p[1] for p in pts)
            q=ys[int(len(ys)*0.7)]
            ly=min(inner.y1-4, q+16)
        cx=min(max(cx, inner.x0+ _tl(page,short[reg],"dm-bold",6.6)/2),
               inner.x1- _tl(page,short[reg],"dm-bold",6.6)/2)
        text(page, cx, ly, short[reg], font="dm-bold", size=6.6,
             color=REGION_COLORS[reg], align="center", tracking=0.5)

    order=data["meta"]["region_order"]
    # ---- legend (bottom left band) ----
    ly=496
    text(page, M, ly, "REGIONS", font="dm-bold", size=8.5, color=INK, tracking=1.6)
    col_w=143; rows=[order[:3],order[3:]]
    for ri,row in enumerate(rows):
        yy=ly+18+ri*20
        for ci,reg in enumerate(row):
            xx=M+ci*col_w
            page.draw_circle(fitz.Point(xx+5, yy-3), 5, color=WHITE, fill=REGION_COLORS[reg], width=0.8)
            text(page, xx+16, yy, reg, font="dm-med", size=8.6, color=INK)

    # ---- QR card (bottom right) ----
    qr = qrcode.QRCode(border=0, box_size=10,
                       error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(data["meta"]["trip_builder_url"]); qr.make()
    img = qr.make_image(fill_color="#0E2F44", back_color="white").convert("RGB")
    buf=io.BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
    card=fitz.Rect(452, 486, W-M, 560)
    rrect(page, card, 8, color=HAIR, fill=PAPER, width=1)
    qsize=58
    page.insert_image(fitz.Rect(card.x0+12, card.y0+8, card.x0+12+qsize, card.y0+8+qsize),
                      stream=buf.getvalue())
    tx=card.x0+12+qsize+12
    text(page, tx, card.y0+24, "Build your route", font="fr-bold", size=12.5, color=INK)
    text(page, tx, card.y0+40, "Scan to open the free Trip Builder:", font="dm", size=8.6, color=MUTED)
    text(page, tx, card.y0+52, "pick stops, see real drive times,", font="dm", size=8.6, color=MUTED)
    text(page, tx, card.y0+64, "and save a day-by-day plan.", font="dm", size=8.6, color=MUTED)

    # footer
    page.draw_line(fitz.Point(M,575), fitz.Point(W-M,575), color=HAIR, width=0.8)
    text(page, M, 590, "Bourbon Trail Planner",
         font="dm", size=8, color=MUTED)
    text(page, W-M, 590, "Full reviews & planner at mybourbontrailplan.com",
         font="dm-med", size=8, color=PRIMARY, align="right")

# ===================================================================
# PAGE 2  -  reference list + planner (landscape, 4-column flow)
# ===================================================================
def build_page2(doc, data, ky):
    W,H = 792,612
    page = doc.new_page(width=W, height=H)
    reg_font(page); M=40
    page.draw_rect(fitz.Rect(0,0,W,H), color=None, fill=WHITE)
    header(page, W, "Distillery Reference")

    text(page, M, 90, "EVERY KENTUCKY DISTILLERY, BY REGION", font="dm-bold",
         size=9, color=GOLD, tracking=1.8)
    text(page, M, 116, "Reference & Trip Planner", font="fr-black", size=22, color=INK)
    text(page, M, 134, "Numbers match the map. Check the box as you visit.",
         font="dm", size=9.5, color=MUTED)

    dists=data["distilleries"]
    order=data["meta"]["region_order"]

    # ---- 4-column flow ----
    NCOL=4; gap=20
    list_x0=M; list_x1=W-M
    col_w=(list_x1-list_x0-gap*(NCOL-1))/NCOL
    colx=[list_x0+i*(col_w+gap) for i in range(NCOL)]
    top=152; bottom=486
    row_h=18.6; head_h=20
    y=[top]*NCOL; c=0

    def newcol():
        nonlocal c
        c+=1
        return c < NCOL

    def header_row(reg, cont=False):
        nonlocal c
        x=colx[c]
        page.draw_circle(fitz.Point(x+4, y[c]-3.5), 4.4, color=WHITE, fill=REGION_COLORS[reg], width=0.8)
        label = reg.upper()+(" (CONT.)" if cont else "")
        text(page, x+13, y[c], label, font="dm-bold", size=8.2, color=INK, tracking=0.4)
        if not cont:
            cnt=sum(1 for d in dists if d["region"]==reg)
            text(page, colx[c]+col_w, y[c], str(cnt), font="dm-bold", size=8.2, color=MUTED, align="right")
        y[c]+=5
        page.draw_line(fitz.Point(x, y[c]), fitz.Point(colx[c]+col_w, y[c]), color=HAIR, width=0.7)
        y[c]+=12

    def row(d, reg):
        x=colx[c]
        rrect(page, fitz.Rect(x, y[c]-7.3, x+8, y[c]+0.7), 1.2, color=MUTED, width=0.8)
        page.draw_circle(fitz.Point(x+19, y[c]-3.3), 6.6, color=None, fill=REGION_COLORS[reg])
        text(page, x+19, y[c]-1, str(d["num"]), font="dm-bold", size=6.6, color=WHITE, align="center")
        nm=d["name"]
        while _tl(page, nm, "dm-med", 8.1) > col_w-52 and len(nm)>4:
            nm=nm[:-2]
        if nm!=d["name"]: nm=nm.rstrip()+"\u2026"
        text(page, x+31, y[c], nm, font="dm-med", size=8.1, color=INK)
        tag="Trail" if d["trail"]=="Trail" else "Craft"
        cost=d["cost"] if d["cost"] else "Free"
        text(page, x+31, y[c]+9, f"{d['city']}  \u00b7  {tag}  \u00b7  {cost}",
             font="dm", size=6.9, color=MUTED)
        bc=BOOK_COLORS.get(d["booking"], MUTED)
        page.draw_circle(fitz.Point(colx[c]+col_w-3, y[c]-3), 3, color=None, fill=bc)
        y[c]+=row_h

    for reg in order:
        rows=[d for d in dists if d["region"]==reg]
        # need room for header + at least 2 rows, else next column
        if y[c]+head_h+row_h*2 > bottom:
            if not newcol(): break
        header_row(reg)
        for d in rows:
            if y[c]+row_h > bottom:
                if not newcol(): break
                header_row(reg, cont=True)
            row(d, reg)

    # ---- bottom band ----
    by=506
    page.draw_line(fitz.Point(M,by-6), fitz.Point(W-M,by-6), color=HAIR, width=0.8)

    # drive times (left, 2 x 3 grid)
    text(page, M, by+12, "DRIVE TIMES BETWEEN HUBS", font="dm-bold", size=8.3, color=INK, tracking=1.0)
    drives=[("Louisville","Bardstown","50 min"),("Louisville","Lexington","1 hr 15"),
            ("Bardstown","Frankfort","50 min"),("Frankfort","Lexington","30 min"),
            ("Bardstown","Lexington","50 min"),("Louisville","Owensboro","1 hr 50")]
    for i,(a,b,t) in enumerate(drives):
        col=i//3; r=i%3
        xx=M+col*168; ry=by+30+r*15
        text(page, xx, ry, f"{a} \u2013 {b}", font="dm", size=8, color=MUTED)
        text(page, xx+132, ry, t, font="dm-med", size=8, color=INK, align="right")

    # booking ease index (center)
    cx0=M+316
    text(page, cx0, by+12, "BOOKING EASE", font="dm-bold", size=8.3, color=INK, tracking=1.0)
    gloss=[("Easy","Walk-up or same-week reservation"),
           ("Moderate","Book about a week ahead"),
           ("Hard","Reserve 4 to 6 weeks ahead")]
    for i,(lab,desc) in enumerate(gloss):
        ry=by+30+i*15
        page.draw_circle(fitz.Point(cx0+4, ry-2.5), 4, color=None, fill=BOOK_COLORS[lab])
        text(page, cx0+14, ry, lab, font="dm-bold", size=8, color=INK)
        text(page, cx0+64, ry, desc, font="dm", size=8, color=MUTED)

    # QR (right)
    qr=qrcode.QRCode(border=0, box_size=10, error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(data["meta"]["trip_builder_url"]); qr.make()
    img=qr.make_image(fill_color="#0E2F44", back_color="white").convert("RGB")
    buf=io.BytesIO(); img.save(buf,format="PNG")
    qs=66; qx=W-M-qs
    page.insert_image(fitz.Rect(qx, by+6, qx+qs, by+6+qs), stream=buf.getvalue())
    text(page, qx-10, by+22, "Build your route", font="fr-bold", size=11.5, color=INK, align="right")
    text(page, qx-10, by+38, "Scan for the free Trip Builder:", font="dm", size=7.6, color=MUTED, align="right")
    text(page, qx-10, by+49, "pick stops, see drive times,", font="dm", size=7.6, color=MUTED, align="right")
    text(page, qx-10, by+60, "save a day-by-day plan.", font="dm", size=7.6, color=MUTED, align="right")

    # footer
    page.draw_line(fitz.Point(M,587), fitz.Point(W-M,587), color=HAIR, width=0.8)
    text(page, M, 600, "Bourbon Trail Planner",
         font="dm", size=8, color=MUTED)
    text(page, W-M, 600, "New distilleries open yearly. Latest at mybourbontrailplan.com",
         font="dm-med", size=8, color=PRIMARY, align="right")


def main():
    data, ky = load()
    doc = fitz.open()
    build_page1(doc, data, ky)
    build_page2(doc, data, ky)
    doc.set_metadata({"title":"Kentucky Bourbon Trail: The Complete Distillery Map",
                      "author":"Bourbon Trail Planner",
                      "subject":"Printable Kentucky Bourbon Trail map and distillery checklist"})
    doc.save(OUT, deflate=True, garbage=4)
    print("wrote", OUT, f"({len(data['distilleries'])} distilleries)")

if __name__=="__main__":
    main()
