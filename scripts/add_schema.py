#!/usr/bin/env python3
"""Comprehensive JSON-LD schema update for mybourbontrailplan.com"""

import os, re, json

BASE_DIR = r"C:\Users\cowde\Desktop\mybourbontrailplan"

REVIEW_BLOCK = {
    "@type": "Review",
    "reviewRating": {
        "@type": "Rating",
        "ratingValue": None,  # filled per distillery
        "bestRating": "10",
        "worstRating": "1"
    },
    "author": {"@type": "Person", "name": "Kyle Cowden"}
}

# Ratings for all active distilleries
RATINGS = {
    "angels-envy": 8.8, "old-forester": 8.9, "evan-williams": 8.7,
    "buzzards-roost": 7.5, "rabbit-hole": 7.9, "michters": 8.6,
    "peerless": 8.2, "whiskey-thief": 7.5, "buffalo-trace": 9.2,
    "castle-key": 8.3, "woodford-reserve": 8.5, "wild-turkey": 8.1,
    "four-roses": 8.3, "makers-mark": 9.0, "heaven-hill": 8.5,
    "preservation": 7.5, "lux-row": 8.0, "willett": 8.2,
    "bardstown-bourbon-co": 8.5, "log-still": 7.8, "jim-beam": 8.4,
    "town-branch": 7.4, "pensive": 8.0, "new-riff": 8.4,
    "wilderness-trail": 8.3, "dark-arts": 8.0, "chicken-cock": 7.0,
    "augusta": 8.1, "general-george": 7.0,
    # Missing schemas:
    "baker-bird": 7.5, "barrel-house": 7.5, "bh-james": 7.2,
    "bluegrass": 7.7, "boone-county": 7.8, "boundary-oak": 7.3,
    "bulleit": 8.0, "casey-jones": 7.5, "copper-kings": 8.3,
    "dueling-grounds": 7.3, "fresh-bourbon": 8.2, "glenns-creek": 7.6,
    "golden-pond": 7.1, "green-river": 8.1, "hartfield": 7.6,
    "j-mattingly": 7.9, "jackson-purchase": 7.3, "james-e-pepper": 7.8,
    "jeptha-creed": 8.0, "kentucky-artisan": 8.0, "larrikin": 7.3,
    "limestone-branch": 7.9, "mb-roland": 7.4, "neeley-family": 7.2,
    "old-pogue": 7.4, "rd1-spirits": 8.4, "second-sight": 7.5,
    "stitzel-weller": 8.6, "the-bard": 7.4, "wenzel": 7.3,
}

# File ID -> copper-and-kings uses "copper-kings" in trip-builder
FILE_TO_ID = {
    "copper-and-kings": "copper-kings",
}

def get_id(slug):
    return FILE_TO_ID.get(slug, slug)

# Full schema data for the 30 distillery files that currently have NO schema
NEW_DISTILLERIES = {
    "baker-bird": {
        "name": "Becker & Bird Distillery",
        "description": "Historic Augusta winery and distillery combo on the Ohio River.",
        "address": {"@type": "PostalAddress", "addressLocality": "Augusta", "addressRegion": "KY", "postalCode": "41002", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 38.6360, "longitude": -83.7740},
        "telephone": "+1-606-756-2708",
        "url": "https://www.bakerbird.com",
    },
    "barrel-house": {
        "name": "Barrel House Distilling Co.",
        "description": "Casual Distillery District stop. Affordable tours, pair with James E. Pepper.",
        "address": {"@type": "PostalAddress", "streetAddress": "1200 Manchester St", "addressLocality": "Lexington", "addressRegion": "KY", "postalCode": "40504", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 38.0540, "longitude": -84.4890},
        "telephone": "+1-859-259-0159",
        "openingHours": "Mo-Su 11:00-17:00",
        "url": "https://www.barrelhousedistillery.com/visit",
    },
    "bh-james": {
        "name": "B.H. James Distillers",
        "description": "Small Western KY operation in Whitesville. Off-the-path craft stop.",
        "address": {"@type": "PostalAddress", "addressLocality": "Whitesville", "addressRegion": "KY", "postalCode": "42378", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 37.6910, "longitude": -87.0700},
        "url": "https://www.bhjamesdistillers.com",
    },
    "bluegrass": {
        "name": "Bluegrass Distillers",
        "description": "True craft operation in Kentucky. Blue corn bourbon.",
        "address": {"@type": "PostalAddress", "streetAddress": "501 Elkwood Farm Ln", "addressLocality": "Midway", "addressRegion": "KY", "postalCode": "40347", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 38.0355, "longitude": -84.5205},
        "telephone": "+1-859-253-0012",
        "url": "https://www.bluegrassdistillers.com/visit",
    },
    "boone-county": {
        "name": "Boone County Distilling Co.",
        "description": "Northern KY gem. First distillery in Boone County since Prohibition.",
        "address": {"@type": "PostalAddress", "streetAddress": "10601 Toebben Dr", "addressLocality": "Independence", "addressRegion": "KY", "postalCode": "41051", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 38.9370, "longitude": -84.6610},
        "telephone": "+1-859-282-6545",
        "openingHours": "Th-Sa 10:00-17:00, Su 12:00-17:00",
        "url": "https://www.boonedistilling.com/visit",
    },
    "boundary-oak": {
        "name": "Boundary Oak Distillery",
        "description": "Family-owned near Fort Knox. Military-themed bourbons, natural spring.",
        "address": {"@type": "PostalAddress", "streetAddress": "2000 Boundary Oak Dr", "addressLocality": "Radcliff", "addressRegion": "KY", "postalCode": "40160", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 37.8210, "longitude": -85.9010},
        "telephone": "+1-270-351-2013",
        "openingHours": "Mo-Sa 10:00-18:00, Su 12:00-17:00",
        "url": "https://www.boundaryoak.co/",
    },
    "bulleit": {
        "name": "Bulleit Distilling Co.",
        "description": "Diageo's showcase facility in Shelbyville. Modern, scenic campus.",
        "address": {"@type": "PostalAddress", "streetAddress": "3464 Benson Pike", "addressLocality": "Shelbyville", "addressRegion": "KY", "postalCode": "40065", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 37.9020, "longitude": -85.0110},
        "telephone": "+1-502-647-5799",
        "openingHours": "Th-Sa 09:30-17:00, Su 11:30-17:00",
        "url": "https://www.bulleit.com/visit-us",
    },
    "casey-jones": {
        "name": "Casey Jones Distillery",
        "description": "Moonshine heritage near the Tennessee border. Good Nashville day trip add-on.",
        "address": {"@type": "PostalAddress", "streetAddress": "2831 Ratliff Rd", "addressLocality": "Hopkinsville", "addressRegion": "KY", "postalCode": "42240", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 36.7920, "longitude": -86.5760},
        "telephone": "+1-270-839-9873",
        "openingHours": "Tu-Sa 10:00-17:00",
        "url": "https://www.caseyjonesdistillery.com",
    },
    "copper-and-kings": {
        "name": "Copper & Kings American Brandy Co.",
        "description": "American brandy meets bourbon. Underground barrel aging with bass-heavy music.",
        "address": {"@type": "PostalAddress", "streetAddress": "1121 E Washington St", "addressLocality": "Louisville", "addressRegion": "KY", "postalCode": "40206", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 38.2380, "longitude": -85.7450},
        "telephone": "+1-502-561-0267",
        "url": "https://www.copperandkings.com/visit/",
    },
    "dueling-grounds": {
        "name": "Dueling Grounds Distillery",
        "description": "Near the Tennessee border. Good Nashville-area bourbon stop.",
        "address": {"@type": "PostalAddress", "streetAddress": "804 N Main St", "addressLocality": "Franklin", "addressRegion": "KY", "postalCode": "42134", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 36.7210, "longitude": -86.5640},
        "telephone": "+1-270-586-0006",
        "openingHours": "Tu-Sa 10:00-17:00",
        "url": "https://duelinggroundsdistillery.com/",
    },
    "fresh-bourbon": {
        "name": "Fresh Bourbon Distillery",
        "description": "Beautiful horse country farm. Grain-to-glass with pastoral views.",
        "address": {"@type": "PostalAddress", "streetAddress": "377 E Main St", "addressLocality": "Lexington", "addressRegion": "KY", "postalCode": "40507", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 38.0350, "longitude": -84.7500},
        "telephone": "+1-859-203-3741",
        "url": "https://freshbourbon.com/tours-and-tastings/",
    },
    "glenns-creek": {
        "name": "Glenns Creek Distilling",
        "description": "Historic Old Crow site reborn. Small-batch bourbon on hallowed ground.",
        "address": {"@type": "PostalAddress", "streetAddress": "8800 Glenns Creek Rd", "addressLocality": "Frankfort", "addressRegion": "KY", "postalCode": "40601", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 38.1845, "longitude": -84.8470},
        "telephone": "+1-502-352-8072",
        "openingHours": "Th-Sa 10:00-16:00",
        "url": "https://www.glennscreekdistilling.com",
    },
    "golden-pond": {
        "name": "Golden Pond Distilleries",
        "description": "Near Land Between the Lakes. Remote Western KY moonshine and bourbon.",
        "address": {"@type": "PostalAddress", "addressLocality": "Golden Pond", "addressRegion": "KY", "postalCode": "42211", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 36.8410, "longitude": -87.9960},
        "telephone": "+1-270-205-7685",
        "url": "https://www.goldenponddistilleries.com",
    },
    "green-river": {
        "name": "Green River Distilling Co.",
        "description": "One of Kentucky's oldest brands reborn in Owensboro.",
        "address": {"@type": "PostalAddress", "streetAddress": "10 Distillery Rd", "addressLocality": "Owensboro", "addressRegion": "KY", "postalCode": "42301", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 37.7740, "longitude": -87.1130},
        "telephone": "+1-270-691-9001",
        "openingHours": "We-Sa 10:00-17:00, Su 12:00-17:00",
        "url": "https://greenriverdistilling.com/visit/",
    },
    "hartfield": {
        "name": "Hartfield & Co. Distillery",
        "description": "Paris, KY craft distillery. First in Bourbon County since Prohibition.",
        "address": {"@type": "PostalAddress", "streetAddress": "718 Main St", "addressLocality": "Paris", "addressRegion": "KY", "postalCode": "40361", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 38.5050, "longitude": -84.2980},
        "telephone": "+1-859-987-0290",
        "openingHours": "Tu-Sa 10:00-18:00",
        "url": "https://www.hartfieldandcompany.com",
    },
    "j-mattingly": {
        "name": "J. Mattingly 1845 Distillery",
        "description": "Custom barrel blending experience. Hands-on, personal Frankfort craft stop.",
        "address": {"@type": "PostalAddress", "streetAddress": "20 Reilly Rd", "addressLocality": "Frankfort", "addressRegion": "KY", "postalCode": "40601", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 38.2065, "longitude": -84.8725},
        "telephone": "+1-859-721-1854",
        "openingHours": "Mo-Sa 08:30-17:00, Su 12:00-17:00",
        "url": "https://www.jmattingly1845.com/visit",
    },
    "jackson-purchase": {
        "name": "Jackson Purchase Distillery",
        "description": "Far western KY craft outpost near Paducah. Corn whiskey roots.",
        "address": {"@type": "PostalAddress", "addressLocality": "Paducah", "addressRegion": "KY", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 36.8530, "longitude": -88.6490},
        "telephone": "+1-270-838-2198",
        "url": "https://www.jacksonpurchasedistillery.com",
    },
    "james-e-pepper": {
        "name": "James E. Pepper Distillery",
        "description": "Distillery District anchor. Historic brand reborn in Lexington.",
        "address": {"@type": "PostalAddress", "streetAddress": "1228 Manchester St", "addressLocality": "Lexington", "addressRegion": "KY", "postalCode": "40504", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 38.0545, "longitude": -84.4860},
        "telephone": "+1-859-309-2037",
        "url": "https://jamesepepper.com/visit/",
    },
    "jeptha-creed": {
        "name": "Jeptha Creed Distillery",
        "description": "Ground-to-glass family farm. Bloody Butcher corn, vodka, and bourbon.",
        "address": {"@type": "PostalAddress", "streetAddress": "500 Gordon Ln", "addressLocality": "Shelbyville", "addressRegion": "KY", "postalCode": "40065", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 38.2880, "longitude": -85.3260},
        "telephone": "+1-502-487-1051",
        "openingHours": "We-Sa 10:00-17:00, Su 13:00-17:00",
        "url": "https://www.jepthacreed.com/visit",
    },
    "kentucky-artisan": {
        "name": "Kentucky Artisan Distillery",
        "description": "Contract distilling plus their own brands. Jeff Ruby's collaboration.",
        "address": {"@type": "PostalAddress", "streetAddress": "6230 Old LaGrange Rd", "addressLocality": "Crestwood", "addressRegion": "KY", "postalCode": "40014", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 37.9680, "longitude": -85.1650},
        "telephone": "+1-502-822-3042",
        "openingHours": "Tu-Fr 10:00-16:00, Sa 10:00-14:00",
        "url": "https://jeffersonsbourbon.com/visit-us/",
    },
    "larrikin": {
        "name": "Larrikin Bourbon Co.",
        "description": "Australian-born distillers making bourbon in Lawrenceburg. Unique story.",
        "address": {"@type": "PostalAddress", "addressLocality": "Lawrenceburg", "addressRegion": "KY", "postalCode": "40342", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 38.0870, "longitude": -84.8975},
        "telephone": "+1-859-300-9590",
        "url": "https://www.larrikinbourbon.com",
    },
    "limestone-branch": {
        "name": "Limestone Branch Distillery",
        "description": "Beam family heritage in Lebanon. Yellowstone bourbon, Minor Case rye.",
        "address": {"@type": "PostalAddress", "streetAddress": "1280 Veterans Memorial Hwy", "addressLocality": "Lebanon", "addressRegion": "KY", "postalCode": "40033", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 37.7320, "longitude": -85.3370},
        "telephone": "+1-270-699-9004",
        "openingHours": "Tu-Sa 10:00-17:00, Su 12:30-17:00",
        "url": "https://www.limestonebranch.com/visit",
    },
    "mb-roland": {
        "name": "MB Roland Distillery",
        "description": "Farm-to-bottle craft in Pembroke. Unfiltered Kentucky spirit.",
        "address": {"@type": "PostalAddress", "streetAddress": "894 Barkers Mill Rd", "addressLocality": "Pembroke", "addressRegion": "KY", "postalCode": "42266", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 36.7770, "longitude": -87.3850},
        "telephone": "+1-270-640-7744",
        "openingHours": "Mo-Sa 09:00-17:00",
        "url": "https://www.mbroland.com",
    },
    "neeley-family": {
        "name": "Neeley Family Distillery",
        "description": "Quick I-71 corridor stop. Small family craft operation.",
        "address": {"@type": "PostalAddress", "streetAddress": "625 Main St", "addressLocality": "Sparta", "addressRegion": "KY", "postalCode": "41086", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 38.6880, "longitude": -84.8400},
        "telephone": "+1-859-643-3500",
        "url": "https://www.neeleyfamilydistillery.com",
    },
    "old-pogue": {
        "name": "The Old Pogue Distillery",
        "description": "Maysville heritage brand. Civil War-era recipe revived.",
        "address": {"@type": "PostalAddress", "streetAddress": "705 Germantown Rd", "addressLocality": "Maysville", "addressRegion": "KY", "postalCode": "41056", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 38.5440, "longitude": -84.1410},
        "telephone": "+1-606-564-0345",
        "url": "https://www.oldpogue.com",
    },
    "rd1-spirits": {
        "name": "RD1 Spirits",
        "description": "Sourcing-first Lexington distillery. Great blending experiences.",
        "address": {"@type": "PostalAddress", "streetAddress": "113 Turner Commons Way", "addressLocality": "Lexington", "addressRegion": "KY", "postalCode": "40508", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 38.0460, "longitude": -84.4950},
        "telephone": "+1-859-286-5550",
        "openingHours": "Mo-Th 11:00-18:00, Fr-Sa 11:00-19:00, Su 12:00-18:00",
        "url": "https://rd1spirits.com/pages/distillery-at-the-commons",
    },
    "second-sight": {
        "name": "Second Sight Spirits",
        "description": "Arts-forward experimental spirits in Ludlow. Creative Northern KY wild card.",
        "address": {"@type": "PostalAddress", "streetAddress": "301 Elm St", "addressLocality": "Ludlow", "addressRegion": "KY", "postalCode": "41016", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 39.0890, "longitude": -84.5710},
        "telephone": "+1-859-261-6222",
        "url": "https://www.secondsightspirits.com",
    },
    "stitzel-weller": {
        "name": "Stitzel-Weller Distillery",
        "description": "Historic Pappy Van Winkle home. Blade & Bow, I.W. Harper. A bourbon pilgrimage.",
        "address": {"@type": "PostalAddress", "streetAddress": "3860 Fitzgerald Rd", "addressLocality": "Shively", "addressRegion": "KY", "postalCode": "40216", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 38.2200, "longitude": -85.8040},
        "telephone": "+1-502-810-3800",
        "openingHours": "We-Mo 10:00-18:00",
        "url": "https://www.stitzelwellerdistillery.com/visit-us",
    },
    "the-bard": {
        "name": "The Bard Distillery",
        "description": "Small-batch Bardstown craft. Walk-in friendly, personal tours.",
        "address": {"@type": "PostalAddress", "addressLocality": "Bardstown", "addressRegion": "KY", "postalCode": "40004", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 37.8130, "longitude": -85.4740},
        "telephone": "+1-502-510-2010",
        "url": "https://www.barddistillery.com",
    },
    "wenzel": {
        "name": "Wenzel Distilling Co.",
        "description": "Small-batch Northern KY craft whiskey. Pair with New Riff.",
        "address": {"@type": "PostalAddress", "addressLocality": "Covington", "addressRegion": "KY", "postalCode": "41011", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 38.9840, "longitude": -84.6490},
        "telephone": "+1-859-279-3614",
        "url": "https://www.wenzeldistilling.com",
    },
}

def build_tourist_attraction(slug, data, rating):
    schema = {
        "@context": "https://schema.org",
        "@type": "TouristAttraction",
        "name": data["name"],
        "description": data["description"],
        "address": data["address"],
        "geo": data["geo"],
    }
    if "telephone" in data:
        schema["telephone"] = data["telephone"]
    if "openingHours" in data:
        schema["openingHours"] = data["openingHours"]
    schema["url"] = data["url"]
    schema["sameAs"] = data["url"]
    review = {
        "@type": "Review",
        "reviewRating": {
            "@type": "Rating",
            "ratingValue": str(rating),
            "bestRating": "10",
            "worstRating": "1"
        },
        "author": {"@type": "Person", "name": "Kyle Cowden"}
    }
    schema["review"] = review
    return schema

def add_review_to_existing(content, rating):
    """Parse existing TouristAttraction schema and add review block."""
    pattern = r'(<script type="application/ld\+json">\s*)((\{.*?"@type"\s*:\s*"TouristAttraction".*?\})(\s*</script>))'

    def replacer(m):
        prefix = m.group(1)
        json_str = m.group(3)
        suffix = m.group(4)
        try:
            data = json.loads(json_str)
        except Exception as e:
            print(f"  JSON parse error: {e}")
            return m.group(0)

        if "review" in data:
            return m.group(0)  # already has review

        data["review"] = {
            "@type": "Review",
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": str(rating),
                "bestRating": "10",
                "worstRating": "1"
            },
            "author": {"@type": "Person", "name": "Kyle Cowden"}
        }
        # Add sameAs if url is present but sameAs is not
        if "url" in data and "sameAs" not in data:
            data["sameAs"] = data["url"]

        new_json = json.dumps(data, indent=2, ensure_ascii=False)
        return f"{prefix}\n{new_json}\n{suffix}"

    new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)
    return new_content

def insert_schema_before_head_close(content, schema_dict):
    """Insert a JSON-LD script block just before </head>."""
    json_str = json.dumps(schema_dict, indent=2, ensure_ascii=False)
    script_block = f'\n<script type="application/ld+json">\n{json_str}\n</script>'
    # Insert before </head>
    if "</head>" not in content:
        print("  WARNING: </head> not found")
        return content
    return content.replace("</head>", f"{script_block}\n</head>", 1)

def has_tourist_attraction_schema(content):
    return '"TouristAttraction"' in content

def process_distillery_file(filepath, slug):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    did_id = get_id(slug)
    rating = RATINGS.get(did_id)
    if rating is None:
        print(f"  SKIP: no rating found for {slug}")
        return False

    if has_tourist_attraction_schema(content):
        # Add review to existing schema
        new_content = add_review_to_existing(content, rating)
        if new_content == content:
            print(f"  SKIP: review already present or parse failed for {slug}")
            return False
        print(f"  Updated existing schema + review: {slug} ({rating})")
    else:
        # Build and insert full schema
        data = NEW_DISTILLERIES.get(slug)
        if data is None:
            print(f"  SKIP: no schema data for {slug}")
            return False
        schema = build_tourist_attraction(slug, data, rating)
        new_content = insert_schema_before_head_close(content, schema)
        print(f"  Inserted new schema: {slug} ({rating})")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True

# Files to skip entirely
SKIP_SLUGS = {"barton-1792", "garrard-county"}

# Non-distillery page schemas
NON_DISTILLERY_SCHEMAS = {
    "eat-and-drink-bourbon-trail.html": {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Where to Eat & Drink on the Kentucky Bourbon Trail (2026)",
        "description": "Best restaurants and bars near Bourbon Trail distilleries. Louisville, Bardstown, Frankfort, and Lexington dining guides.",
        "url": "https://mybourbontrailplan.com/eat-and-drink-bourbon-trail",
        "mainEntityOfPage": {"@type": "WebPage", "@id": "https://mybourbontrailplan.com/eat-and-drink-bourbon-trail"},
        "author": {"@type": "Person", "name": "Kyle Cowden"},
        "publisher": {"@type": "Organization", "name": "Bourbon Trail Planner", "url": "https://mybourbontrailplan.com/"},
        "datePublished": "2026-01-15",
        "dateModified": "2026-05-22",
    },
    "trip-builder.html": {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "Bourbon Trail Trip Builder",
        "description": "Build your perfect Kentucky Bourbon Trail itinerary. Add distilleries, see drive times, get smart tips, and export your plan. Free, no account needed.",
        "url": "https://mybourbontrailplan.com/trip-builder",
        "applicationCategory": "TravelApplication",
        "operatingSystem": "Web",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "author": {"@type": "Person", "name": "Kyle Cowden"},
    },
    "about.html": {
        "@context": "https://schema.org",
        "@type": "AboutPage",
        "name": "About Bourbon Trail Planner",
        "description": "Bourbon Trail Planner was built by people who've actually done the Kentucky Bourbon Trail — multiple times.",
        "url": "https://mybourbontrailplan.com/about",
        "mainEntity": {
            "@type": "Person",
            "name": "Kyle Cowden",
            "description": "Kentucky Bourbon Trail veteran and independent travel guide author.",
            "url": "https://mybourbontrailplan.com/about",
        },
    },
    "contact.html": {
        "@context": "https://schema.org",
        "@type": "ContactPage",
        "name": "Contact Bourbon Trail Planner",
        "description": "Get in touch with the Bourbon Trail Planner team. Questions, corrections, partnership inquiries, and feedback welcome.",
        "url": "https://mybourbontrailplan.com/contact",
    },
}

def process_non_distillery(filepath, schema):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if '"application/ld+json"' in content:
        print(f"  SKIP: already has schema: {os.path.basename(filepath)}")
        return False
    new_content = insert_schema_before_head_close(content, schema)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  Added schema ({schema['@type']}): {os.path.basename(filepath)}")
    return True

def upgrade_index_html():
    """Add Organization schema block to index.html."""
    filepath = os.path.join(BASE_DIR, "index.html")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if '"Organization"' in content:
        print("  SKIP: index.html already has Organization schema")
        return False

    org_schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Bourbon Trail Planner",
        "url": "https://mybourbontrailplan.com/",
        "description": "Independent trip planning resource for the Kentucky Bourbon Trail.",
        "founder": {"@type": "Person", "name": "Kyle Cowden"},
    }
    new_content = insert_schema_before_head_close(content, org_schema)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("  Added Organization schema to index.html")
    return True

def main():
    print("=== Distillery Profile Schema Update ===\n")

    distillery_files = [
        f for f in os.listdir(BASE_DIR)
        if f.startswith("distillery-") and f.endswith(".html") and " " not in f
    ]

    updated = 0
    skipped = 0

    for filename in sorted(distillery_files):
        slug = filename.replace("distillery-", "").replace(".html", "")
        if slug in SKIP_SLUGS:
            print(f"  SKIP (excluded): {filename}")
            skipped += 1
            continue
        filepath = os.path.join(BASE_DIR, filename)
        result = process_distillery_file(filepath, slug)
        if result:
            updated += 1
        else:
            skipped += 1

    print(f"\nDistillery files: {updated} updated, {skipped} skipped\n")

    print("=== Non-Distillery Page Schema ===\n")
    for filename, schema in NON_DISTILLERY_SCHEMAS.items():
        filepath = os.path.join(BASE_DIR, filename)
        process_non_distillery(filepath, schema)

    print("\n=== index.html Organization Schema ===\n")
    upgrade_index_html()

    print("\nDone.")

if __name__ == "__main__":
    main()
