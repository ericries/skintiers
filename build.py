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

    counts = {}
    for typ, filename, heading in LISTINGS:
        items = [p.metadata for p in profiles if p.get("type") == typ]
        counts[typ] = len(items)
        html = env.get_template("listing.html").render(heading=heading, items=items)
        (out / f"{filename}.html").write_text(html)

    index = env.get_template("index.html").render(
        product_count=counts.get("product", 0),
        ingredient_count=counts.get("ingredient", 0),
        condition_count=counts.get("condition", 0),
        goal_count=counts.get("goal", 0),
    )
    (out / "index.html").write_text(index)

    if sklib.STATIC_DIR.exists():
        for f in sklib.STATIC_DIR.iterdir():
            if f.is_file():
                shutil.copy(f, out / f.name)
    print(f"built {len(profiles)} profiles -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(build())
