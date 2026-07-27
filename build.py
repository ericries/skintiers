#!/usr/bin/env python3
"""SkinTiers static site generator."""
import os
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
        html = env.get_template("profile.html").render(
            profile=p.metadata, body=body,
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

    if sklib.STATIC_DIR.exists():
        for f in sklib.STATIC_DIR.iterdir():
            if f.is_file():
                shutil.copy(f, out / f.name)
    print(f"built {len(profiles)} profiles -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(build())
