import os
import subprocess
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _write(dirpath, slug, status, typ, body="Body.\n", tags=None):
    dirpath.mkdir(parents=True, exist_ok=True)
    tags_line = f"tags: [{', '.join(tags)}]\n" if tags else ""
    (dirpath / f"{slug}.md").write_text(
        f"---\nname: {slug.title()}\nslug: {slug}\ntype: {typ}\nstatus: {status}\n"
        f"updated: 2026-07-26\nanalyzed: 2026-07-26\n{tags_line}---\n\n{body}"
    )


def test_build_renders_all_statuses_with_badge_and_xref(tmp_path):
    data = tmp_path / "data"
    out = tmp_path / "_site"
    _write(data / "ingredients", "niacinamide", "published", "ingredient")
    _write(data / "products", "serum", "published", "product",
           "Contains [[niacinamide]] and [[unobtainium]].\n")
    _write(data / "products", "secret", "draft", "product")
    _write(data / "conditions", "acne", "published", "condition")
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert (out / "serum.html").exists()
    assert (out / "niacinamide.html").exists()
    assert (out / "secret.html").exists()              # draft renders as a link target
    assert (out / "index.html").exists()
    assert (out / "conditions.html").exists()           # new condition listing generated
    assert (out / "goals.html").exists()                # new goal listing generated
    assert (out / "acne.html").exists()                 # condition profile page renders
    assert "Acne" in (out / "acne.html").read_text()
    assert "draft" in (out / "secret.html").read_text().lower()   # status badge shown
    serum_html = (out / "serum.html").read_text()
    assert 'href="niacinamide.html"' in serum_html   # resolvable xref linked
    assert "unobtainium.html" not in serum_html        # broken xref is plain text


def test_index_nav_hides_categories_with_no_published_content(tmp_path):
    data = tmp_path / "data"
    out = tmp_path / "_site"
    # Products: has a published profile -> should appear in nav.
    _write(data / "products", "serum", "published", "product")
    # Ingredients: has a published profile -> should appear in nav.
    _write(data / "ingredients", "niacinamide", "published", "ingredient")
    # Conditions: only draft/stub -> hidden from nav, but listing still built.
    _write(data / "conditions", "acne", "draft", "condition")
    _write(data / "conditions", "rosacea", "stub", "condition")
    # Goals: no profiles at all -> hidden from nav, but listing still built.
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    index_html = (out / "index.html").read_text()
    # The global site header links every listing page; the empty-category hiding
    # is about the INDEX's category nav specifically, so assert within that block.
    import re
    m = re.search(r'<ul class="nav-cats">(.*?)</ul>', index_html, re.DOTALL)
    assert m, "index category nav not found"
    cat_nav = m.group(1)
    # (a) categories with >=1 published profile appear in the index category nav.
    assert 'href="products.html"' in cat_nav
    assert 'href="ingredients.html"' in cat_nav
    # (b) all-draft/stub and empty categories are omitted from the index category nav...
    assert 'href="conditions.html"' not in cat_nav
    assert 'href="goals.html"' not in cat_nav
    # ...yet their listing page files are still produced.
    assert (out / "conditions.html").exists()
    assert (out / "goals.html").exists()
    # Visible categories show their TOTAL count (published + draft + stub).
    assert "Products (1)" in cat_nav
    assert "Ingredients (1)" in cat_nav


def test_products_listing_groups_by_category_in_order(tmp_path):
    data = tmp_path / "data"
    out = tmp_path / "_site"
    pdir = data / "products"
    pdir.mkdir(parents=True)

    def _prod(slug, category=None):
        cat = f"category: {category}\n" if category else ""
        (pdir / f"{slug}.md").write_text(
            f"---\nname: {slug.title()}\nslug: {slug}\ntype: product\n"
            f"status: published\nupdated: 2026-07-26\nanalyzed: 2026-07-26\n"
            f"{cat}---\n\nBody.\n")

    # Deliberately out of display order in the file glob; Moisturizers should
    # still render AFTER Sunscreens, and the uncategorized one under "Other".
    _prod("a-cream", "Moisturizers")
    _prod("b-spf", "Sunscreens")
    _prod("c-mystery")  # no category -> "Other"
    # Ingredient listing must stay flat (no category grouping).
    _write(data / "ingredients", "niacinamide", "published", "ingredient")

    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr

    products_html = (out / "products.html").read_text()
    # All three category headings present.
    assert 'class="listing-group">Sunscreens<' in products_html
    assert 'class="listing-group">Moisturizers<' in products_html
    assert 'class="listing-group">Other<' in products_html
    # Order: Sunscreens (a defined bucket) before Moisturizers, both before Other.
    assert (products_html.index("Sunscreens")
            < products_html.index("Moisturizers")
            < products_html.index("Other"))
    # Each product sits under its heading.
    assert products_html.index("Sunscreens") < products_html.index("B-Spf")
    assert products_html.index("Moisturizers") < products_html.index("A-Cream")
    assert products_html.index("Other") < products_html.index("C-Mystery")
    # The flat ingredient listing has no group headings.
    assert 'class="listing-group"' not in (out / "ingredients.html").read_text()


def test_product_photo_gallery_with_source_captions(tmp_path):
    data = tmp_path / "data"
    out = tmp_path / "_site"
    pdir = data / "products"
    pdir.mkdir(parents=True)
    # images: entries may be bare strings or mappings with a source + source_url.
    (pdir / "serum.md").write_text(
        "---\nname: Test Serum\nslug: serum\ntype: product\nstatus: published\n"
        "updated: 2026-07-26\nanalyzed: 2026-07-26\n"
        "images:\n"
        "- file: serum-front.jpg\n"
        "  source: Manufacturer\n"
        "  source_url: https://example.com/serum\n"
        "- https://cdn.example.net/serum-side.jpg\n"
        "---\n\nBody.\n")
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    html = (out / "serum.html").read_text()
    # A gallery section, not the old single "Product photo" caption box.
    assert 'class="gallery"' in html
    assert 'class="gallery-h">Photos' in html
    assert '<div class="cap">Product photo</div>' not in html  # old pattern gone
    # Local filename resolves under images/; a full URL is used as-is.
    assert 'src="images/serum-front.jpg"' in html
    assert 'src="https://cdn.example.net/serum-side.jpg"' in html
    # The sourced image is captioned with a link to its site; the bare one isn't.
    assert '<figcaption>' in html
    assert 'href="https://example.com/serum"' in html
    assert '>Manufacturer</a>' in html


def test_build_renders_tagged_index_on_condition_page(tmp_path):
    data = tmp_path / "data"
    out = tmp_path / "_site"
    _write(data / "conditions", "acne", "published", "condition")
    _write(data / "ingredients", "tretinoin", "published", "ingredient", tags=["acne"])
    _write(data / "ingredients", "adapalene", "published", "ingredient", tags=["acne"])
    _write(data / "ingredients", "niacinamide", "published", "ingredient")  # untagged
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    acne_html = (out / "acne.html").read_text()
    assert "tagged" in acne_html.lower()                 # tagged section rendered
    assert "Ingredients" in acne_html                    # grouped under Ingredients heading
    assert 'href="tretinoin.html"' in acne_html
    assert 'href="adapalene.html"' in acne_html
    assert 'href="niacinamide.html"' not in acne_html    # untagged page not listed
    # The tagged section is NOT rendered on ingredient (non condition/goal) pages.
    assert "tagged" not in (out / "tretinoin.html").read_text().lower()
