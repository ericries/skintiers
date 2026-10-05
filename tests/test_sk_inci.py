"""Raw-INCI text search. Fixes a false negative that mattered.

`products_with.py copper-peptides` does NOT return COSRX 6 Peptide Skin Booster,
even though that page names "copper tripeptide-1" six times, because it matches the
ingredient SLUG via key_actives or an [[xref]]. An agent asking "does COSRX contain
copper peptides" therefore got a confident wrong answer. Composition questions need
to search the declared ingredient TEXT.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import sklib  # noqa: E402


def test_finds_a_raw_inci_string_that_is_not_a_slug(tmp_path):
    d = tmp_path / "data" / "products"
    d.mkdir(parents=True)
    (d / "serum.md").write_text(
        "---\nname: Six Peptide Serum\nslug: serum\ntype: product\n"
        "status: published\nupdated: 2026-01-01\nkey_actives:\n- peptides\n---\n\n"
        "## What's In It\n\nAqua, Copper Tripeptide-1 (GHK-Cu), Glycerin.\n")
    (d / "other.md").write_text(
        "---\nname: Other\nslug: other\ntype: product\n"
        "status: published\nupdated: 2026-01-01\n---\n\nAqua, Glycerin.\n")
    hits = sklib.search_inci("copper tripeptide", tmp_path / "data")
    assert [h["slug"] for h in hits] == ["serum"]
    assert "Copper Tripeptide-1" in hits[0]["snippet"]


def test_match_is_case_and_punctuation_tolerant(tmp_path):
    d = tmp_path / "data" / "products"
    d.mkdir(parents=True)
    (d / "p.md").write_text(
        "---\nname: P\nslug: p\ntype: product\nstatus: published\n"
        "updated: 2026-01-01\n---\n\nAqua, Palmitoyl Tripeptide-1, Glycerin.\n")
    assert sklib.search_inci("PALMITOYL tripeptide 1", tmp_path / "data")
    assert sklib.search_inci("palmitoyl-tripeptide-1", tmp_path / "data")


def test_absent_term_returns_empty_not_a_guess(tmp_path):
    d = tmp_path / "data" / "products"
    d.mkdir(parents=True)
    (d / "p.md").write_text(
        "---\nname: P\nslug: p\ntype: product\nstatus: published\n"
        "updated: 2026-01-01\n---\n\nAqua, Glycerin.\n")
    assert sklib.search_inci("retinol", tmp_path / "data") == []
