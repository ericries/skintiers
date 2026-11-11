"""An ingredient's top-level `tier:` must be one of best/good/mid/weak.

Why this matters, and why the damage is invisible on the rendered page:
build.py keeps a `_TIER_ALIASES` table that quietly folds "top"->best,
"strong"->good, "moderate"->mid and "minimal"->weak, so a page carrying one of
those spellings LOOKS right in the browser while storing a value the routine
builder does not recognise. Worse, `entity_tier` does `_TIER_ALIASES.get(manual)`
and returns None for anything not in that table, so a genuine typo does not fail
loudly: the ingredient silently drops out of every evidence grouping.

Nine pages had drifted off-enum before this test existed. The data check below
stops the drift coming back; the lint check makes `sk lint` say so at the point
the page is written, rather than leaving it to be counted later.
"""
import pathlib

import pytest
import yaml

import sklib

REPO = pathlib.Path(__file__).resolve().parents[1]
INGREDIENTS = REPO / "data" / "ingredients"

VALID_TIERS = {"best", "good", "mid", "weak"}


def _tier_of(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return None
    try:
        fm = yaml.safe_load(text.split("---", 2)[1]) or {}
    except yaml.YAMLError:
        return None
    return fm.get("tier")


def test_every_ingredient_tier_is_on_enum():
    off = []
    for path in sorted(INGREDIENTS.glob("*.md")):
        tier = _tier_of(path)
        if tier is None:
            continue  # unrated is allowed; a wrong rating is not
        if str(tier) not in VALID_TIERS:
            off.append(f"{path.name}: tier: {tier!r}")
    assert not off, (
        "ingredient tier: must be one of best/good/mid/weak "
        "(build.py aliases some of these so the page still renders, which is "
        "exactly why they go unnoticed):\n  " + "\n  ".join(off))


@pytest.mark.parametrize("bad", ["strong", "top", "moderate", "minimal", "amazing", ""])
def test_lint_rejects_off_enum_tier(bad):
    errors = sklib.check_tier_enum({"type": "ingredient", "tier": bad})
    assert errors, f"lint accepted off-enum tier {bad!r}"


@pytest.mark.parametrize("good", ["best", "good", "mid", "weak"])
def test_lint_accepts_on_enum_tier(good):
    assert sklib.check_tier_enum({"type": "ingredient", "tier": good}) == []


def test_lint_allows_missing_tier():
    """Unrated is a legitimate state; only a WRONG value is an error."""
    assert sklib.check_tier_enum({"type": "ingredient"}) == []


def test_lint_ignores_tier_on_other_types():
    """Lists and hubs use their own vocabulary for tier_list rungs; this enum is
    the ingredient evidence grade only and must not police other types."""
    assert sklib.check_tier_enum({"type": "list", "tier": "strong"}) == []
