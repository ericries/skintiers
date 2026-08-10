#!/usr/bin/env python3
"""Find published products that contain ALL of the given active ingredients.

Use when a study on an ingredient/product page tests a COMBINATION (not the
isolated active): run this with the tested actives' slugs to find a site product
that embodies that exact combination, so the study can link to a real product.

    python scripts/products_with.py ascorbyl-palmitate sodium-ascorbyl-phosphate

Matches against each product's `key_actives:` first (the structured field); falls
back to a body [[xref]] mention so a product that names an active in its INCI list
but not in key_actives still counts. Prints "slug\tname" per match, or a note if
none. Exit 0 always (a no-match is a valid, informative answer)."""
import sys
import pathlib
import frontmatter

ROOT = pathlib.Path(__file__).resolve().parent.parent
PRODUCTS = ROOT / "data" / "products"


def actives_of(post):
    ka = {str(a).strip().lower() for a in (post.metadata.get("key_actives") or []) if a}
    # also count an active named as a [[xref]] anywhere in the body (e.g. INCI list)
    body = post.content.lower()
    return ka, body


def main(argv):
    wanted = [a.strip().lower() for a in argv if a.strip()]
    if not wanted:
        print("usage: products_with.py <active-slug> [<active-slug> ...]", file=sys.stderr)
        return 2
    matches = []
    for f in sorted(PRODUCTS.glob("*.md")):
        post = frontmatter.load(f)
        if post.metadata.get("status") != "published":
            continue
        ka, body = actives_of(post)
        if all(w in ka or f"[[{w}" in body for w in wanted):
            matches.append((post.metadata.get("slug") or f.stem,
                            post.metadata.get("name") or f.stem))
    if not matches:
        print(f"no published product contains all of: {', '.join(wanted)}")
        return 0
    for slug, name in matches:
        print(f"{slug}\t{name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
