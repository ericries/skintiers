"""The product filter catalog (products-filter.json) and its helpers.

filter_catalog reuses the same grade helpers the product pages use, so the filter
surfaces existing grades and never invents a ranking. These tests pin the JSON shape
(price + actives for a known product) and the lowest-price/grade derivation.
"""
import json
import os
import subprocess
import sys
import pathlib

import build

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_lowest_price_picks_minimum():
    low = build._lowest_price({"price": [
        {"amount": 20, "size": "50 ml"},
        {"amount": 8.5, "size": "30 ml", "currency": "USD"},
    ]})
    assert low["amount"] == 8.5
    assert low["size"] == "30 ml"


def test_lowest_price_none_when_missing_or_malformed():
    assert build._lowest_price({}) is None
    assert build._lowest_price({"price": None}) is None
    assert build._lowest_price({"price": [{"currency": "USD"}]}) is None


def test_filter_catalog_row_shape_and_grade():
    # Emulate the mapping-ish profile objects build() passes (p["slug"], p.get(...), p.metadata).
    class _Prof(dict):
        def __init__(self, slug, meta, status, typ):
            super().__init__(slug=slug, status=status, type=typ)
            self.metadata = meta

    ing = _Prof("niacinamide", {"name": "Niacinamide"}, "published", "ingredient")
    prod = _Prof("acme-serum", {
        "name": "Acme Serum", "brand": "Acme", "category": "Vitamin C serums",
        "key_actives": ["niacinamide"],
        "price": [{"amount": 29, "size": "30 ml"}, {"amount": 45, "size": "50 ml"}],
        "grades": [
            {"effect": "notable", "evidence": "solid", "use": "Brightening (health)"},
            {"effect": "strong", "evidence": "anecdotal", "use": "Glow (cosmetic)"},
        ],
    }, "published", "product")
    draft = _Prof("wip", {"name": "WIP", "category": "Cleansers"}, "draft", "product")

    by_slug = {p["slug"]: p for p in (prod, ing, draft)}
    cat = build.filter_catalog([prod, ing, draft], by_slug)
    rows = cat["products"]
    assert [r["slug"] for r in rows] == ["acme-serum"]  # drafts + ingredients excluded
    r = rows[0]
    assert r["price"] == 29 and r["price_display"] == "$29" and r["price_size"] == "30 ml"
    assert r["actives"] == [{"slug": "niacinamide", "name": "Niacinamide"}]
    # Health-labeled grade wins over the stronger cosmetic one.
    assert r["effect"] == "notable" and r["evidence"] == "solid" and r["segs"] == 3
    assert r["brand"] == "Acme" and r["url"] == "acme-serum.html"


def test_no_price_product_is_kept_with_null_price():
    import build as b

    class _Prof(dict):
        def __init__(self, slug, meta):
            super().__init__(slug=slug, status="published", type="product")
            self.metadata = meta

    p = _Prof("no-price", {"name": "No Price", "category": "Cleansers"})
    rows = b.filter_catalog([p], {"no-price": p})["products"]
    assert len(rows) == 1
    assert rows[0]["price"] is None and rows[0]["price_display"] is None


def test_built_catalog_json_has_price_and_actives_for_known_product(tmp_path):
    out = tmp_path / "_site"
    env = {**os.environ, "SK_OUTPUT": str(out)}
    r = subprocess.run([sys.executable, str(ROOT / "build.py")], env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr

    catalog_path = out / "products-filter.json"
    assert catalog_path.exists(), "products-filter.json was not emitted"
    assert (out / "filter.html").exists(), "filter.html was not emitted"

    data = json.loads(catalog_path.read_text())
    products = data["products"]
    assert products, "catalog has no products"

    known = next((p for p in products
                  if p["slug"] == "cosrx-advanced-snail-96-mucin-power-essence"), None)
    assert known is not None, "expected known published product missing from catalog"
    assert isinstance(known["price"], (int, float)) and known["price"] > 0
    assert known["price_display"]
    assert any(a["slug"] == "snail-secretion-filtrate" for a in known["actives"])
    # Every row carries the grade fields the filter needs.
    for p in products:
        assert set(p) >= {"slug", "name", "category", "actives", "price", "segs", "effect"}
        assert 0 <= p["segs"] <= 4
