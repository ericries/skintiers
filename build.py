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
)

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


def image_and_monogram(metadata):
    """Return (image_src_or_None, monogram) for a profile.

    A bare filename resolves to images/<file>; a URL is used as-is. When no
    image is set, image_src is None and the template draws a monogram badge.
    """
    image = metadata.get("image")
    image_src = None
    if image:
        image_src = image if re.match(r"^https?://", image) else f"images/{image}"
    words = (metadata.get("name") or "").split()
    monogram = "".join(w[0] for w in words[:2] if w).upper()
    return image_src, monogram

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


def build():
    env = Environment(loader=FileSystemLoader(str(sklib.TEMPLATES_DIR)), autoescape=True)
    out = sklib.OUTPUT_DIR
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    # Render EVERY status (stubs/drafts included) so cross-links always resolve; each is badged.
    profiles = sklib.load_profiles(sklib.DATA_DIR)
    slugs = {p["slug"] for p in profiles}
    names = {p["slug"]: p["name"] for p in profiles}
    tag_index = sklib.build_tag_index(profiles)

    for p in profiles:
        linked = sklib.linkify_xrefs(p.content, slugs, names)
        body = sklib.render_markdown(linked)
        standfirst, body_rest = split_standfirst(body)
        body_main, sources_html = split_sources(body_rest)
        image_src, monogram = image_and_monogram(p.metadata)
        html = env.get_template("profile.html").render(
            profile=p.metadata,
            standfirst=standfirst,
            body_main=body_main,
            sources_html=sources_html,
            comparator=p.get("comparator") or "others in its category",
            grades_view=grades_view_for(p.metadata),
            recommended_in=p.get("recommended_in") or [],
            image_src=image_src,
            monogram=monogram,
            type_href=TYPE_HREF.get(p.get("type"), "index.html"),
            tagged_groups=tagged_groups_for(p, tag_index))
        (out / f"{p['slug']}.html").write_text(html)

    # Listing pages are always built for every category; only the index nav is
    # filtered to categories with at least one PUBLISHED profile.
    nav_categories = []
    for typ, filename, label in LISTINGS:
        of_type = [p for p in profiles if p.get("type") == typ]
        items = [p.metadata for p in of_type]
        published_count = sum(1 for p in of_type if p.get("status") == "published")
        html = env.get_template("listing.html").render(heading=label, items=items)
        (out / f"{filename}.html").write_text(html)
        if published_count >= 1:
            nav_categories.append(
                {"label": label, "filename": filename, "count": len(of_type)})

    index = env.get_template("index.html").render(nav_categories=nav_categories)
    (out / "index.html").write_text(index)

    # Standalone Method page (not a data profile).
    method = env.get_template("method.html").render()
    (out / "method.html").write_text(method)

    if sklib.STATIC_DIR.exists():
        for f in sklib.STATIC_DIR.iterdir():
            if f.is_file():
                shutil.copy(f, out / f.name)
        images = sklib.STATIC_DIR / "images"
        if images.is_dir():
            shutil.copytree(images, out / "images", dirs_exist_ok=True)
    print(f"built {len(profiles)} profiles -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(build())
