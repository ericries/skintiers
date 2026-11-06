"""A video card's byline must never render as an empty link.

Why this exists. 84 cards carry a blank `creator` while still carrying a
`creator_slug`, so the profile template emitted
`<a href="chris-tomassian.html"></a>`: a real link with no text. Invisible on
the page, unreachable by keyboard, and meaningless to a screen reader. The
built site had 226 such anchors. Nobody noticed because the card's thesis still
names the creator, so the page reads correctly and only the byline is gone.

70 of those cards resolve through a person page and 3 more through the creator
roster, both of which the build already loads. The remaining 11 have no slug at
all and must render as plain text or nothing, never as an empty anchor.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sklib  # noqa: E402

NAMES = {"chris-tomassian": "Dr. Chris Tomassian", "fatima-fahs": "Fatima Fahs"}


def test_an_explicit_creator_is_used_as_is():
    assert sklib.creator_display_name("Jenn Lexi", "jennlexi", NAMES) == "Jenn Lexi"


def test_an_explicit_creator_wins_over_the_index():
    """The card's own wording is authoritative; the index is only a fallback."""
    assert sklib.creator_display_name(
        "Dr Tomassian", "chris-tomassian", NAMES) == "Dr Tomassian"


def test_a_blank_creator_is_recovered_from_the_slug():
    assert sklib.creator_display_name(
        "", "chris-tomassian", NAMES) == "Dr. Chris Tomassian"


def test_whitespace_only_creator_counts_as_blank():
    assert sklib.creator_display_name(
        "   ", "fatima-fahs", NAMES) == "Fatima Fahs"


def test_none_creator_is_recovered_from_the_slug():
    assert sklib.creator_display_name(
        None, "fatima-fahs", NAMES) == "Fatima Fahs"


def test_an_unresolvable_slug_gives_none_not_an_empty_string():
    """None tells the template to omit the anchor entirely. An empty string
    would let it render <a href=...></a> again, which is the whole bug."""
    assert sklib.creator_display_name("", "nobody-here", NAMES) is None


def test_no_creator_and_no_slug_gives_none():
    assert sklib.creator_display_name("", None, NAMES) is None
    assert sklib.creator_display_name(None, None, {}) is None


def test_surrounding_whitespace_is_trimmed():
    assert sklib.creator_display_name("  Ella  ", None, NAMES) == "Ella"


def test_a_blank_name_in_the_index_does_not_resurrect_the_empty_anchor():
    assert sklib.creator_display_name("", "chris-tomassian", {"chris-tomassian": "  "}) is None
