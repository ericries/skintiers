#!/usr/bin/env python3
"""SkinTiers static site generator."""
import datetime
import hashlib
import html as _htmllib
import json
import os
import re
import shutil
import sys
import types

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
import sklib  # noqa: E402
import product_codes  # noqa: E402
import routine_string  # noqa: E402
from jinja2 import Environment, FileSystemLoader  # noqa: E402

LISTINGS = (
    ("product", "products", "Products"),
    ("ingredient", "ingredients", "Ingredients"),
    ("condition", "conditions", "Conditions"),
    ("goal", "goals", "Goals"),
    ("study", "studies", "Studies"),
    ("list", "lists", "Lists"),
    ("person", "people", "People"),
    ("brand", "brands", "Brands"),
)

# High-level buckets for the Products index. Two are by product format
# (Sunscreens, Moisturizers); the rest are by primary active and mirror the
# ingredient hubs. Order is stable; anything without a known category falls
# into "Other" at the end so nothing is dropped from the listing.
PRODUCT_CATEGORY_ORDER = (
    "Sunscreens",
    "Moisturizers",
    "Cleansers",
    "Retinoids",
    "Vitamin C serums",
    "Azelaic acid",
    "Peptide serums",
)

# The People directory is grouped by credential type (their `expertise` field).
# "Influencers & educators" is the NON-credentialed tier (not a derm/chemist): their
# claims are treated skeptically - used only when they align with the evidence, product
# recommendations are suspect (affiliate/sponsor conflicts), and their credential is
# always labeled honestly. TODO: split out a "Licensed estheticians" group later.
PEOPLE_EXPERTISE_ORDER = (
    "Dermatologists",
    "Cosmetic chemists",
    "Licensed estheticians",
    "Influencers & educators",
)


def grouped_by_category(metadatas, order, key="category"):
    """Group metadata dicts into [{label, items}] by their `key` field (default
    `category`), following `order`; unknown/missing values collect under
    "Other". Empty groups are omitted. Within a group, original (alphabetical
    by slug) order is preserved."""
    buckets = {label: [] for label in order}
    other = []
    for m in metadatas:
        label = m.get(key)
        (buckets[label] if label in buckets else other).append(m)
    groups = [types.SimpleNamespace(label=label, items=buckets[label])
              for label in order if buckets[label]]
    if other:
        groups.append(types.SimpleNamespace(label="Other", items=other))
    return groups

# --- Auto cross-references ------------------------------------------------
# Every page lists the published pages that [[link]] to it, grouped by type, so
# the link runs both ways with zero manual upkeep: a product that links to an
# ingredient automatically appears under "Referenced by" on that ingredient's
# page, and likewise for studies, conditions, people, and every other type.
TYPE_LABEL = {typ: label for typ, _filename, label in LISTINGS}
TYPE_LABEL.setdefault("brand", "Brands")
TYPE_LABEL.setdefault("person", "People")
# Order the "Referenced by" groups: concrete products first, then the actives and
# hubs, then the corpus pages.
BACKREF_ORDER = ("product", "ingredient", "goal", "condition", "study", "list", "brand", "person")


# "At a glance" tier navigation: a page with 2+ "## Tier N:" headings gets a
# compact click-down summary of its tiers at the top, so a reader can see the
# whole ranking and jump to any tier. Built from the rendered heading ids so the
# anchors always match the toc-generated ones.
_TIER_H2 = re.compile(r'<h2 id="(tier-[^"]+)"[^>]*>(.*?)</h2>', re.I | re.S)
_TIER_LABEL = re.compile(r"^\s*Tier\s+(\d+)\s*[:.\-]\s*(.*)$", re.I)


def tier_nav_from_html(body_html):
    """List of {href, num, label} for each '## Tier ...' heading; empty if under 2.
    'Tier 1: The Foundation' -> num '1', label 'The Foundation'."""
    items = []
    for m in _TIER_H2.finditer(body_html):
        full = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        lm = _TIER_LABEL.match(full)
        items.append({"href": "#" + m.group(1),
                      "num": lm.group(1) if lm else "",
                      "label": lm.group(2) if lm else full})
    return items if len(items) >= 2 else []


# --- Sunscreen UV-filter coverage infographic --------------------------------
# A static SVG spectrum (290 to 400 nm) showing the approximate UV range each
# common filter protects against, against the UVB / UVA-II / UVA-I bands and the
# 370 nm broad-spectrum threshold. Ranges are approximate protective ranges from
# each filter's standard classification (mineral/bemotrizinol-class = broad;
# avobenzone = UVA; salicylates/cinnamate = UVB; octocrylene = UVB + partial
# UVA-II), consistent with the sourced bands on sunscreen-uv-filters. Rendered
# in place of the <!--uv-filter-spectrum--> marker.
UV_FILTERS = [  # (slug, display name, start nm, end nm)
    ("zinc-oxide", "Zinc oxide", 290, 400),
    ("bisoctrizole", "Bisoctrizole", 290, 400),
    ("avobenzone", "Avobenzone", 320, 400),
    ("octocrylene", "Octocrylene", 290, 340),
    ("octinoxate", "Octinoxate", 290, 320),
    ("octisalate", "Octisalate", 290, 320),
    ("homosalate", "Homosalate", 290, 320),
    ("ethylhexyl-triazone", "Ethylhexyl triazone", 290, 320),
]
_UV_MARKER = "<!--uv-filter-spectrum-->"
_UV_SLUGS = {f[0] for f in UV_FILTERS}


def product_uv_filters(content):
    """The UV_FILTERS entries a body references via [[xref]], in UV_FILTERS
    order. Used to render a per-sunscreen coverage chart from the filters the
    product's own page actually names."""
    refs = set()
    for m in sklib._XREF_RE.finditer(content):
        refs.add(m.group(1).split("#")[0].split("|")[0].strip())
    return [f for f in UV_FILTERS if f[0] in refs]


def render_uv_spectrum(filters=UV_FILTERS):
    nm0, nm1, L, R = 290, 400, 152, 700
    top, row_h = 48, 22
    plot_h = len(filters) * row_h
    h = top + plot_h + 20

    def x(nm):
        return L + (nm - nm0) / (nm1 - nm0) * (R - L)

    p = [f'<svg class="uv-spectrum" viewBox="0 0 720 {h}" role="img" '
         f'aria-label="Approximate UV wavelengths each sunscreen filter covers">']
    for cls, a, b, lbl in (("uvb", 290, 320, "UVB"), ("uva2", 320, 340, "UVA II"),
                           ("uva1", 340, 400, "UVA I")):
        p.append(f'<rect class="uv-band uv-band-{cls}" x="{x(a):.1f}" y="{top}" '
                 f'width="{x(b)-x(a):.1f}" height="{plot_h}"/>')
        p.append(f'<text class="uv-bandlabel" x="{(x(a)+x(b))/2:.1f}" y="14" '
                 f'text-anchor="middle">{lbl}</text>')
    for nm in (290, 320, 340, 400):
        p.append(f'<text class="uv-tick" x="{x(nm):.1f}" y="34" text-anchor="middle">{nm}</text>')
    p.append(f'<line class="uv-broad" x1="{x(370):.1f}" y1="{top-4}" '
             f'x2="{x(370):.1f}" y2="{top+plot_h}"/>')
    p.append(f'<text class="uv-broadlabel" x="{x(370):.1f}" y="{top+plot_h+14}" '
             f'text-anchor="middle">broad-spectrum line (370 nm)</text>')
    for i, (slug, name, a, b) in enumerate(filters):
        y = top + i * row_h
        p.append(f'<a href="{slug}.html"><text class="uv-label" x="{L-8}" '
                 f'y="{y+row_h/2+3:.1f}" text-anchor="end">{name}</text></a>')
        p.append(f'<rect class="uv-bar" x="{x(a):.1f}" y="{y+4:.1f}" '
                 f'width="{x(b)-x(a):.1f}" height="{row_h-8}" rx="2"/>')
    p.append("</svg>")
    return "".join(p)


def reverse_xref_index(profiles):
    """Map each slug -> list of profiles whose body [[links]] to it (self excluded).

    Uses the same xref regex the renderer uses; a `[[slug#anchor]]` or
    `[[slug|label]]` target counts as a reference to `slug`."""
    idx = {}
    for p in profiles:
        targets = set()
        for m in sklib._XREF_RE.finditer(p.content):
            target = m.group(1).split("#")[0].strip()
            if target:
                targets.add(target)
        for target in targets:
            if target != p.get("slug"):
                idx.setdefault(target, []).append(p)
    return idx


def backref_groups_for(slug, rev_index):
    """The 'Referenced by' groups for one page: PUBLISHED referencing pages only
    (transient stubs/drafts are not surfaced), grouped by type in BACKREF_ORDER
    and sorted by name within a group."""
    refs = [r for r in rev_index.get(slug, []) if r.get("status") == "published"]
    by_type = {}
    for r in refs:
        by_type.setdefault(r.get("type"), []).append(r.metadata)
    groups = []
    for typ in BACKREF_ORDER:
        items = sorted(by_type.get(typ, []), key=lambda m: (m.get("name") or "").lower())
        if items:
            groups.append(types.SimpleNamespace(
                type_label=TYPE_LABEL.get(typ, typ.title() + "s"), items=items))
    return groups


# type -> listing page filename (for the profile kicker link).
TYPE_HREF = {typ: f"{filename}.html" for typ, filename, _ in LISTINGS}

# effect word -> filled segments out of 4.
EFFECT_SEGS = {"none": 0, "minimal": 1, "modest": 2, "notable": 3, "strong": 4}
# evidence word -> (css class, display label).
EVIDENCE_MAP = {
    "anecdotal": ("ev-anec", "Anecdotal"),
    "preliminary": ("ev-prelim", "Preliminary"),
    "mixed": ("ev-mixed", "Mixed"),
    "solid": ("ev-solid", "Solid"),
    "gold-standard": ("ev-gold", "Gold-standard"),
}

_LEADING_P_RE = re.compile(r"\s*<p>(.*?)</p>(.*)", re.DOTALL)
_SOURCES_RE = re.compile(r"<h2[^>]*>Sources</h2>", re.IGNORECASE)


def split_standfirst(body_html):
    """Split rendered body into (standfirst_inner, body_rest).

    standfirst is the inner HTML of the leading <p>; body_rest is everything
    after it. If the body does not start with <p>, standfirst is "" and
    body_rest is the whole body.
    """
    m = _LEADING_P_RE.match(body_html)
    if not m:
        return "", body_html
    return m.group(1).strip(), m.group(2).lstrip()


def split_sources(body_rest):
    """Split off the trailing Sources block (its <h2> plus python-markdown's
    footnote list) so it can render last, after recommended_in and tagged.

    Returns (body_main, sources_html). If there is no Sources heading,
    sources_html is "" and body_main is the whole input.
    """
    m = _SOURCES_RE.search(body_rest)
    if not m:
        return body_rest, ""
    return body_rest[:m.start()].rstrip(), body_rest[m.start():].strip()


# A video card embeds the video where the platform allows (the static site permits
# third-party iframes/scripts). YouTube -> responsive iframe; TikTok -> blockquote
# embed (needs tiktok's embed.js, included once per page). Anything else -> no
# embed, the link-out in the card stands.
_YT_EMBED = re.compile(r"(?:youtube\.com/(?:watch\?v=|shorts/|embed/)|youtu\.be/)([A-Za-z0-9_-]{11})")
_TT_EMBED = re.compile(r"tiktok\.com/.+?/video/(\d+)")


def video_embed(url):
    """Return {kind, id, src|cite} for an embeddable video URL, or None."""
    if not url:
        return None
    m = _YT_EMBED.search(url)
    if m:
        return {"kind": "youtube", "id": m.group(1),
                "src": f"https://www.youtube.com/embed/{m.group(1)}"}
    m = _TT_EMBED.search(url)
    if m:
        return {"kind": "tiktok", "id": m.group(1), "cite": url}
    return None


def grades_view_for(metadata):
    """Build the dossier view rows from a `grades:` frontmatter list."""
    view = []
    for g in metadata.get("grades") or []:
        effect = (g.get("effect") or "").lower()
        evidence = (g.get("evidence") or "").lower()
        ev_class, ev_label = EVIDENCE_MAP.get(evidence, ("ev-anec", evidence.title()))
        view.append({
            "use": g.get("use", ""),
            "note": g.get("note", ""),
            "effect_word": effect,
            "effect_segs": EFFECT_SEGS.get(effect, 0),
            "evidence_class": ev_class,
            "evidence_label": ev_label,
        })
    return view


# --- Routine dashboards ---------------------------------------------------
# A `list` of `kind: routine` carries an ordered `steps:` list in frontmatter:
#   steps:
#     - when: AM            # AM or PM
#       product: <slug>     # a product page on the site
#       role: Cleanser      # short label for the step
#       note: optional one-liner
# From those product slugs build.py rolls up an at-a-glance summary computed
# from each product's own `grades:` and [[xref]] links, so the dashboard stays
# in sync automatically as the underlying product pages change. The same
# summary is also emitted to _site/routines.json for a future client-side
# (JavaScript) renderer; the page itself renders the baked HTML with no JS.

# Coarse tiers for the distribution bar, from a product's best HEALTH effect.
_ROUTINE_TIERS = (
    ("top", "Top-tier", {"notable", "strong"}),
    ("mid", "Moderate", {"modest"}),
    ("entry", "Entry", {"minimal", "none"}),
)

# Really-common, household-name actives, each satisfied by any of a family of
# ingredient slugs. Used to state plainly which of these a routine does not
# contain. Kept deliberately short (only ingredients a general reader would
# recognize and might look for) so the line stays neutral, not a checklist.
_NOTABLE_ACTIVES = (
    ("Retinoid", {"retinol", "retinaldehyde", "adapalene", "tretinoin",
                  "retinyl-esters", "retinyl-retinoate", "bakuchiol"}),
    ("Vitamin C", {"ascorbic-acid-vitamin-c", "vitamin-c"}),
    ("Niacinamide", {"niacinamide"}),
    ("Exfoliant", {"salicylic-acid", "glycolic-acid", "lactic-acid", "mandelic-acid"}),
)


def _top_health_effect(metadata):
    """A product's best effect word among its HEALTH-labeled grades (falling
    back to all grades if none are health-labeled); "" if it has no grades."""
    grades = metadata.get("grades") or []
    health = [g for g in grades if "(health)" in (g.get("use") or "").lower()]
    pool = health or grades
    best_word, best_segs = "", -1
    for g in pool:
        word = (g.get("effect") or "").lower()
        segs = EFFECT_SEGS.get(word, 0)
        if segs > best_segs:
            best_word, best_segs = word, segs
    return best_word


def routine_summary(profile, by_slug):
    """Build the at-a-glance dashboard model for a routine list, or None if the
    profile is not a routine with steps. Reads each step's product frontmatter
    for grades (tier distribution) and body xrefs (ingredient union, conditions
    /goals served). Unknown product slugs are skipped so a routine never breaks
    the build; they are surfaced via the returned `missing` list."""
    if profile.get("type") != "list" or profile.get("kind") != "routine":
        return None
    steps = profile.metadata.get("steps")
    if not steps:
        return None
    phases = {"AM": [], "PM": []}
    products, missing = [], []
    for step in steps:
        slug = (step.get("product") or "").strip()
        prod = by_slug.get(slug)
        if prod is None:
            missing.append(slug)
            continue
        if prod not in products:
            products.append(prod)
        effect = _top_health_effect(prod.metadata)
        # Standardized product badge: the product's first photo (cropped to a
        # fixed square by the template's object-fit) inside a tier-colored frame,
        # with a monogram fallback when the product has no photo.
        imgs, mono = images_and_monogram(prod.metadata)
        tier_key = next((k for k, _l, words in _ROUTINE_TIERS if effect in words), "entry")
        row = {
            "slug": slug,
            "name": prod.metadata.get("name") or slug,
            "role": step.get("role") or prod.metadata.get("category") or "",
            "note": step.get("note") or "",
            "effect_word": effect,
            "effect_segs": EFFECT_SEGS.get(effect, 0),
            "tier_key": tier_key,
            "thumb": imgs[0]["src"] if imgs else None,
            "monogram": mono,
            "published": prod.get("status") == "published",
        }
        phases.get((step.get("when") or "AM").upper().strip(), phases["AM"]).append(row)

    tier_counts = {key: 0 for key, _label, _words in _ROUTINE_TIERS}
    seg_values = []
    for prod in products:
        word = _top_health_effect(prod.metadata)
        seg_values.append(EFFECT_SEGS.get(word, 0))
        for key, _label, words in _ROUTINE_TIERS:
            if word in words:
                tier_counts[key] += 1
                break
    tiers = [{"key": key, "label": label, "count": tier_counts[key]}
             for key, label, _words in _ROUTINE_TIERS]

    # A single "how well it works" read: the mean of the products' best HEALTH
    # effect (0 to 4), mapped to a plain word. It is a summary of the graded
    # products, not a trial of the routine, and is labeled that way on the page.
    mean_seg = sum(seg_values) / len(seg_values) if seg_values else 0
    for cutoff, word in ((3.0, "Strong"), (2.25, "Solid"), (1.5, "Moderate"), (0, "Light")):
        if mean_seg >= cutoff:
            strength_label = word
            break
    strength = {"label": strength_label, "segs": round(mean_seg), "mean": round(mean_seg, 2)}

    # Active ingredients "as a whole": each product's declared `key_actives:`
    # (author-declared, so base emollients and comparators do not leak in). We
    # COUNT how many distinct products in the routine carry each active, so a
    # layered ingredient shows as "x2", "x3" etc.; a product with no key_actives
    # contributes nothing.
    ing_count, ing_name = {}, {}
    for prod in products:
        for slug in prod.metadata.get("key_actives") or []:
            t = by_slug.get(slug)
            if t is None:
                continue
            ing_count[slug] = ing_count.get(slug, 0) + 1
            ing_name[slug] = t.metadata.get("name") or slug

    # Sunscreen filters are grouped into one chip labeled by UVB/UVA coverage,
    # because most readers do not recognize filter names (bisoctrizole, etc.).
    uv_map = {f[0]: (f[1], f[2], f[3]) for f in UV_FILTERS}
    filter_slugs = [s for s in ing_count if s in uv_map]
    filters = None
    if filter_slugs:
        covers_uvb = any(uv_map[s][1] < 320 for s in filter_slugs)   # any range into UVB (<320 nm)
        covers_uva = any(uv_map[s][2] > 320 for s in filter_slugs)   # any range into UVA (>320 nm)
        bands = [b for b, on in (("UVB", covers_uvb), ("UVA", covers_uva)) if on]
        fset = set(filter_slugs)
        entries = [{"slug": f[0], "name": f[1]} for f in UV_FILTERS if f[0] in fset]
        filters = {"coverage": " + ".join(bands) or "UV", "entries": entries}

    # Non-filter actives only, most-layered first then alphabetical.
    ingredients = sorted(
        ({"slug": s, "name": ing_name[s], "count": ing_count[s]}
         for s in ing_count if s not in uv_map),
        key=lambda d: (-d["count"], d["name"].lower()))

    # Notable actives the routine does NOT include (informational, not a flaw).
    present = set(ing_count)
    absent = [label for label, members in _NOTABLE_ACTIVES if not (members & present)]

    # Conditions/goals the routine is for: declared on the routine's own `for:`
    # frontmatter (a routine targets a concern as a whole, so this is a property
    # of the routine, not something to infer from its products' links).
    serves = []
    for slug in profile.metadata.get("for") or []:
        t = by_slug.get(slug)
        if t is not None:
            serves.append({"slug": slug, "name": t.metadata.get("name") or slug,
                           "type_label": TYPE_LABEL.get(t.get("type"), (t.get("type") or "").title())})

    return {
        "am": phases["AM"], "pm": phases["PM"],
        "product_count": len(products),
        "top_tier_count": tier_counts["top"],
        "strength": strength,
        "tiers": tiers,
        "ingredients": ingredients,
        "filters": filters,
        "absent": absent,
        "serves": serves,
        "missing": missing,
    }


def routine_catalog(profiles, by_slug, code_map):
    """A hyper-compact, code-keyed catalog the browser routine builder loads once,
    so any routine string (r1.a04...) resolves entirely client-side. Carries only
    what the live dashboard needs - the same signals routine_summary() computes:
    tier, effect strength, key actives, sunscreen filter bands, badge art.

    Short keys keep it small: p[code]={s slug, n name, c category, t tier_key,
    g effect_segs 0-4, a [active slugs], th thumb, m monogram}; i[active]={n name,
    f filter band}; notable=[[label,[member slugs]]] for the "does not contain" line.
    Only PUBLISHED products are included (the pickable, resolvable set)."""
    uv_map = {f[0]: (f[1], f[2], f[3]) for f in UV_FILTERS}
    prods, ings = {}, {}
    for p in profiles:
        if p.get("type") != "product" or p.get("status") != "published":
            continue
        code = code_map.get(p["slug"])
        if not code:
            continue
        imgs, mono = images_and_monogram(p.metadata)
        effect = _top_health_effect(p.metadata)
        tier_key = next((k for k, _l, words in _ROUTINE_TIERS if effect in words), "entry")
        actives = []
        for slug in p.metadata.get("key_actives") or []:
            if by_slug.get(slug) is None:
                continue
            actives.append(slug)
            if slug not in ings:
                meta = {"n": by_slug[slug].metadata.get("name") or slug}
                if slug in uv_map:
                    _n, lo, hi = uv_map[slug]
                    meta["f"] = ("both" if lo < 320 and hi > 320
                                 else "uvb" if lo < 320 else "uva")
                ings[slug] = meta
        prods[code] = {"s": p["slug"], "n": p.metadata.get("name") or p["slug"],
                       "c": p.metadata.get("category") or "", "t": tier_key,
                       "g": EFFECT_SEGS.get(effect, 0), "a": actives,
                       "th": imgs[0]["src"] if imgs else None, "m": mono}
    notable = [[label, sorted(members)] for label, members in _NOTABLE_ACTIVES]
    return {"v": routine_string.VERSION, "p": prods, "i": ings, "notable": notable}


def _resolve_image(val):
    """A URL is used as-is; a bare filename resolves to images/<file>."""
    return val if re.match(r"^https?://", val) else f"images/{val}"


def images_and_monogram(metadata):
    """Return (images, monogram) for a profile.

    `images:` (a list) is preferred; `image:` (single) is accepted for
    back-compat. Each entry is normalized to a dict with `src` (resolved),
    `source` (the site/retailer the photo is from, or None), `source_url`
    (link to that site, or None), and `alt`. Entries may be:
      - a bare string (filename or URL): source unknown.
      - a mapping with `file:` or `url:` (or `src:`), plus optional `source:`,
        `source_url:`, `alt:`.
    The gallery section renders one figure per image, captioned with its source
    so a page can carry several product photos from different sites. Returns an
    empty list when none are set (the page then shows no gallery).
    """
    raw = metadata.get("images")
    if not raw:
        one = metadata.get("image")
        raw = [one] if one else []
    name = metadata.get("name")
    images = []
    for v in raw:
        if not v:
            continue
        if isinstance(v, dict):
            f = v.get("file") or v.get("url") or v.get("src")
            if not f:
                continue
            images.append({"src": _resolve_image(f), "source": v.get("source"),
                           "source_url": v.get("source_url"),
                           "alt": v.get("alt") or name})
        else:
            images.append({"src": _resolve_image(v), "source": None,
                           "source_url": None, "alt": name})
    words = (name or "").split()
    monogram = "".join(w[0] for w in words[:2] if w).upper()
    return images, monogram


def gen_icon(seed, monogram="", label=None):
    """A deterministic inline-SVG tile for entities with no photo: a two-stop
    gradient whose hue is derived from the slug, with the monogram centered. Same
    seed -> same icon, everywhere. The gradient id is hashed so many can share a page."""
    h = hashlib.md5((seed or "").encode("utf-8")).hexdigest()
    hue = int(h[:2], 16) * 360 // 256
    hue2 = (hue + 40) % 360
    gid = "gi" + h[:8]
    mono = _htmllib.escape((monogram or "")[:2])
    aria = _htmllib.escape(label or seed or "")
    return (
        f'<svg class="genicon" viewBox="0 0 64 64" role="img" aria-label="{aria}" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="hsl({hue} 58% 56%)"/>'
        f'<stop offset="1" stop-color="hsl({hue2} 62% 44%)"/></linearGradient></defs>'
        f'<rect width="64" height="64" rx="13" fill="url(#{gid})"/>'
        f'<text x="32" y="35" text-anchor="middle" dominant-baseline="central" '
        f'font-family="IBM Plex Mono, monospace" font-weight="600" font-size="26" '
        f'fill="#fff">{mono}</text></svg>')

# Stable order + plural labels for the auto "tagged pages" groups.
TAG_GROUP_ORDER = (
    ("product", "Products"),
    ("ingredient", "Ingredients"),
    ("condition", "Conditions"),
    ("goal", "Goals"),
)


def tagged_groups_for(profile, tag_index):
    """Group pages tagged with `profile.slug` by entity type (stable order).

    Only condition/goal profiles get groups; everything else gets []."""
    if profile.get("type") not in ("condition", "goal"):
        return []
    tagged = tag_index.get(profile["slug"], [])
    groups = []
    for typ, label in TAG_GROUP_ORDER:
        items = [{"slug": p["slug"], "name": p["name"]}
                 for p in tagged if p.get("type") == typ]
        if items:
            # SimpleNamespace so the template's `g.items` resolves to this list
            # rather than dict.items (Jinja prefers attribute over key lookup).
            groups.append(types.SimpleNamespace(type_label=label, items=items))
    return groups


MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")


def _date_label(iso):
    """'2026-07-28' -> 'July 28, 2026'; pass through anything unparseable."""
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", str(iso))
    if not m:
        return str(iso)
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return f"{MONTHS[mo - 1]} {d}, {y}" if 1 <= mo <= 12 else str(iso)


def changelog_groups_for(path, published):
    """Read data/changelog.yaml (a flat, newest-first list of {date, title, slug?})
    and group consecutive entries by date for rendering. A slug that names a
    published profile becomes a link; anything else renders as plain text."""
    import yaml
    if not path.exists():
        return []
    entries = yaml.safe_load(path.read_text()) or []
    groups, cur = [], None
    for e in entries:
        if not isinstance(e, dict) or not e.get("title"):
            continue
        date = str(e.get("date", ""))
        slug = e.get("slug")
        href = f"{slug}.html" if slug and slug in published else None
        item = {"title": e["title"], "href": href}
        if cur is None or cur["date"] != date:
            cur = {"date": date, "date_label": _date_label(date), "entries": [item]}
            groups.append(cur)
        else:
            cur["entries"].append(item)
    return groups


# --- Syndication feeds (freshness) -------------------------------------------
# The changelog becomes a real RSS 2.0 + JSON Feed of recently added/updated pages,
# so the site's freshness is subscribable and machine-readable. Static, no deps.
SITE_URL = "https://ericries.github.io/skintiers"
FEED_TITLE = "SkinTiers - What's New"
FEED_DESC = "Recently added and updated pages on SkinTiers, a skeptical, evidence-first skincare directory."
FEED_LIMIT = 50


def _feed_items(entries, published):
    """Normalize newest-first changelog entries to feed items (capped at FEED_LIMIT).
    A slug that names an existing page links to it; otherwise the item points at the
    What's New page. Each id is stable per (date, title) so readers don't re-notify."""
    items = []
    for e in entries:
        if not isinstance(e, dict) or not e.get("title"):
            continue
        title, date, slug = str(e["title"]), str(e.get("date", "")), e.get("slug")
        url = f"{SITE_URL}/{slug}.html" if slug and slug in published else f"{SITE_URL}/whats-new.html"
        uid = f"{SITE_URL}/#{date}-{hashlib.sha1(title.encode('utf-8')).hexdigest()[:12]}"
        items.append({"title": title, "date": date, "url": url, "id": uid})
        if len(items) >= FEED_LIMIT:
            break
    return items


def _rfc822(date_str):
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 +0000")
    except ValueError:
        return ""


def render_rss(entries, published):
    """RSS 2.0 XML string of the recent changelog."""
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0"><channel>',
           f"<title>{_htmllib.escape(FEED_TITLE)}</title>", f"<link>{SITE_URL}/</link>",
           f"<description>{_htmllib.escape(FEED_DESC)}</description>",
           f'<atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>']
    for it in _feed_items(entries, published):
        out.append("<item>")
        out.append(f"<title>{_htmllib.escape(it['title'])}</title>")
        out.append(f"<link>{it['url']}</link>")
        out.append(f'<guid isPermaLink="false">{it["id"]}</guid>')
        pd = _rfc822(it["date"])
        if pd:
            out.append(f"<pubDate>{pd}</pubDate>")
        out.append("</item>")
    out.append("</channel></rss>")
    return "".join(out)


def render_json_feed(entries, published):
    """JSON Feed 1.1 string of the recent changelog."""
    feed = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": FEED_TITLE, "home_page_url": f"{SITE_URL}/",
        "feed_url": f"{SITE_URL}/feed.json", "description": FEED_DESC,
        "items": [
            {"id": it["id"], "url": it["url"], "title": it["title"],
             **({"date_published": f"{it['date']}T00:00:00Z"} if it["date"] else {})}
            for it in _feed_items(entries, published)
        ],
    }
    return json.dumps(feed, ensure_ascii=False, indent=2)


ASSURANCE_TIPS = {
    "stub": "Placeholder page, not yet fully researched.",
    "sonnet": "Drafted and auto-checked (lint, sources, style), single pass.",
    "opus": "Independently verified: every cited source re-fetched, quotes and statistics checked.",
    "reviewed": "Read and signed off by a human editor.",
}


def build():
    env = Environment(loader=FileSystemLoader(str(sklib.TEMPLATES_DIR)), autoescape=True)
    env.globals["assurance_tip"] = lambda level: ASSURANCE_TIPS.get(level, "")
    env.globals["video_embed"] = video_embed
    env.globals["gen_icon"] = gen_icon
    out = sklib.OUTPUT_DIR
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    # Render EVERY status (stubs/drafts included) so cross-links always resolve; each is badged.
    profiles = sklib.load_profiles(sklib.DATA_DIR)
    slugs = {p["slug"] for p in profiles}
    names = {p["slug"]: p["name"] for p in profiles}
    tag_index = sklib.build_tag_index(profiles)
    rev_index = reverse_xref_index(profiles)
    by_slug = {p["slug"]: p for p in profiles}
    routines_json = {}

    # Assign each product a stable base62 code (append-only registry), for the
    # compact routine-string URLs the browser builder reads/writes.
    code_map = product_codes.sync(
        [p["slug"] for p in profiles if p.get("type") == "product"],
        registry=sklib.DATA_DIR / "routine-codes.yaml")

    # Reverse index of the expert-video cards across the site, keyed by the
    # creator's person slug, so each expert's page can summarise what we have
    # verified from them (only videos cited on PUBLISHED pages are surfaced).
    creator_videos = {}
    for p in profiles:
        if p.get("status") != "published":
            continue
        for v in p.metadata.get("videos") or []:
            cs = v.get("creator_slug")
            if cs:
                creator_videos.setdefault(cs, []).append(
                    {**v, "on_slug": p["slug"], "on_name": p.metadata.get("name")})

    for p in profiles:
        linked = sklib.linkify_xrefs(p.content, slugs, names)
        body = sklib.render_markdown(linked)
        standfirst, body_rest = split_standfirst(body)
        body_main, sources_html = split_sources(body_rest)
        if _UV_MARKER in body_main:
            body_main = body_main.replace(_UV_MARKER, render_uv_spectrum())
        images, monogram = images_and_monogram(p.metadata)
        # Per-sunscreen UV-filter coverage chart: only for Sunscreen products
        # that name at least one known filter on their page.
        uv_spectrum = None
        if p.get("type") == "product" and p.metadata.get("category") == "Sunscreens":
            fils = product_uv_filters(p.content)
            if fils:
                uv_spectrum = render_uv_spectrum(fils)
        routine = routine_summary(p, by_slug)
        if routine is not None:
            routines_json[p["slug"]] = {
                "name": p.metadata.get("name"),
                "product_count": routine["product_count"],
                "top_tier_count": routine["top_tier_count"],
                "strength": routine["strength"],
                "tiers": {t["key"]: t["count"] for t in routine["tiers"]},
                "ingredients": {i["slug"]: i["count"] for i in routine["ingredients"]},
                "ingredient_slugs": [i["slug"] for i in routine["ingredients"]],
                "filters": routine["filters"],
                "absent": routine["absent"],
                "serves_slugs": [s["slug"] for s in routine["serves"]],
            }
        cvids = creator_videos.get(p["slug"], []) if p.get("type") == "person" else []
        html = env.get_template("profile.html").render(
            profile=p.metadata,
            standfirst=standfirst,
            body_main=body_main,
            sources_html=sources_html,
            comparator=p.get("comparator") or "others in its category",
            grades_view=grades_view_for(p.metadata),
            recommended_in=p.get("recommended_in") or [],
            images=images,
            monogram=monogram,
            type_href=TYPE_HREF.get(p.get("type"), "index.html"),
            tagged_groups=tagged_groups_for(p, tag_index),
            backref_groups=backref_groups_for(p["slug"], rev_index),
            tier_nav=tier_nav_from_html(body_main),
            routine=routine,
            uv_spectrum=uv_spectrum,
            videos=p.metadata.get("videos") or [],
            creator_videos=cvids,
            needs_tiktok_js=any((video_embed(v.get("url")) or {}).get("kind") == "tiktok"
                                for v in (p.metadata.get("videos") or []) + cvids))
        (out / f"{p['slug']}.html").write_text(html)

    # Baked routine rollups for a future client-side renderer (the pages
    # themselves render static HTML and need no JS).
    (out / "routines.json").write_text(json.dumps(routines_json, indent=2, sort_keys=True))

    # Code-keyed product catalog for the routine builder (resolves routine-string
    # URLs entirely client-side). Minified - it is machine-loaded, not read.
    catalog = routine_catalog(profiles, by_slug, code_map)
    (out / "routine-catalog.json").write_text(json.dumps(catalog, separators=(",", ":")))

    # Routines index: surfaces the dashboards (routines otherwise live under Lists).
    _STRENGTH_KEY = {"Strong": "strong", "Solid": "solid", "Moderate": "moderate", "Light": "light"}
    routine_cards = []
    for p in profiles:
        if p.get("status") != "published" or p["slug"] not in routines_json:
            continue
        rj = routines_json[p["slug"]]
        _, mono = images_and_monogram(p.metadata)
        routine_cards.append({
            "slug": p["slug"], "name": rj["name"] or p["slug"], "monogram": mono,
            "strength": rj["strength"]["label"],
            "strength_key": _STRENGTH_KEY.get(rj["strength"]["label"], "light"),
            "product_count": rj["product_count"],
            "coverage": (rj["filters"] or {}).get("coverage") if rj["filters"] else None,
            "serves": [names.get(s, s) for s in rj["serves_slugs"]],
            "absent": rj["absent"],
        })
    routine_cards.sort(key=lambda c: c["name"].lower())
    (out / "routines.html").write_text(
        env.get_template("routines_index.html").render(routines=routine_cards))

    # Listing pages are always built for every category; only the index nav is
    # filtered to categories with at least one PUBLISHED profile.
    nav_categories = []
    for typ, filename, label in LISTINGS:
        of_type = [p for p in profiles if p.get("type") == typ]
        items = [p.metadata for p in of_type]
        published_count = sum(1 for p in of_type if p.get("status") == "published")
        # Products group by category and People by credential type; the other
        # listings stay flat.
        if typ == "product":
            groups = grouped_by_category(items, PRODUCT_CATEGORY_ORDER)
        elif typ == "person":
            groups = grouped_by_category(items, PEOPLE_EXPERTISE_ORDER, key="expertise")
        else:
            groups = None
        html = env.get_template("listing.html").render(
            heading=label, items=items, groups=groups)
        (out / f"{filename}.html").write_text(html)
        if published_count >= 1:
            nav_categories.append(
                {"label": label, "filename": filename, "count": len(of_type)})

    index = env.get_template("index.html").render(nav_categories=nav_categories)
    (out / "index.html").write_text(index)

    # Standalone Method page (not a data profile).
    method = env.get_template("method.html").render()
    (out / "method.html").write_text(method)

    # What's New: a date-sorted changelog from data/changelog.yaml, grouped by day.
    changelog_groups = changelog_groups_for(sklib.ROOT / "data" / "changelog.yaml",
                                             published=set(slugs))
    whats_new = env.get_template("whats_new.html").render(groups=changelog_groups)
    (out / "whats-new.html").write_text(whats_new)

    # Syndication feeds (RSS + JSON) of the same changelog, for subscribers/monitoring.
    import yaml as _yaml
    _cl = sklib.ROOT / "data" / "changelog.yaml"
    _cl_entries = (_yaml.safe_load(_cl.read_text()) or []) if _cl.exists() else []
    (out / "feed.xml").write_text(render_rss(_cl_entries, set(slugs)))
    (out / "feed.json").write_text(render_json_feed(_cl_entries, set(slugs)))

    if sklib.STATIC_DIR.exists():
        for f in sklib.STATIC_DIR.iterdir():
            if f.is_file():
                shutil.copy(f, out / f.name)
        images = sklib.STATIC_DIR / "images"
        if images.is_dir():
            shutil.copytree(images, out / "images", dirs_exist_ok=True)
    print(f"built {len(profiles)} profiles -> {out}")
    # Ship-live backstop: a committed page the critic cleared ('publish') but that
    # is still status:draft never reaches the site. Warn loudly (in CI logs too) so
    # it can't silently rot. See `sk audit` for the full local check.
    try:
        import yaml
        log_path = sklib.ROOT / "data" / "review-log.yaml"
        review_log = yaml.safe_load(log_path.read_text()) if log_path.exists() else {}
        by_slug = {p.get("slug"): p.get("status") for p in profiles}
        stuck = [s for s, e in (review_log or {}).items()
                 if (e or {}).get("verdict") == "publish" and by_slug.get(s) == "draft"]
        if stuck:
            print(f"WARNING: {len(stuck)} page(s) cleared to publish but still draft "
                  f"(run `sk audit`): {', '.join(sorted(stuck))}")
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(build())
