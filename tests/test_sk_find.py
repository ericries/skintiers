"""Name -> file resolution. The root-cause fix for agents grepping the repo.

An agent knows a product by its marketed name ("COS de BAHA AZ15", "CeraVe AM
Facial Moisturizing Lotion SPF 30"). The repo is organised by slug, and slugs are
often shorter or differently worded than the marketed name
(anua-azelaic-acid-serum). So name -> path resolution previously required guessing
or grepping, which external agents were observed doing repeatedly.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import sklib  # noqa: E402


def _mk(d, typ, slug, name, **extra):
    p = d / typ
    p.mkdir(parents=True, exist_ok=True)
    lines = [f"name: {name}", f"slug: {slug}", f"type: {typ[:-1]}",
             "status: published", "updated: 2026-01-01"]
    for k, v in extra.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            lines += [f"- {i}" for i in v]
        else:
            lines.append(f"{k}: {v}")
    (p / f"{slug}.md").write_text("---\n" + "\n".join(lines) + "\n---\n\nBody.\n")


def _data(tmp_path):
    d = tmp_path / "data"
    _mk(d, "products", "cos-de-baha-az20-azelaic-acid-20-serum",
        "Cos De BAHA AZ20 Azelaic Acid 20% Serum", brand="Cos De BAHA")
    _mk(d, "products", "anua-azelaic-acid-serum",
        "Anua Azelaic Acid 10% Hyaluron Redness Soothing Serum", brand="Anua")
    _mk(d, "products", "cerave-am-facial-moisturizing-lotion-spf-30",
        "CeraVe AM Facial Moisturizing Lotion SPF 30", brand="CeraVe")
    _mk(d, "ingredients", "azelaic-acid", "Azelaic Acid")
    return d


def test_exact_slug_and_exact_name_win(tmp_path):
    d = _data(tmp_path)
    assert sklib.find_entities("azelaic-acid", d)[0]["slug"] == "azelaic-acid"
    hit = sklib.find_entities("CeraVe AM Facial Moisturizing Lotion SPF 30", d)[0]
    assert hit["slug"] == "cerave-am-facial-moisturizing-lotion-spf-30"
    assert hit["path"].endswith("data/products/cerave-am-facial-moisturizing-lotion-spf-30.md")


def test_resolves_a_compact_product_code_in_the_name(tmp_path):
    """'AZ20' appears inside the name as a token; an agent will type it alone."""
    d = _data(tmp_path)
    hits = sklib.find_entities("AZ20", d)
    assert hits and hits[0]["slug"] == "cos-de-baha-az20-azelaic-acid-20-serum"


def test_partial_brand_plus_active_resolves(tmp_path):
    d = _data(tmp_path)
    hits = sklib.find_entities("anua azelaic", d)
    assert hits[0]["slug"] == "anua-azelaic-acid-serum"


def test_type_filter_and_no_match_is_empty(tmp_path):
    d = _data(tmp_path)
    assert sklib.find_entities("azelaic", d, typ="ingredient")[0]["type"] == "ingredient"
    assert sklib.find_entities("tirtir azelaic 12", d) == [] or \
        sklib.find_entities("tirtir azelaic 12", d)[0]["score"] < 80


def test_aliases_are_searchable(tmp_path):
    """The feedback asked for regional/version names in discovery metadata."""
    d = _data(tmp_path)
    _mk(d, "products", "some-product", "Some Product",
        aliases=["AZ15", "15% Azelaic Acid High Strength Serum"])
    hits = sklib.find_entities("AZ15", d)
    assert hits and hits[0]["slug"] == "some-product"


def test_find_entities_resolves_a_near_slug_for_hub_dedup(tmp_path):
    """discover_hubs.py deduped candidates by EXACT slug, so its 'neck-chest-care'
    candidate kept re-firing even though data/goals/neck-chest-decolletage-care.md
    exists. A resolver lookup on the human name has to find it."""
    d = tmp_path / "data"
    _mk(d, "goals", "neck-chest-decolletage-care", "Neck and Chest (Décolletage) Care")
    hits = sklib.find_entities("Neck & chest (décolletage) care", d, typ="goal")
    assert hits and hits[0]["slug"] == "neck-chest-decolletage-care"
    assert hits[0]["score"] >= 80
