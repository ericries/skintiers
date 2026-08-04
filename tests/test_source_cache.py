import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import source_cache as sc

NYT = "https://www.nytimes.com/wirecutter/reviews/best-retinol-products/"
SPACENK = "https://www.spacenk.com/uk/skincare/serum-MUK200049348.html"
PUBMED = "https://pubmed.ncbi.nlm.nih.gov/28042100/"
SEPHORA = "https://www.sephora.com/product/x"


def test_only_unknown_class_is_cacheable():
    assert sc.should_cache(NYT)                    # editorial, intermittent -> cache
    assert sc.should_cache(SPACENK)                # retailer, unknown -> cache
    assert not sc.should_cache(PUBMED)             # primary, re-fetchable -> never
    assert not sc.should_cache(SEPHORA)            # aggregator, non-citable -> never


def test_put_get_roundtrip_and_skip(tmp_path):
    f = sc.put(NYT, "TESTER SAID THE SERUM WAS GENTLE", cache_dir=tmp_path)
    assert f is not None and f.exists()
    assert "TESTER SAID THE SERUM WAS GENTLE" in sc.get(NYT, cache_dir=tmp_path)
    # a re-fetchable primary is deliberately NOT cached (anti-bloat)
    assert sc.put(PUBMED, "abstract text", cache_dir=tmp_path) is None
    assert sc.get(PUBMED, cache_dir=tmp_path) is None
    with pytest.raises(ValueError):
        sc.put(NYT, "   ", cache_dir=tmp_path)     # never cache empty content


def test_gc_prunes_uncited_and_keeps_cited(tmp_path):
    cache = tmp_path / "cache"
    data = tmp_path / "data" / "products"
    data.mkdir(parents=True)
    # one page cites NYT but not SPACENK
    (data / "p.md").write_text(f"---\nslug: p\n---\n\nSee [source]({NYT}).\n")
    sc.put(NYT, "cited content", cache_dir=cache)
    sc.put(SPACENK, "orphan content", cache_dir=cache)
    assert sc.get(NYT, cache_dir=cache) and sc.get(SPACENK, cache_dir=cache)

    removed = sc.gc(cache_dir=cache, data_dir=tmp_path / "data")
    assert sc.get(NYT, cache_dir=cache) is not None        # still cited -> kept
    assert sc.get(SPACENK, cache_dir=cache) is None        # uncited -> pruned
    assert len(removed) == 1
