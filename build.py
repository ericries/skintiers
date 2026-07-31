#!/usr/bin/env python3
"""SkinTiers static site generator."""
import os
import re
import shutil
import sys
import types

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
import sklib  # noqa: E402
from jinja2 import Environment, FileSystemLoader  # noqa: E402

LISTINGS = (
    ("product", "products", "Products"),
    ("ingredient", "ingredients", "Ingredients"),
    ("condition", "conditions", "Conditions"),
    ("goal", "goals", "Goals"),
    ("study", "studies", "Studies"),
    ("list", "lists", "Lists"),
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


def grouped_by_category(metadatas, order):
    """Group product metadata dicts into [{label, items}] by their `category`
    field, following `order`; unknown/missing categories collect under
    "Other". Empty groups are omitted. Within a group, original (alphabetical
    by slug) order is preserved."""
    buckets = {label: [] for label in order}
    other = []
    for m in metadatas:
        label = m.get("category")
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


ASSURANCE_TIPS = {
    "stub": "Placeholder page, not yet fully researched.",
    "sonnet": "Drafted and auto-checked (lint, sources, style), single pass.",
    "opus": "Independently verified: every cited source re-fetched, quotes and statistics checked.",
    "reviewed": "Read and signed off by a human editor.",
}


def build():
    env = Environment(loader=FileSystemLoader(str(sklib.TEMPLATES_DIR)), autoescape=True)
    env.globals["assurance_tip"] = lambda level: ASSURANCE_TIPS.get(level, "")
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

    for p in profiles:
        linked = sklib.linkify_xrefs(p.content, slugs, names)
        body = sklib.render_markdown(linked)
        standfirst, body_rest = split_standfirst(body)
        body_main, sources_html = split_sources(body_rest)
        images, monogram = images_and_monogram(p.metadata)
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
            backref_groups=backref_groups_for(p["slug"], rev_index))
        (out / f"{p['slug']}.html").write_text(html)

    # Listing pages are always built for every category; only the index nav is
    # filtered to categories with at least one PUBLISHED profile.
    nav_categories = []
    for typ, filename, label in LISTINGS:
        of_type = [p for p in profiles if p.get("type") == typ]
        items = [p.metadata for p in of_type]
        published_count = sum(1 for p in of_type if p.get("status") == "published")
        # The Products index is grouped into high-level categories; the other
        # listings stay flat.
        groups = grouped_by_category(items, PRODUCT_CATEGORY_ORDER) \
            if typ == "product" else None
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
