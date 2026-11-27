"""`verify_profile` classifies sources attributed in PROSE, not just in footnotes.

Why it exists. `_source_defs` matches only footnote-definition lines inside
`## Sources`, so every URL a page attributes in running prose bypassed domain
classification completely. A page whose price and composition rested on a
retailer listing, named only in a prose Sources paragraph, exited 0 and looked
identical to a page citing PubMed in footnotes. Found 2026-11-27 on
la-roche-posay-toleriane-double-repair-face-moisturizer, which attributes its
INCI to incidecoder and its price and marketing claims to an Ulta listing, all
in prose, and passed the source gate silently.

Why these are WARNINGS and never errors. A footnoted aggregator is an error
because a footnote is a citation: the page is leaning on it as evidence. Prose
attribution is weaker and does real, sanctioned work here, above all naming
incidecoder as where an INCI was decoded, which is exactly what this project's
own `inci_lookup.py` is for. Erroring on prose would break four correctly
written product pages. The goal is to make what a page rests on VISIBLE in the
gate's output, not to relabel honest attribution as a defect.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import sklib  # noqa: E402

META = {"type": "product", "status": "published"}


def _page(sources_prose):
    return (
        "## Summary\n\nA product.\n\n## The Rubric\n\nGrades.\n\n"
        "## What's In It\n\nINCI.\n\n## The Evidence\n\nEvidence.\n\n"
        "## Common Marketing Claims\n\nClaims.\n\n## Where to Buy\n\nShops.\n\n"
        "## See Also\n\nLinks.\n\n"
        f"## Sources\n\n{sources_prose}\n"
    )


def _warn_text(prose):
    return " ".join(sklib.verify_profile(META, _page(prose))[1])


def test_retailer_named_only_in_prose_is_reported():
    """The real 2026-11-27 case: a retailer carrying the price, in prose only."""
    prose = (
        "The price and the brand's marketing claims are from the Ulta product "
        "listing at https://www.ulta.com/p/some-moisturizer-pimprod1234567, "
        "accessed 2026-09-24."
    )
    errors, warnings = sklib.verify_profile(META, _page(prose))
    assert any("ulta.com" in w for w in warnings), warnings
    assert not errors, errors


def test_prose_aggregator_warns_but_does_not_error():
    """incidecoder named as where an INCI was decoded must stay publishable."""
    prose = (
        "The composition above is the product's INCI as decoded by incidecoder, "
        "https://incidecoder.com/products/some-product, from the packaging."
    )
    errors, warnings = sklib.verify_profile(META, _page(prose))
    assert any("incidecoder.com" in w for w in warnings), warnings
    assert not errors, "prose attribution must never hard-error: %r" % (errors,)


def test_primary_source_in_prose_is_not_flagged():
    prose = (
        "The trial is reported at https://pubmed.ncbi.nlm.nih.gov/31565952/ "
        "and the label at https://dailymed.nlm.nih.gov/dailymed/x.cfm."
    )
    assert "pubmed" not in _warn_text(prose)
    assert "dailymed" not in _warn_text(prose)


def test_footnoted_aggregator_still_errors():
    """The existing, stricter footnote contract is unchanged."""
    prose = "[^a]: incidecoder. https://incidecoder.com/products/some-product"
    errors, _ = sklib.verify_profile(META, _page(prose))
    assert any("aggregator" in e for e in errors), errors


def test_prose_url_is_not_double_reported():
    """A URL in a footnote must not also be reported as a prose source."""
    prose = "[^a]: Brand page. https://www.example-brand.com/p/x"
    warnings = sklib.verify_profile(META, _page(prose))[1]
    assert len([w for w in warnings if "example-brand.com" in w]) == 1, warnings


# --- sources named in words, with no URL at all -----------------------------
# The page that prompted all of this, la-roche-posay-toleriane-double-repair-
# face-moisturizer, turned out not to have a prose URL either: its Sources
# block names "incidecoder" and "the Ulta product listing" in words and links
# neither. Nothing can be re-fetched or cached from that, so the price and
# composition it carries cannot be re-verified by anyone later.
#
# Scoped to the claim-bearing types on purpose. A list's Sources block
# legitimately carries no URL, because a list is curatorial over pages that
# already exist and each claim is sourced on the page it came from; 29 list
# pages are correct exactly as they are.

def test_product_sources_with_no_url_at_all_is_reported():
    prose = (
        "The composition is the INCI as decoded by incidecoder and confirmed on "
        "the Ulta product listing; the price is from that same listing."
    )
    errors, warnings = sklib.verify_profile(META, _page(prose))
    assert any("no citable url" in w.lower() for w in warnings), warnings
    assert not errors, errors


def test_list_sources_with_no_url_is_left_alone():
    meta = {"type": "list", "status": "published"}
    prose = "Every claim is sourced on the linked product and ingredient pages."
    warnings = sklib.verify_profile(meta, _page(prose))[1]
    assert not any("no citable url" in w.lower() for w in warnings), warnings
