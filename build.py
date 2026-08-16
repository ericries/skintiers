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
import zipfile

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
    "Toners",
    "Retinoids",
    "Exfoliants",
    "Vitamin C serums",
    "Niacinamide serums",
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
    ("bemotrizinol", "Bemotrizinol", 290, 400),
    ("diethylamino-hydroxybenzoyl-hexyl-benzoate", "Diethylamino hydroxybenzoyl hexyl benzoate", 320, 400),
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


def _merge_uv_intervals(filters):
    """Union of the filters' (start, end) nm ranges into sorted, merged segments,
    plus the gaps left uncovered inside 290-400. Lets the chart state plainly which
    wavelengths the whole product does and does not cover."""
    ivals = sorted((a, b) for _, _, a, b in filters)
    covered = []
    for a, b in ivals:
        if covered and a <= covered[-1][1]:
            covered[-1][1] = max(covered[-1][1], b)
        else:
            covered.append([a, b])
    gaps, cur = [], 290
    for a, b in covered:
        if a > cur:
            gaps.append([cur, a])
        cur = max(cur, b)
    if cur < 400:
        gaps.append([cur, 400])
    return covered, gaps


def render_uv_spectrum(filters=UV_FILTERS, combined=False):
    nm0, nm1, L, R = 290, 400, 152, 700
    top, row_h = 48, 22
    n_rows = len(filters) + (1 if combined else 0)
    plot_h = n_rows * row_h
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
    offset = 0
    if combined:
        # Summary row first: the union of every filter, so the reader sees the
        # product's total covered range (and any uncovered gap) at a glance.
        covered, gaps = _merge_uv_intervals(filters)
        y = top
        p.append(f'<text class="uv-label uv-label-combined" x="{L-8}" '
                 f'y="{y+row_h/2+3:.1f}" text-anchor="end">Combined coverage</text>')
        for a, b in covered:
            p.append(f'<rect class="uv-bar uv-bar-combined" x="{x(a):.1f}" y="{y+4:.1f}" '
                     f'width="{x(b)-x(a):.1f}" height="{row_h-8}" rx="2"/>')
        for a, b in gaps:
            p.append(f'<rect class="uv-gap" x="{x(a):.1f}" y="{y+4:.1f}" '
                     f'width="{x(b)-x(a):.1f}" height="{row_h-8}" rx="2"/>')
            p.append(f'<text class="uv-gaplabel" x="{(x(a)+x(b))/2:.1f}" '
                     f'y="{y+row_h/2+3:.1f}" text-anchor="middle">gap</text>')
        p.append(f'<line class="uv-sep" x1="{L-8}" y1="{top+row_h:.1f}" x2="{R}" y2="{top+row_h:.1f}"/>')
        offset = 1
    for i, (slug, name, a, b) in enumerate(filters):
        y = top + (i + offset) * row_h
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


def grades_view_for(metadata, published_slugs=None, slug_to_name=None):
    """Build the dossier view rows from a `grades:` frontmatter list.

    A grade `note` may carry [[xref]] links and inline markdown. When the slug
    maps are supplied, the note is linkified and rendered to inline HTML the same
    way the body is, so its links resolve (a missing target renders as plain text,
    never raw `[[brackets]]`). The rendered note is marked safe in the template."""
    published_slugs = published_slugs or frozenset()
    slug_to_name = slug_to_name or {}
    view = []
    for g in metadata.get("grades") or []:
        effect = (g.get("effect") or "").lower()
        evidence = (g.get("evidence") or "").lower()
        ev_class, ev_label = EVIDENCE_MAP.get(evidence, ("ev-anec", evidence.title()))
        note = g.get("note", "")
        if note:
            note = sklib.render_markdown(
                sklib.linkify_xrefs(note, published_slugs, slug_to_name)).strip()
            # The note sits inline in a <small>; strip a single wrapping <p>.
            if note.startswith("<p>") and note.endswith("</p>") and note.count("<p>") == 1:
                note = note[3:-4]
        view.append({
            "use": g.get("use", ""),
            "note": note,
            "effect_word": effect,
            "effect_segs": EFFECT_SEGS.get(effect, 0),
            "evidence_class": ev_class,
            "evidence_label": ev_label,
        })
    return view


def _fmt_amount(amount):
    """Money as it reads on a shelf: no trailing zeros for whole dollars, else cents."""
    if amount == int(amount):
        return f"${int(amount):,}"
    return f"${amount:,.2f}"


def price_view_for(metadata):
    """Rows for the structured Price section from a product's `price:` frontmatter.
    Each entry mirrors a price the page already states (enforced by sklib.check_price_backing),
    so this only formats it; it does not fetch or compute anything."""
    entries = metadata.get("price")
    if not entries or not isinstance(entries, list):
        return []
    view = []
    for e in entries:
        if not isinstance(e, dict) or not isinstance(e.get("amount"), (int, float)):
            continue
        view.append({
            "amount": _fmt_amount(float(e["amount"])),
            "currency": e.get("currency") or "USD",
            "size": e.get("size"),
            "as_of": e.get("as_of"),
        })
    return view


def _derive_primary_active(metadata, published_slugs, rank_index):
    """Pick the product's primary studied active for an auto-derived evidence box.
    Prefers a key_active that sits in a ranked potency list (so the ladder shows),
    else the first key_active with a published ingredient page. None if neither."""
    actives = [str(a).strip() for a in (metadata.get("key_actives") or []) if a]
    for a in actives:
        if a in rank_index:
            return a
    for a in actives:
        if a in published_slugs:
            return a
    return None


def _clean_active_note(text, active_name):
    """Level 01 of the evidence box is composed as '{active_name} is {active_note}',
    so a note authored as a full sentence ('adapalene is a well studied retinoid')
    renders the subject twice: 'Adapalene is adapalene is a well studied retinoid'.
    Strip a redundant leading subject/verb so the note is always a clean predicate,
    regardless of how it was authored. Belt-and-suspenders with clean source notes."""
    if not text:
        return text
    s = text.lstrip()
    name = (active_name or "").strip()
    pats = []
    if name:
        pats += [rf"{re.escape(name)}\s+is\s+", rf"{re.escape(name)}\s*,\s*"]
    pats.append(r"is\s+")
    for pat in pats:
        m = re.match(pat, s, re.I)
        if m:
            return s[m.end():]
    return text


def render_inline(text, published_slugs=None, slug_to_name=None):
    """Linkify [[xrefs]] and render inline markdown to HTML with no wrapping <p>,
    for a short frontmatter phrase shown inline in the template (e.g. the grade
    `comparator`). Without this, a [[slug]] in such a field reaches the reader as raw
    bracket markup — the render bug the smoke test caught on comparator fields."""
    if not text:
        return text
    html = sklib.render_markdown(
        sklib.linkify_xrefs(text, published_slugs or frozenset(), slug_to_name or {})).strip()
    if html.startswith("<p>") and html.endswith("</p>") and html.count("<p>") == 1:
        html = html[3:-4]
    return html


def evidence_levels_view(metadata, published_slugs=None, slug_to_name=None, rank_index=None):
    """Build the three-level evidence model from a product's `evidence_levels:`
    frontmatter, or None if absent. Separates the evidence a reader conflates:
      01 the active/ingredient (reuses the top grade's effect x evidence + links
         the ingredient page), 02 this product as a vehicle (authored, factual),
         03 this exact formula (authored; whether the product itself was tested).
    Levels 02/03 carry no rendered editorial verdict badge on purpose — the notes
    state the facts and the reader judges. Notes may hold [[xrefs]]/markdown."""
    published_slugs = published_slugs or frozenset()
    slug_to_name = slug_to_name or {}
    rank_index = rank_index or {}
    el = metadata.get("evidence_levels")
    derived = False
    if not el:
        # No authored block: auto-derive the scaffold from key_actives so every
        # graded product with a recognized active still renders the box (and its
        # potency ladder) with no per-product authoring. Authored evidence_levels:
        # enriches this with the three prose notes; this is the floor, not a
        # replacement. Requires a resolvable primary active AND grades to badge.
        active = _derive_primary_active(metadata, published_slugs, rank_index)
        if not active or not (grades_view_for(metadata, published_slugs, slug_to_name)):
            return None
        el = {"active": active, "formula_tested": False}
        derived = True

    def note(text):
        if not text:
            return ""
        html = sklib.render_markdown(
            sklib.linkify_xrefs(text, published_slugs, slug_to_name)).strip()
        if html.startswith("<p>") and html.endswith("</p>") and html.count("<p>") == 1:
            html = html[3:-4]
        return html

    active = (el.get("active") or "").strip()
    gv = grades_view_for(metadata, published_slugs, slug_to_name)
    g0 = gv[0] if gv else None
    product_note = note(el.get("product_note"))
    rank = rank_index.get(active)
    # Levels shown: 01 active + 04 formula always; 02 product only when authored;
    # 03 rank only when the active sits in a ranked list. The subtitle counts them.
    nq = 2 + (1 if product_note else 0) + (1 if rank else 0)
    return {
        "active_slug": active,
        "active_name": slug_to_name.get(active, active),
        "active_href": f"{active}.html" if active in published_slugs else None,
        "active_note": note(_clean_active_note(el.get("active_note"), slug_to_name.get(active, active))),
        "effect_word": g0["effect_word"] if g0 else "",
        "effect_segs": g0["effect_segs"] if g0 else 0,
        "evidence_class": g0["evidence_class"] if g0 else "",
        "evidence_label": g0["evidence_label"] if g0 else "",
        "product_note": product_note,
        "formula_note": note(el.get("formula_note")),
        "formula_tested": bool(el.get("formula_tested", False)),
        "rank": rank,
        "derived": derived,
        "nquestions_word": {2: "Two", 3: "Three", 4: "Four"}.get(nq, str(nq)),
    }


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


# --- Evidence tiers (tier lists / rankings) -------------------------------
# One coarse evidence tier per entity, reused by tier-list pages. Products
# derive it from their `grades:`; pages that grade in prose (ingredient hubs)
# carry an explicit summary `tier:` field. Keys match the --tier-* CSS vars.
_TIER_LABELS = (
    ("best", "Top-evidenced"),
    ("good", "Strong"),
    ("mid", "Moderate"),
    ("weak", "Minimal"),
)
_TIER_LABEL_BY_KEY = dict(_TIER_LABELS)
# Accepted manual / page-level tier spellings -> canonical key.
_TIER_ALIASES = {
    "top": "best", "best": "best", "top-evidenced": "best",
    "strong": "good", "good": "good",
    "moderate": "mid", "mid": "mid",
    "minimal": "weak", "weak": "weak",
}
_THIN_EVIDENCE = {"anecdotal", "preliminary"}


def _best_health_grade(metadata):
    """(effect_segs, evidence_word) of the HEALTH grade with the best effect,
    or None if the page has no grades. Mirrors _top_health_effect's health-first
    selection so a tier agrees with the routine dashboards."""
    grades = metadata.get("grades") or []
    if not grades:
        return None
    health = [g for g in grades if "(health)" in (g.get("use") or "").lower()]
    pool = health or grades
    best = None
    for g in pool:
        segs = EFFECT_SEGS.get((g.get("effect") or "").lower(), 0)
        if best is None or segs > best[0]:
            best = (segs, (g.get("evidence") or "").lower())
    return best


def _segs_to_tier(segs):
    if segs >= 4:
        return "best"
    if segs == 3:
        return "good"
    if segs == 2:
        return "mid"
    return "weak"


def entity_tier(metadata):
    """A single evidence tier key for a page, or None (unrated).
    Precedence: explicit page-level `tier:` (e.g. ingredient hubs that grade in
    prose) -> derived from `grades:`, demoting one segment for thin
    (anecdotal/preliminary) evidence -> None."""
    manual = (metadata.get("tier") or "").strip().lower()
    if manual:
        return _TIER_ALIASES.get(manual)          # unknown spelling -> None (unrated)
    best = _best_health_grade(metadata)
    if best is None:
        return None
    segs, evidence = best
    if evidence in _THIN_EVIDENCE:
        segs = max(0, segs - 1)
    return _segs_to_tier(segs)


_TIER_ORDER = ["best", "good", "mid", "weak", "unrated"]


def tier_list_view(profile, by_slug):
    """Build the tier-list render model from a page's `tier_list:` frontmatter,
    or None if absent. Each item is a bare slug or {slug, note?, tier?}. Tier
    precedence per item: its own `tier:` override -> entity_tier(target).
    Unknown/unpublished slugs are skipped and surfaced in `missing`. Within a
    tier, products sort by effect segs desc with declared order breaking ties;
    items with no numeric effect (segs -1, e.g. ingredient hubs) keep declared
    order."""
    tl = profile.metadata.get("tier_list")
    if not tl:
        return None
    # Optional per-list tier labels: `tier_labels:` maps a tier key (canonical
    # best/good/mid/weak/unrated, or an alias spelling like top/strong) to a
    # custom, factual label for THIS list only. Lets an evidence axis that is
    # not "better/worse" (e.g. how much on-skin conversion a form needs) carry
    # descriptive tier names without changing the global defaults.
    label_overrides = {}
    for k, v in (tl.get("tier_labels") or {}).items():
        canon = _TIER_ALIASES.get(str(k).strip().lower(), str(k).strip().lower())
        if v:
            label_overrides[canon] = str(v)
    buckets = {k: [] for k in _TIER_ORDER}
    missing = []
    for idx, raw in enumerate(tl.get("items") or []):
        if isinstance(raw, dict):
            slug = (raw.get("slug") or "").strip()
            note = raw.get("note") or ""
            override = (raw.get("tier") or "").strip().lower()
        else:
            slug, note, override = str(raw).strip(), "", ""
        target = by_slug.get(slug)
        if target is None or target.get("status") != "published":
            missing.append(slug)
            continue
        if override:
            key = _TIER_ALIASES.get(override) or entity_tier(target.metadata) or "unrated"
        else:
            key = entity_tier(target.metadata) or "unrated"
        imgs, mono = images_and_monogram(target.metadata)
        best = _best_health_grade(target.metadata)
        segs = best[0] if best else -1
        ev_label = EVIDENCE_MAP.get(best[1], (None, None))[1] if best else None
        buckets[key].append({
            "slug": slug,
            "name": target.metadata.get("name") or slug,
            "thumb": imgs[0]["src"] if imgs else None,
            "monogram": mono,
            "evidence": ev_label,
            "note": note,
            "order": idx,
            "segs": segs,
        })
    tiers = []
    for key in _TIER_ORDER:
        rows = buckets[key]
        if not rows:
            continue
        rows.sort(key=lambda r: (-r["segs"], r["order"]))
        label = label_overrides.get(key) or _TIER_LABEL_BY_KEY.get(key, "Unrated")
        tiers.append({"key": key, "label": label, "items": rows})
    return {"title": tl.get("title") or "", "by": tl.get("by") or "",
            "caption": tl.get("caption") or "",
            "tiers": tiers, "missing": missing}


def products_for_tier_list(tl_view, profiles):
    """For a condition/goal tier list that ranks ingredient ACTIVES, list the published
    PRODUCTS that contain each active (via key_actives), turning a concern page into a
    concern -> product discovery hub. Each product is placed under the single
    highest-tier active it contains (no duplicates); actives appear best-tier first, and
    products within an active sort by their own evidence tier. Returns None if nothing
    matches (e.g. a tier list that ranks products, not actives)."""
    if not tl_view:
        return None
    rank = {k: i for i, k in enumerate(_TIER_ORDER)}
    active_tier, active_name = {}, {}
    for t in tl_view["tiers"]:
        for it in t["items"]:
            active_tier[it["slug"]] = t["key"]
            active_name[it["slug"]] = it["name"]
    actives = set(active_tier)
    if not actives:
        return None
    groups = {}
    for p in profiles:
        if p.get("type") != "product" or p.get("status") != "published":
            continue
        ka = {str(a).strip().lower() for a in (p.metadata.get("key_actives") or [])}
        matched = ka & actives
        if not matched:
            continue
        best = min(matched, key=lambda a: rank.get(active_tier[a], 99))
        imgs, mono = images_and_monogram(p.metadata)
        ptier = entity_tier(p.metadata) or "unrated"
        pseg = (_best_health_grade(p.metadata) or (-1,))[0]
        groups.setdefault(best, []).append({
            "slug": p["slug"], "name": p.metadata.get("name") or p["slug"],
            "thumb": imgs[0]["src"] if imgs else None, "monogram": mono,
            "ptier": ptier, "pseg": pseg})
    out = []
    for a in sorted(actives, key=lambda a: rank.get(active_tier[a], 99)):
        prods = groups.get(a)
        if not prods:
            continue
        prods.sort(key=lambda r: (rank.get(r["ptier"], 99), -r["pseg"], r["name"].lower()))
        out.append({"active_slug": a, "active_name": active_name[a],
                    "tier_key": active_tier[a], "products": prods[:8],
                    "more": max(0, len(prods) - 8)})
    return {"groups": out} if out else None


def build_potency_rank_index(profiles, by_slug):
    """Map an ingredient slug -> a potency-ladder render model, derived from any
    published best-of `list` whose ranking is by potency/strength. Lets a product
    page answer 'where does this active rank vs. others?' with no hand-authoring,
    staying in sync with the tier list itself."""
    index = {}
    for p in profiles:
        if p.get("type") != "list" or p.get("status") != "published":
            continue
        tl = p.metadata.get("tier_list") or {}
        # A list drives the evidence-box ladder ONLY if it opts in with `ladder: true`.
        # The ladder answers "how strong a TYPE is this active vs. its alternatives",
        # so it only fits lists that rank FORMS of one active family (retinoids,
        # vitamin C forms). A cross-ingredient roundup like "best moisturizing
        # ingredients ranked" must NOT drive it: a product contains many of those at
        # once, so singling out one and ranking it against the rest is meaningless.
        if not tl.get("ladder"):
            continue
        rungs = []
        for raw in tl.get("items") or []:
            if isinstance(raw, dict):
                slug = (raw.get("slug") or "").strip()
                override = (raw.get("tier") or "").strip().lower()
            else:
                slug, override = str(raw).strip(), ""
            tgt = by_slug.get(slug)
            if tgt is None or tgt.get("status") != "published":
                continue
            key = (_TIER_ALIASES.get(override) if override else None) or entity_tier(tgt.metadata) or "unrated"
            rungs.append({"slug": slug, "name": tgt.metadata.get("name") or slug, "tier_key": key})
        if len(rungs) < 2:
            continue
        # Always render the ladder as an ordered gradient (best -> weak), so it reads
        # as a ranking regardless of the list's declared item order; ties keep
        # declared order (stable sort).
        rungs.sort(key=lambda r: _TIER_ORDER.index(r["tier_key"]) if r["tier_key"] in _TIER_ORDER else len(_TIER_ORDER))
        for i, r in enumerate(rungs):
            index[r["slug"]] = {
                "list_slug": p["slug"],
                "list_name": p.metadata.get("name") or p["slug"],
                "list_href": f"{p['slug']}.html",
                "rungs": [{**rr, "here": (j == i)} for j, rr in enumerate(rungs)],
            }
    return index


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


def render_og_image(og_dir, name, title, subtitle):
    """Write a 1200x630 branded share card PNG (og_dir/<name>.png) for rich link
    previews. Uses Pillow's scalable default font (no bundled TTF needed)."""
    import textwrap

    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), (245, 242, 236))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 16], fill=(47, 125, 79))
    d.text((64, 66), "SkinTiers", font=ImageFont.load_default(size=30), fill=(122, 112, 96))
    title_font = ImageFont.load_default(size=62)
    y = 168
    for line in textwrap.wrap(title, width=24)[:4]:
        d.text((64, y), line, font=title_font, fill=(35, 32, 27))
        y += 76
    if subtitle:
        d.text((64, H - 92), subtitle, font=ImageFont.load_default(size=32), fill=(92, 84, 72))
    og_dir.mkdir(parents=True, exist_ok=True)
    img.save(og_dir / f"{name}.png")


def _plain_excerpt(html, limit=200):
    """Plain-text, whitespace-collapsed excerpt of rendered HTML, for og:description /
    meta description. Truncated at `limit` on a word boundary."""
    text = _htmllib.unescape(re.sub(r"<[^>]+>", "", html or ""))
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(" ,;:") + "…"


def routine_builder_path(routine, code_map):
    """The builder URL path (r1/a.../p...) for a curated routine's AM/PM products, so a
    reader can open it in the interactive builder and fork it. Weekly steps are omitted
    (the MVP builder is AM/PM). Returns None if no step maps to a coded product."""
    if not routine:
        return None
    phases = []
    for key, rows in (("am", routine["am"]), ("pm", routine["pm"])):
        items = []
        for row in rows:
            code = code_map.get(row["slug"])
            if code and not any(it["code"] == code for it in items):
                items.append({"code": code, "freq": 7})
        if items:
            phases.append({"key": key, "items": items})
    return routine_string.encode({"phases": phases}) if phases else None


def routine_catalog(profiles, by_slug, code_map):
    """A hyper-compact, code-keyed catalog the browser routine builder loads once,
    so any routine string (r1.a04...) resolves entirely client-side. Carries only
    what the live dashboard needs - the same signals routine_summary() computes:
    tier, effect strength, key actives, sunscreen filter bands, badge art.

    Short keys keep it small: p[code]={s slug, n name, c category, t tier_key,
    g effect_segs 0-4, a [active slugs], th thumb, m monogram}; i[active]={n name,
    f filter band}; notable=[[label,[member slugs]]] for the "does not contain" line.
    PUBLISHED and STUB products are included, to give the builder a broad universe of
    real products to pick from; stubs carry name/brand/category/key_actives (the fill
    crons add grades/evidence later). Draft (mid-research) products are excluded."""
    uv_map = {f[0]: (f[1], f[2], f[3]) for f in UV_FILTERS}
    prods, ings = {}, {}
    for p in profiles:
        if p.get("type") != "product" or p.get("status") not in ("published", "stub"):
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
    return {"v": routine_string.GRAMMAR, "p": prods, "i": ings, "notable": notable}


def _lowest_price(metadata):
    """The lowest structured price for a product, or None. Reads the same `price:`
    frontmatter the product page shows (price_view_for); it only picks the minimum
    amount, it never fetches or invents a number. Returns {amount, size, currency}."""
    entries = metadata.get("price")
    if not entries or not isinstance(entries, list):
        return None
    best = None
    for e in entries:
        if not isinstance(e, dict) or not isinstance(e.get("amount"), (int, float)):
            continue
        amt = float(e["amount"])
        if best is None or amt < best["amount"]:
            best = {"amount": amt, "size": e.get("size"),
                    "currency": e.get("currency") or "USD"}
    return best


def filter_catalog(profiles, by_slug):
    """A flat, readable catalog for the client-side product filter (filter.html): one
    row per PUBLISHED product, carrying only what the filter needs. The evidence
    signals are factored from the SAME helpers the product pages and routine
    dashboards use - _best_health_grade (best HEALTH grade's 0-4 effect strength +
    evidence word), _top_health_effect (its effect word) and _ROUTINE_TIERS (the
    coarse tier key) - so the filter surfaces the site's own grades and never invents
    a ranking. Price is the lowest structured `price:` entry, or null.

    Products with no price are kept (price null; the UI flags them "price not listed"
    and drops them when a max-price filter is active). Draft/stub products are omitted:
    the filter is a buying aid over the graded, published catalog."""
    rows = []
    for p in profiles:
        if p.get("type") != "product" or p.get("status") != "published":
            continue
        meta = p.metadata
        actives = []
        for slug in meta.get("key_actives") or []:
            ing = by_slug.get(slug)
            name = (ing.metadata.get("name") if ing is not None else None) or slug
            actives.append({"slug": slug, "name": name})
        low = _lowest_price(meta)
        best = _best_health_grade(meta)
        effect = _top_health_effect(meta)
        tier = next((k for k, _l, words in _ROUTINE_TIERS if effect in words), None)
        rows.append({
            "slug": p["slug"],
            "url": f"{p['slug']}.html",
            "name": meta.get("name") or p["slug"],
            "brand": meta.get("brand") or "",
            "category": meta.get("category") or "",
            "actives": actives,
            "price": low["amount"] if low else None,
            "price_display": _fmt_amount(low["amount"]) if low else None,
            "price_size": (low.get("size") if low else None),
            "effect": effect,
            "evidence": best[1] if best else "",
            "segs": best[0] if best else 0,
            "tier": tier,
        })
    rows.sort(key=lambda r: r["name"].lower())
    return {"products": rows}


def _resolve_image(val):
    """A URL is used as-is; a bare filename resolves to images/<file>."""
    return val if re.match(r"^https?://", val) else f"images/{val}"


def build_video_feed(profiles):
    """Collect every expert-video card cited on a PUBLISHED page into one feed,
    de-duplicated by video and ordered newest-first by the video's own posting
    date (`posted:` on the card). A video cited on several pages appears once,
    with every page it is cited on listed under `on`. Cards without a resolvable
    `posted:` date sort to the end (never dropped), so the feed is complete even
    when a date could not be fetched.

    Each card also carries `related`: additional pages the video is about but is
    not embedded on, taken from the card's own `related:` slug list (each resolved
    to {slug, name}, published pages only, excluding any page already under `on`).
    So a feed entry links to every page it is appropriate for, not just its home.

    Returns a list of card dicts: each is the card's frontmatter plus
    `on` (list of {slug, name}), `related` (list of {slug, name}), and `posted`.
    """
    slug_to_name = {p["slug"]: (p.metadata.get("name") or p["slug"])
                    for p in profiles if p.get("status") == "published"}
    by_key = {}
    order = []                       # preserve first-seen order for stable ties
    for p in profiles:
        if p.get("status") != "published":
            continue
        for v in p.metadata.get("videos") or []:
            url = v.get("url")
            if not url:
                continue
            emb = video_embed(url) or {}
            key = f"{emb.get('kind')}:{emb.get('id')}" if emb.get("id") else url
            on = {"slug": p["slug"], "name": p.metadata.get("name")}
            rel = {str(s).strip() for s in (v.get("related") or [])}
            if key in by_key:
                # same video on another page - record the extra citation only once
                if not any(o["slug"] == on["slug"] for o in by_key[key]["on"]):
                    by_key[key]["on"].append(on)
                by_key[key]["_rel"] |= rel
            else:
                by_key[key] = {**v, "on": [on], "posted": v.get("posted"), "_rel": rel}
                order.append(key)
    # Resolve each card's related slugs to {slug, name}: published pages only, and
    # never a page the card is already embedded on (that is already in `on`).
    for card in by_key.values():
        on_slugs = {o["slug"] for o in card["on"]}
        card["related"] = [{"slug": s, "name": slug_to_name[s]}
                           for s in sorted(card.pop("_rel"))
                           if s in slug_to_name and s not in on_slugs]
    cards = [by_key[k] for k in order]
    dated = sorted((c for c in cards if c.get("posted")),
                   key=lambda c: c["posted"], reverse=True)
    undated = [c for c in cards if not c.get("posted")]
    return dated + undated


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
    if not monogram:                       # derive initials from the label when none given
        monogram = "".join(w[0] for w in (label or seed or "").split()[:2] if w).upper()
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


_TYPE_SINGULAR = {"product": "Product", "ingredient": "Ingredient", "condition": "Condition",
                  "goal": "Goal", "study": "Study", "list": "List", "person": "Person", "brand": "Brand"}


def recent_pages(profiles, limit=200):
    """Newest-first list of published pages, keyed off each page's `updated` date. This
    is the auto-derived 'What's New' - a list of recently added/updated pages, not a
    hand-kept changelog (git history is the changelog)."""
    items = []
    for p in profiles:
        if p.get("status") != "published":
            continue
        upd = p.metadata.get("updated")
        if not upd:
            continue
        items.append({"slug": p["slug"], "name": p.metadata.get("name") or p["slug"],
                      "type": p.get("type"),
                      "type_label": _TYPE_SINGULAR.get(p.get("type"), (p.get("type") or "").title()),
                      "date": str(upd)})
    items.sort(key=lambda d: (d["date"], d["name"].lower()), reverse=True)
    return items[:limit]


def recent_pages_grouped(pages):
    """Group a recent_pages() list into [{date, date_label, entries}] by day, newest first."""
    groups, cur = [], None
    for it in pages:
        if cur is None or cur["date"] != it["date"]:
            cur = {"date": it["date"], "date_label": _date_label(it["date"]), "entries": [it]}
            groups.append(cur)
        else:
            cur["entries"].append(it)
    return groups


# --- Syndication feeds (freshness) -------------------------------------------
# The changelog becomes a real RSS 2.0 + JSON Feed of recently added/updated pages,
# so the site's freshness is subscribable and machine-readable. Static, no deps.
SITE_URL = "https://ericries.github.io/skintiers"
import urllib.parse as _urlparse  # noqa: E402
SITE_BASE = _urlparse.urlsplit(SITE_URL).path.rstrip("/")  # "/skintiers"


def render_builder(env, catalog):
    """Render the self-contained routine builder page (used for both routine.html and
    404.html). Inlines the catalog JSON and assets/routine-builder.js so it works when
    served at any deep /r1/... fallback path on GitHub Pages."""
    builder_js = (sklib.ROOT / "assets" / "routine-builder.js").read_text()
    return env.get_template("routine_builder.html").render(
        site_base=SITE_BASE,
        catalog_json=json.dumps(catalog, separators=(",", ":")),
        builder_js=builder_js,
    )


def render_filter(env, filter_data):
    """Render filter.html: a self-contained client-side product filter/search over the
    published catalog. Inlines products-filter.json and assets/product-filter.js so the
    whole thing runs in the browser with no external deps (mirrors the routine builder).
    Category and active option lists are built in JS from the catalog itself."""
    filter_js = (sklib.ROOT / "assets" / "product-filter.js").read_text()
    return env.get_template("filter.html").render(
        page_url=f"{SITE_URL}/filter.html",
        page_desc="Filter and search the SkinTiers catalog by category, active ingredient, "
                  "price, and evidence strength - every result carries the site's own grade.",
        catalog_json=json.dumps(filter_data, separators=(",", ":")),
        filter_js=filter_js,
        product_count=len(filter_data["products"]),
    )


# --- Phase E: agent-native access layer ------------------------------------
# Raw GitHub base for the data-as-git markdown, handed to agents on for-agents.html.
RAW_BASE = "https://raw.githubusercontent.com/ericries/skintiers/main/"
SKILL_NAME = "skintiers"                         # skill slug; invoked as /skintiers
SKILL_ZIP = f"{SKILL_NAME}-skill.zip"            # published at the site root

# The machine-readable endpoints an agent consumes. Each `path` MUST be produced as a
# build output (asserted by tests/test_skill_bundle.py) so the "For Agents" page and the
# skill never advertise an endpoint that does not exist. Mirrored into skill/endpoints.json.
AGENT_ENDPOINTS = [
    {"path": "routine-catalog.json",
     "desc": "Every published/stub product, code-keyed, with pre-derived effect strength, "
             "tier, key actives, and UV-filter bands (fastest input for routine analysis)."},
    {"path": "routines.json",
     "desc": "Pre-computed dashboards for the site's curated routine pages."},
    {"path": "feed.json", "desc": "Recently added/updated pages (JSON Feed 1.1)."},
    {"path": "feed.xml", "desc": "Recently added/updated pages (RSS 2.0)."},
]


def render_for_agents(env):
    """Render for-agents.html: the plain-language guide that points any AI agent at the
    site (zero-install path + installable skill). Deliberately NOT linked from the nav or
    footer yet - discoverability is the integrator's call (Phase E is a first draft)."""
    return env.get_template("for_agents.html").render(
        page_url=f"{SITE_URL}/for-agents.html",
        page_desc="Use SkinTiers with an AI agent: a machine-readable, cited skincare "
                  "evidence source. Zero-install path plus a downloadable skill.",
        og_type="website",
        site_url=SITE_URL,
        raw_base=RAW_BASE,
        endpoints=AGENT_ENDPOINTS,
        skill_name=SKILL_NAME,
        skill_zip=SKILL_ZIP,
    )


def build_skill_bundle(out):
    """Assemble the installable agent skill under _site/skill/ (browsable) and zip it to
    _site/<SKILL_ZIP>. Single-sources its algorithm: docs/routine-strength-spec.md is copied
    in verbatim, and endpoints.json is generated from AGENT_ENDPOINTS, so the bundle cannot
    drift from the live build. Returns the list of files placed in the bundle dir."""
    skill_src = sklib.ROOT / "skill"
    spec_src = sklib.ROOT / "docs" / "routine-strength-spec.md"
    skill_out = out / "skill"
    skill_out.mkdir(parents=True, exist_ok=True)

    # Canonical, hand-written skill instructions.
    shutil.copy(skill_src / "SKILL.md", skill_out / "SKILL.md")
    # Single-sourced strength algorithm (canonical copy lives in docs/).
    shutil.copy(spec_src, skill_out / "routine-strength-spec.md")
    # Generated endpoint manifest so the skill's endpoint list is always build-accurate.
    endpoints_manifest = {
        "site_url": SITE_URL,
        "raw_base": RAW_BASE,
        "endpoints": [{"url": f"{SITE_URL}/{e['path']}", **e} for e in AGENT_ENDPOINTS],
    }
    (skill_out / "endpoints.json").write_text(json.dumps(endpoints_manifest, indent=2))

    bundle_files = sorted(p.name for p in skill_out.iterdir() if p.is_file())
    zip_path = out / SKILL_ZIP
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in bundle_files:
            zf.write(skill_out / name, arcname=f"{SKILL_NAME}/{name}")
    return bundle_files


FEED_TITLE = "SkinTiers - What's New"
FEED_DESC = "Recently added and updated pages on SkinTiers, a skeptical, evidence-first skincare directory."
FEED_LIMIT = 50


def _feed_items(pages):
    """Feed items from the newest-first recent_pages() list (capped at FEED_LIMIT). Each
    item links its page; the id is stable per (slug, updated) so readers don't re-notify
    until the page actually changes date."""
    items = []
    for pg in pages:
        title = f"{pg['type_label']}: {pg['name']}"
        url = f"{SITE_URL}/{pg['slug']}.html"
        uid = f"{SITE_URL}/#{pg['date']}-{hashlib.sha1(pg['slug'].encode('utf-8')).hexdigest()[:12]}"
        items.append({"title": title, "date": pg["date"], "url": url, "id": uid})
        if len(items) >= FEED_LIMIT:
            break
    return items


def _rfc822(date_str):
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 +0000")
    except ValueError:
        return ""


def render_rss(pages):
    """RSS 2.0 XML string of recently added/updated pages."""
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0"><channel>',
           f"<title>{_htmllib.escape(FEED_TITLE)}</title>", f"<link>{SITE_URL}/</link>",
           f"<description>{_htmllib.escape(FEED_DESC)}</description>",
           f'<atom:link xmlns:atom="http://www.w3.org/2005/Atom" href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>']
    for it in _feed_items(pages):
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


def render_json_feed(pages):
    """JSON Feed 1.1 string of recently added/updated pages."""
    feed = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": FEED_TITLE, "home_page_url": f"{SITE_URL}/",
        "feed_url": f"{SITE_URL}/feed.json", "description": FEED_DESC,
        "items": [
            {"id": it["id"], "url": it["url"], "title": it["title"],
             **({"date_published": f"{it['date']}T00:00:00Z"} if it["date"] else {})}
            for it in _feed_items(pages)
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
    render_og_image(out / "og", "_default", "SkinTiers",
                    "A skeptical, evidence-first skincare directory")

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

    potency_rank_index = build_potency_rank_index(profiles, by_slug)

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
                uv_spectrum = render_uv_spectrum(fils, combined=True)
        routine = routine_summary(p, by_slug)
        tier_list = tier_list_view(p, by_slug)
        # Surface the products that contain each graded active: on concern hubs
        # (condition/goal) and on strength ladders (a `list` whose tier_list opts into
        # `ladder: true`, i.e. it ranks FORMS of one active family - acids, retinoids,
        # vitamin C - so "products with each form" is exactly the useful next step).
        _wants_products = p.get("type") in ("condition", "goal") or (
            p.get("type") == "list" and (p.metadata.get("tier_list") or {}).get("ladder"))
        concern_products = (products_for_tier_list(tier_list, profiles)
                            if _wants_products else None)
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
        render_og_image(out / "og", p["slug"], p.metadata.get("name") or p["slug"],
                        _TYPE_SINGULAR.get(p.get("type"), (p.get("type") or "").title()))
        html = env.get_template("profile.html").render(
            profile=p.metadata,
            page_url=f"{SITE_URL}/{p['slug']}.html",
            page_desc=_plain_excerpt(standfirst),
            og_image=f"{SITE_URL}/og/{p['slug']}.png",
            og_type="article",
            standfirst=standfirst,
            body_main=body_main,
            sources_html=sources_html,
            comparator=render_inline(p.get("comparator") or "others in its category", slugs, names),
            grades_view=grades_view_for(p.metadata, slugs, names),
            price_view=price_view_for(p.metadata),
            evidence_levels=evidence_levels_view(p.metadata, slugs, names, potency_rank_index),
            recommended_in=p.get("recommended_in") or [],
            images=images,
            monogram=monogram,
            type_href=TYPE_HREF.get(p.get("type"), "index.html"),
            tagged_groups=tagged_groups_for(p, tag_index),
            backref_groups=backref_groups_for(p["slug"], rev_index),
            tier_nav=tier_nav_from_html(body_main),
            routine=routine,
            tier_list=tier_list,
            concern_products=concern_products,
            builder_url=routine_builder_path(routine, code_map),
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

    # Interactive routine builder: one self-contained page served as both the start
    # page (routine.html) and the 404 fallback (serves shared /r1/... paths on Pages).
    _builder_html = render_builder(env, catalog)
    (out / "routine.html").write_text(_builder_html)
    (out / "404.html").write_text(_builder_html)

    # Product filter/search: a flat, published-only catalog + a self-contained client-side
    # page (filter.html) that filters by category, active, max price, and evidence strength.
    # The catalog carries the site's own grades; the page surfaces them, never re-ranks.
    filter_data = filter_catalog(profiles, by_slug)
    (out / "products-filter.json").write_text(
        json.dumps(filter_data, separators=(",", ":")))
    (out / "filter.html").write_text(render_filter(env, filter_data))

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

    # What's New: an auto-derived, newest-first list of published pages (by their
    # `updated` date), grouped by day. No hand-kept changelog - git is the changelog.
    recent = recent_pages(profiles)
    (out / "whats-new.html").write_text(
        env.get_template("whats_new.html").render(groups=recent_pages_grouped(recent)))

    # Syndication feeds (RSS + JSON) of the same recently added/updated pages.
    (out / "feed.xml").write_text(render_rss(recent))
    (out / "feed.json").write_text(render_json_feed(recent))

    # The Feed: every expert-video card on the site, one place, newest-first by the
    # video's own posting date. Maintained automatically on every build.
    feed_cards = build_video_feed(profiles)
    (out / "feed.html").write_text(env.get_template("feed.html").render(
        cards=feed_cards,
        n_dated=sum(1 for c in feed_cards if c.get("posted")),
        needs_tiktok_js=any((video_embed(c.get("url")) or {}).get("kind") == "tiktok"
                            for c in feed_cards)))

    # Phase E: agent-native access layer. The "For Agents" page + the installable skill
    # bundle. Left UNLINKED from the nav/footer on purpose (integrator decides launch).
    (out / "for-agents.html").write_text(render_for_agents(env))
    build_skill_bundle(out)

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
