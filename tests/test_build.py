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


def test_pages_show_auto_backreferences_from_xrefs(tmp_path):
    # Every page auto-lists the published pages that [[link]] to it, grouped by type.
    data = tmp_path / "data"
    out = tmp_path / "_site"
    _write(data / "ingredients", "niacinamide", "published", "ingredient")
    _write(data / "ingredients", "glycerin", "published", "ingredient")  # referenced by nobody
    _write(data / "products", "serum", "published", "product",
           "Built on [[niacinamide]].\n")
    _write(data / "products", "draftprod", "draft", "product",
           "Also uses [[niacinamide]].\n")
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    nia = (out / "niacinamide.html").read_text()
    assert "Referenced by" in nia                     # section present
    assert 'href="serum.html"' in nia                 # published referencing product listed
    assert 'href="draftprod.html"' not in nia         # draft referencing page not surfaced
    gly = (out / "glycerin.html").read_text()
    assert "Referenced by" not in gly                 # no backrefs -> no empty section
    # a page does not list itself even if it self-references
    assert 'href="serum.html"' not in (out / "serum.html").read_text()


def test_tagged_section_does_not_name_the_site(tmp_path):
    data = tmp_path / "data"
    out = tmp_path / "_site"
    # the tagged section renders on condition/goal pages that other pages tag by slug
    _write(data / "conditions", "acne", "published", "condition")
    _write(data / "products", "spot", "published", "product", "Body.\n", tags=["acne"])
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    html = (out / "acne.html").read_text()
    # the tagged-content heading must not name the site (masthead/title brand chrome is fine)
    assert "Also on SkinTiers" not in html
    assert "Also tagged" in html   # the section still renders, just without the site name


def test_tiered_page_gets_at_a_glance_tier_nav(tmp_path):
    # A page with 2+ "## Tier N:" headings gets an auto "At a glance" click-down nav.
    data = tmp_path / "data"
    out = tmp_path / "_site"
    body = ("Intro.\n\n## Tier 1: The Foundation\n\nText.\n\n"
            "## Tier 2: Reliable Adjuncts\n\nMore.\n\n## What this page is not\n\nEnd.\n")
    _write(data / "goals", "anti-aging", "published", "goal", body)
    _write(data / "ingredients", "niacinamide", "published", "ingredient")  # not tiered
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    ag = (out / "anti-aging.html").read_text()
    assert "tier-glance" in ag                       # the nav renders
    assert 'href="#tier-1-the-foundation"' in ag     # click-down link to tier 1
    assert 'href="#tier-2-reliable-adjuncts"' in ag  # and tier 2
    assert "What this page is not" not in ag.split("tier-glance")[1].split("</nav>")[0]  # only tiers in the nav
    # a non-tiered page gets no tier-glance nav
    assert "tier-glance" not in (out / "niacinamide.html").read_text()


def test_uv_filter_spectrum_marker_renders_svg(tmp_path):
    data = tmp_path / "data"
    out = tmp_path / "_site"
    _write(data / "ingredients", "sunscreen-uv-filters", "published", "ingredient",
           "Filters.\n\n<!--uv-filter-spectrum-->\n\nMore.\n")
    _write(data / "ingredients", "avobenzone", "published", "ingredient")
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    html = (out / "sunscreen-uv-filters.html").read_text()
    assert 'class="uv-spectrum"' in html          # the SVG rendered
    assert 'href="avobenzone.html"' in html        # filter rows link their pages
    assert "uv-filter-spectrum" not in html        # marker was consumed
    assert 'class="uv-bar"' in html                # coverage bars present


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


def test_product_photo_rail_no_captions(tmp_path):
    data = tmp_path / "data"
    out = tmp_path / "_site"
    pdir = data / "products"
    pdir.mkdir(parents=True)
    # images: entries may be bare strings or mappings (source is kept in the
    # schema but NOT rendered as a caption; the rail shows photos, no labels).
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
    # A concise side rail, not the old "Product photo" box and not a captioned gallery.
    assert 'class="photo-rail"' in html
    assert '<div class="cap">Product photo</div>' not in html  # old pattern gone
    assert '<figcaption>' not in html                          # no photo labels
    # Local filename resolves under images/; a full URL is used as-is.
    assert 'src="images/serum-front.jpg"' in html
    assert 'src="https://cdn.example.net/serum-side.jpg"' in html


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


def _write_graded_product(dirpath, slug, effect, key_actives):
    """A product with one HEALTH grade at `effect` and a key_actives list."""
    dirpath.mkdir(parents=True, exist_ok=True)
    ka = "".join(f"- {a}\n" for a in key_actives)
    (dirpath / f"{slug}.md").write_text(
        f"---\nname: {slug.title()}\nslug: {slug}\ntype: product\nstatus: published\n"
        f"updated: 2026-08-03\nanalyzed: 2026-08-03\ncategory: Test\n"
        f"key_actives:\n{ka}"
        f"grades:\n- effect: {effect}\n  evidence: solid\n  use: For test (health)\n"
        f"---\n\n## Summary\n\nBody.\n\n## Sources\n\nNone.\n"
    )


def test_routine_dashboard_aggregates_from_products(tmp_path):
    # A `kind: routine` list with `steps:` gets an at-a-glance dashboard whose
    # tier distribution comes from each product's grades, whose active
    # ingredients come from the products' `key_actives`, and whose "good for"
    # comes from the routine's own `for:`. The rollup is also in routines.json.
    import json
    data = tmp_path / "data"
    out = tmp_path / "_site"
    _write(data / "ingredients", "azelaic-acid", "published", "ingredient")
    _write(data / "ingredients", "ceramides", "published", "ingredient")
    _write(data / "conditions", "acne", "published", "condition")
    _write_graded_product(data / "products", "cleanser", "minimal", [])
    _write_graded_product(data / "products", "treatment", "notable", ["azelaic-acid", "niacinamide"])
    _write_graded_product(data / "products", "cream", "modest", ["ceramides", "niacinamide"])
    _write(data / "ingredients", "niacinamide", "published", "ingredient")
    (data / "lists").mkdir(parents=True, exist_ok=True)
    (data / "lists" / "myroutine.md").write_text(
        "---\nname: My Routine\nslug: myroutine\ntype: list\nkind: routine\n"
        "status: published\nupdated: 2026-08-03\nanalyzed: 2026-08-03\n"
        "for:\n- acne\n"
        "steps:\n"
        "- when: AM\n  product: cleanser\n  role: Cleanser\n"
        "- when: AM\n  product: treatment\n  role: Treatment\n"
        "- when: PM\n  product: cream\n  role: Moisturizer\n"
        "---\n\nA routine.\n\n## Sources\n\nOn the linked pages.\n"
    )
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    # routines.json rollup
    rj = json.loads((out / "routines.json").read_text())["myroutine"]
    assert rj["product_count"] == 3
    assert rj["top_tier_count"] == 1                      # only "treatment" (notable)
    assert rj["tiers"] == {"top": 1, "mid": 1, "entry": 1}
    # composite strength: mean of effects notable(3)+modest(2)+minimal(1) = 2.0 -> "Moderate"
    assert rj["strength"]["label"] == "Moderate"
    assert rj["strength"]["segs"] == 2
    assert rj["ingredient_slugs"] == ["niacinamide", "azelaic-acid", "ceramides"]  # most-layered first
    assert rj["ingredients"]["niacinamide"] == 2         # niacinamide in 2 products -> x2

    # Code-keyed catalog for the routine builder: every published product gets a
    # stable base62 code and carries the signals the client dashboard recomputes.
    cat = json.loads((out / "routine-catalog.json").read_text())
    assert cat["v"] == 1 and "w" not in cat
    code_of = {p["s"]: c for c, p in cat["p"].items()}
    assert set(code_of) == {"cleanser", "treatment", "cream"}
    assert all(len(c) == 1 for c in code_of.values())          # first 62 products = 1-char codes
    treat = cat["p"][code_of["treatment"]]
    assert treat["t"] == "top" and set(treat["a"]) == {"azelaic-acid", "niacinamide"}
    assert cat["i"]["niacinamide"]["n"] == "Niacinamide"
    assert [n[0] for n in cat["notable"]] == ["Retinoid", "Vitamin C", "Niacinamide", "Exfoliant"]
    # the registry was written under the tmp data dir, NOT the real one
    assert (data / "routine-codes.yaml").exists()
    # routines index surfaces the dashboard as a card
    ri = (out / "routines.html").read_text()
    assert "ri-card" in ri and "My Routine" in ri and "genicon" in ri
    # "Open in builder" link: AM cleanser(0)+treatment(2), PM cream(1) -> r1/a02/p1
    my = (out / "myroutine.html").read_text()
    assert "Open this routine in the builder" in my
    assert 'href="r1/a02/p1"' in my
    assert "Retinoid" in rj["absent"]                    # common actives the routine lacks
    assert "Niacinamide" not in rj["absent"]             # present -> not listed
    assert rj["serves_slugs"] == ["acne"]
    # rendered dashboard
    html = (out / "myroutine.html").read_text()
    assert 'class="routine-dash"' in html
    assert "Moderate" in html                            # composite strength word rendered
    assert "how well it works" in html
    assert 'class="rd-x"' in html                        # x2 badge on the layered active
    assert "Does not contain" in html                    # absent row present
    assert "rd-chip-absent" in html
    assert 'href="azelaic-acid.html"' in html            # active-ingredient chip links out
    assert 'href="acne.html"' in html                    # "good for" chip
    assert 'href="treatment.html"' in html               # a step links its product
    assert "rd-tier-top" in html                          # tier bar present
    assert "rd-step-badge" in html                        # standardized product badge rendered
    assert "rd-badge-top" in html                         # badge frame colored by the product's tier
    assert "rd-step-mono" in html                         # monogram fallback (test products have no photo)
    # a non-routine page has no dashboard
    assert 'class="routine-dash"' not in (out / "treatment.html").read_text()


def test_routine_groups_sunscreen_filters_by_uv_band(tmp_path):
    # Sunscreen filters (which readers do not recognize by name) collapse into one
    # chip labeled by UVB/UVA coverage, not shown as individual ingredient chips.
    import json
    data = tmp_path / "data"
    out = tmp_path / "_site"
    _write(data / "ingredients", "zinc-oxide", "published", "ingredient")
    _write(data / "ingredients", "octinoxate", "published", "ingredient")
    _write(data / "ingredients", "sunscreen-uv-filters", "published", "ingredient")
    _write_graded_product(data / "products", "spf", "modest", ["zinc-oxide", "octinoxate"])
    (data / "lists").mkdir(parents=True, exist_ok=True)
    (data / "lists" / "sunroutine.md").write_text(
        "---\nname: Sun Routine\nslug: sunroutine\ntype: list\nkind: routine\n"
        "status: published\nupdated: 2026-08-03\nanalyzed: 2026-08-03\n"
        "steps:\n- when: AM\n  product: spf\n  role: Sunscreen\n"
        "---\n\nA routine.\n\n## Sources\n\nOn the linked pages.\n"
    )
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    rj = json.loads((out / "routines.json").read_text())["sunroutine"]
    # zinc-oxide covers 290-400 (UVB+UVA); octinoxate 290-320 (UVB) -> combined UVB + UVA
    assert rj["filters"]["coverage"] == "UVB + UVA"
    assert [i["name"] for i in rj["filters"]["entries"]] == ["Zinc oxide", "Octinoxate"]
    assert rj["ingredient_slugs"] == []                  # filters are NOT plain ingredient chips
    html = (out / "sunroutine.html").read_text()
    assert "rd-filters" in html                           # one grouped sunscreen block
    assert "UVB + UVA" in html                            # labeled by band
    assert 'href="sunscreen-uv-filters.html"' in html    # band label links the filter hub
    # the filter names ARE shown (under the band) and each links its own page
    assert ">Zinc oxide</a>" in html
    assert 'href="zinc-oxide.html"' in html


def test_expert_video_card_and_routine_source_render(tmp_path):
    # A page with `videos:` renders an attributed expert-video card; a routine
    # with `source:` renders a "Sourced from" attribution block.
    data = tmp_path / "data"
    out = tmp_path / "_site"
    _write(data / "people", "creator", "published", "person")
    (data / "ingredients").mkdir(parents=True, exist_ok=True)
    (data / "ingredients" / "vitc.md").write_text(
        "---\nname: VitC\nslug: vitc\ntype: ingredient\nstatus: published\n"
        "updated: 2026-08-03\nanalyzed: 2026-08-03\n"
        "videos:\n- title: Test Short\n  creator: A Creator\n  creator_slug: creator\n"
        "  credential: Cosmetic chemist\n  platform: YouTube\n  url: https://www.youtube.com/watch?v=U68MTXuOG9k\n"
        "  thesis: A verifiable claim.\n"
        "---\n\nBody.\n\n## Sources\n\nNone.\n"
    )
    _write_graded_product(data / "products", "cl", "modest", [])
    (data / "lists").mkdir(parents=True, exist_ok=True)
    (data / "lists" / "r.md").write_text(
        "---\nname: R\nslug: r\ntype: list\nkind: routine\nstatus: published\n"
        "updated: 2026-08-03\nanalyzed: 2026-08-03\n"
        "source:\n  creator: A Creator\n  creator_slug: creator\n  platform: TikTok\n"
        "  url: https://example.com/r\n  note: Sourced note.\n"
        "steps:\n- when: AM\n  product: cl\n  role: Cleanser\n"
        "---\n\nBody.\n\n## Sources\n\nNone.\n"
    )
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    v = (out / "vitc.html").read_text()
    assert 'class="vids"' in v and "Test Short" in v
    assert 'href="creator.html"' in v                    # creator links their person page
    assert "https://www.youtube.com/watch?v=U68MTXuOG9k" in v   # link-out fallback kept
    assert 'class="vid-embed"' in v                      # and the video is embedded
    assert "https://www.youtube.com/embed/U68MTXuOG9k" in v     # responsive iframe src
    rt = (out / "r.html").read_text()
    assert "rd-source" in rt and "Sourced from" in rt
    assert "Sourced note." in rt


def test_routine_builder_page_is_emitted_self_contained(tmp_path):
    data = tmp_path / "data"
    out = tmp_path / "_site"
    _write(data / "products", "serum", "published", "product")
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    builder = (out / "routine.html").read_text()
    fallback = (out / "404.html").read_text()
    assert builder == fallback                                  # same page serves both
    assert 'id="rb-catalog"' in builder                        # catalog inlined
    assert '"p":' in builder                                    # catalog JSON present
    assert "function parseRoutine" in builder                  # builder JS inlined
    assert '<base href="/skintiers/">' in builder              # base href for deep-path links


def test_builder_catalog_includes_stub_products(tmp_path):
    # The builder universe includes published AND stub products (breadth); drafts excluded.
    import json
    data = tmp_path / "data"
    out = tmp_path / "_site"
    _write(data / "products", "pubprod", "published", "product")
    _write(data / "products", "stubby", "stub", "product")
    _write(data / "products", "draftp", "draft", "product")
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    cat = json.loads((out / "routine-catalog.json").read_text())
    slugs = {p["s"] for p in cat["p"].values()}
    assert "pubprod" in slugs and "stubby" in slugs        # published + stub are pickable
    assert "draftp" not in slugs                           # mid-research drafts excluded


def test_gen_icon_is_deterministic_svg():
    sys.path.insert(0, str(ROOT))
    import build
    a = build.gen_icon("cerave-moisturizing-cream", "CM", "CeraVe Moisturizing Cream")
    b = build.gen_icon("cerave-moisturizing-cream", "CM", "CeraVe Moisturizing Cream")
    c = build.gen_icon("differin-adapalene-0-1-gel", "DA")
    assert a == b                                   # same seed -> identical icon
    assert a != c                                   # different seed -> different icon
    assert a.startswith("<svg") and ">CM<" in a     # inline SVG carrying the monogram
    assert "hsl(" in a                              # hue-derived gradient


def test_profile_pages_have_open_graph_meta(tmp_path):
    data = tmp_path / "data"
    out = tmp_path / "_site"
    _write(data / "ingredients", "niacinamide", "published", "ingredient",
           "Niacinamide is a well-studied form of vitamin B3 with real barrier benefits.\n")
    env = {**os.environ, "SK_DATA": str(data), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    html = (out / "niacinamide.html").read_text()
    assert '<meta property="og:title" content="Niacinamide' in html
    assert '<meta property="og:type" content="article">' in html
    assert '<meta property="og:url" content="https://ericries.github.io/skintiers/niacinamide.html">' in html
    assert '<link rel="canonical" href="https://ericries.github.io/skintiers/niacinamide.html">' in html
    assert 'property="og:description" content="Niacinamide is a well-studied' in html
    assert '<meta property="og:image" content="https://ericries.github.io/skintiers/og/niacinamide.png">' in html
    assert '<meta name="twitter:card" content="summary_large_image">' in html
    assert (out / "og" / "niacinamide.png").exists()             # generated share card
    assert (out / "og" / "_default.png").exists()                # site fallback card


def test_whats_new_is_auto_derived_page_list(tmp_path):
    # What's New is a newest-first list of published pages (by `updated`), NOT a changelog.
    pdir = tmp_path / "data" / "products"
    pdir.mkdir(parents=True)
    (pdir / "old.md").write_text("---\nname: Old Serum\nslug: old\ntype: product\n"
                                 "status: published\nupdated: 2026-07-01\nanalyzed: 2026-07-01\n---\n\nBody.\n")
    (pdir / "new.md").write_text("---\nname: New Serum\nslug: new\ntype: product\n"
                                 "status: published\nupdated: 2026-08-04\nanalyzed: 2026-08-04\n---\n\nBody.\n")
    out = tmp_path / "_site"
    env = {**os.environ, "SK_DATA": str(tmp_path / "data"), "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    wn = (out / "whats-new.html").read_text()
    assert "wn-type wn-type-product" in wn                       # auto-derived, type-badged list
    assert 'href="new.html"' in wn and 'href="old.html"' in wn
    assert wn.index("New Serum") < wn.index("Old Serum")         # newest first
    assert "running log of what has changed" not in wn          # no hand-kept changelog
    assert "<title>Product: New Serum</title>" in (out / "feed.xml").read_text()


def test_syndication_feeds_render():
    import json
    import xml.dom.minidom as minidom
    sys.path.insert(0, str(ROOT))
    import build
    # Feeds are built from the recent_pages() list: each item links its own page.
    pages = [
        {"slug": "niacinamide", "name": "Niacinamide", "type": "ingredient",
         "type_label": "Ingredient", "date": "2026-08-03"},
        {"slug": "cerave-moisturizing-cream", "name": "CeraVe Moisturizing Cream",
         "type": "product", "type_label": "Product", "date": "2026-08-02"},
    ]
    # RSS: well-formed, every item links its page.
    rss = build.render_rss(pages)
    doc = minidom.parseString(rss)                       # raises if malformed
    items = doc.getElementsByTagName("item")
    assert len(items) == 2
    links = [i.getElementsByTagName("link")[0].firstChild.data for i in items]
    assert links[0] == "https://ericries.github.io/skintiers/niacinamide.html"
    assert links[1] == "https://ericries.github.io/skintiers/cerave-moisturizing-cream.html"
    titles = [i.getElementsByTagName("title")[0].firstChild.data for i in items]  # each item's own title
    assert titles[0] == "Ingredient: Niacinamide"
    assert "Mon, 03 Aug 2026" in rss                     # RFC-822 pubDate from the page's updated date
    # JSON Feed 1.1: valid, same items.
    feed = json.loads(build.render_json_feed(pages))
    assert feed["version"] == "https://jsonfeed.org/version/1.1"
    assert len(feed["items"]) == 2
    assert feed["items"][0]["url"] == "https://ericries.github.io/skintiers/niacinamide.html"
    assert feed["items"][0]["title"] == "Ingredient: Niacinamide"
    assert feed["items"][0]["date_published"] == "2026-08-03T00:00:00Z"


def test_video_embed_helper():
    sys.path.insert(0, str(ROOT))
    import build
    yt = build.video_embed("https://www.youtube.com/watch?v=U68MTXuOG9k")
    assert yt["kind"] == "youtube" and yt["src"] == "https://www.youtube.com/embed/U68MTXuOG9k"
    assert build.video_embed("https://youtu.be/K5zwloQza9M")["id"] == "K5zwloQza9M"
    assert build.video_embed("https://www.youtube.com/shorts/K5zwloQza9M")["kind"] == "youtube"
    tt = build.video_embed("https://www.tiktok.com/@x/video/7178297870498483457")
    assert tt["kind"] == "tiktok" and tt["id"] == "7178297870498483457"
    assert build.video_embed("https://example.com/not-a-video") is None
