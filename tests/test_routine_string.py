import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import routine_string as rs

CANON = ("r1.am:cerave-foaming-cleanser,timeless-20-vitamin-c-e-ferulic-serum,"
         "supergoop-unseen-sunscreen-spf-40.pm:cerave-hydrating-cleanser,"
         "medik8-crystal-retinal-3@3,cerave-daily-moisturizing-lotion")


def test_parse_basic_structure():
    r = rs.parse(CANON)
    assert [p["key"] for p in r["phases"]] == ["am", "pm"]
    am = r["phases"][0]["items"]
    assert am[0] == {"slug": "cerave-foaming-cleanser", "freq": 7}          # daily default
    pm = r["phases"][1]["items"]
    assert pm[1] == {"slug": "medik8-crystal-retinal-3", "freq": 3}         # @3 cadence


def test_roundtrip_is_canonical():
    assert rs.encode(rs.parse(CANON)) == CANON


def test_encode_drops_daily_and_canonicalizes_phase_order():
    routine = {"phases": [
        {"key": "pm", "items": [{"slug": "tretinoin-0-025-cream", "freq": 4}]},
        {"key": "am", "items": [{"slug": "cerave-foaming-cleanser", "freq": 7}]},
    ]}
    # am sorts before pm; the freq=7 item drops its @7
    assert rs.encode(routine) == "r1.am:cerave-foaming-cleanser.pm:tretinoin-0-025-cream@4"


def test_slug_may_repeat_across_phases():
    r = rs.parse("r1.am:cerave-daily-moisturizing-lotion.pm:cerave-daily-moisturizing-lotion")
    assert rs.slugs(r) == ["cerave-daily-moisturizing-lotion"]              # distinct, first-seen


def test_empty_phase_allowed():
    r = rs.parse("r1.am:.pm:medik8-crystal-retinal-3")
    assert r["phases"][0]["items"] == []


@pytest.mark.parametrize("bad", [
    "r0.am:x",                       # wrong version
    "am:x",                          # no version
    "r1.am",                         # phase missing ':'
    "r1.xx:foo",                     # unknown phase key
    "r1.am:Bad_Slug",                # invalid slug chars
    "r1.am:x@9",                     # cadence out of range
    "r1.am:x.am:y",                  # duplicate phase
])
def test_parse_rejects_malformed(bad):
    with pytest.raises(ValueError):
        rs.parse(bad)
