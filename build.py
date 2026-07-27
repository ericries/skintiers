#!/usr/bin/env python3
"""SkinTiers static site generator."""
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
import sklib  # noqa: E402
from jinja2 import Environment, FileSystemLoader  # noqa: E402

LISTINGS = (
    ("product", "products", "Products"),
    ("ingredient", "ingredients", "Ingredients"),
    ("condition", "conditions", "Conditions"),
    ("goal", "goals", "Goals"),
)


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

    for p in profiles:
        linked = sklib.linkify_xrefs(p.content, slugs, names)
        body = sklib.render_markdown(linked)
        html = env.get_template("profile.html").render(profile=p.metadata, body=body)
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
