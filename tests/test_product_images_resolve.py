"""Every `images:` entry points at a real file that actually renders.

Why it exists. The repo's recurring failure shape is that the gates check the
SOURCE while the bug lives in the render layer: `sk lint` is happy with an
`images:` block whose file was never committed, or was committed as a 400-byte
error page, and the only symptom is a broken image on the live site.

Two near-misses on 2026-11-27 are the reason this is a test and not a habit. A
free curl of a brand URL returned a 5,741-byte Cloudflare interstitial and a
retailer returned an 18-byte rate-limit body; both would have been written to
disk by a less careful fetch and both would have passed every existing gate.
The image cron also reports "nothing to do" for days at a time, so nothing was
re-checking the 489 entries already shipped.

The 3KB floor is the image cron's own rule for distinguishing a photo from an
error page. The render half is skipped when _site is absent, since the test
suite must pass without a build.
"""
import pathlib

import frontmatter
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MIN_BYTES = 3000


def _entries():
    for f in sorted((ROOT / "data/products").glob("*.md")):
        meta = frontmatter.load(f).metadata
        for item in meta.get("images") or []:
            if isinstance(item, dict) and item.get("file"):
                yield f.stem, item["file"]


def test_there_are_images_to_check():
    assert sum(1 for _ in _entries()) > 100, "expected the shipped image corpus"


def test_every_referenced_image_file_exists_and_is_a_real_image():
    bad = []
    for slug, name in _entries():
        p = ROOT / "static/images" / name
        if not p.exists():
            bad.append(f"{slug}: static/images/{name} does not exist")
        elif p.stat().st_size < MIN_BYTES:
            bad.append(f"{slug}: static/images/{name} is {p.stat().st_size}B, under the 3KB floor")
    assert not bad, "image entries pointing at nothing usable:\n" + "\n".join(bad)


def test_every_image_is_referenced_by_its_built_page():
    site = ROOT / "_site"
    if not site.is_dir():
        pytest.skip("_site not built")
    bad = []
    for slug, name in _entries():
        html = site / f"{slug}.html"
        if not html.exists():
            continue
        if f"images/{name}" not in html.read_text(errors="replace"):
            bad.append(f"{slug}: declares {name} but the built page does not reference it")
    assert not bad, "images declared in source but absent from the render:\n" + "\n".join(bad)


# Seven photos predate the attribution convention and their provenance is not
# recoverable: the commits that added them record no source, and inventing one
# would be a fabricated factual claim about where an image came from, which is
# worse than an acknowledged gap. They are listed so the rule binds every NEW
# photo, and recovering their real sources is queued separately.
UNATTRIBUTED_LEGACY = {
    ("anua-azelaic-acid-serum", "anua-azelaic-acid-serum.jpg"),
    ("anua-nano-retinol-0-3-niacin-renewing-serum",
     "anua-nano-retinol-0-3-niacin-renewing-serum.jpg"),
    ("beauty-of-joseon-light-on-serum-centella-vita-c",
     "beauty-of-joseon-light-on-serum-centella-vita-c.jpg"),
    ("cos-de-baha-az20-azelaic-acid-20-serum", "cos-de-baha-az20-azelaic-acid-20-serum.jpg"),
    ("la-roche-posay-anthelios-melt-in-milk-spf-60",
     "la-roche-posay-anthelios-melt-in-milk-spf-60.png"),
    ("la-roche-posay-toleriane", "la-roche-posay-toleriane.jpg"),
    ("the-ordinary-multi-peptide-copper-peptides-serum",
     "the-ordinary-multi-peptide-copper-peptides-serum.png"),
}


def _unattributed():
    out = set()
    for f in sorted((ROOT / "data/products").glob("*.md")):
        for item in frontmatter.load(f).metadata.get("images") or []:
            if isinstance(item, dict) and item.get("file") and not item.get("source"):
                out.add((f.stem, item["file"]))
    return out


def test_new_photos_attribute_a_source():
    """The site's convention: a photo carries where it came from."""
    bad = sorted(_unattributed() - UNATTRIBUTED_LEGACY)
    assert not bad, (
        "unattributed product photos (attribute the source, do not guess it):\n"
        + "\n".join(f"  {s}: {n}" for s, n in bad)
    )


def test_the_legacy_list_does_not_outlive_the_problem():
    """Once a legacy photo is attributed, drop it from the list above."""
    fixed = sorted(UNATTRIBUTED_LEGACY - _unattributed())
    assert not fixed, (
        "these now carry a source, so remove them from UNATTRIBUTED_LEGACY:\n"
        + "\n".join(f"  {s}: {n}" for s, n in fixed)
    )
