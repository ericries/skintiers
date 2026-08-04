import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import routine_string as rs

# width 1 (all codes single char): am 4 o u ; pm 4 Y@5/wk 6 ; wk M  -> no commas
CANON = "r1/a4ou/p4Y~56/wM"


def test_parse_from_path_abs_and_full_url():
    for src in (CANON, "/" + CANON, "https://ericries.github.io/skintiers/" + CANON):
        r = rs.parse(src)
        assert [p["key"] for p in r["phases"]] == ["am", "pm", "wk"]
        assert [it["code"] for it in r["phases"][0]["items"]] == ["4", "o", "u"]
        assert r["phases"][1]["items"][1] == {"code": "Y", "freq": 5}      # ~5 cadence
        assert r["phases"][0]["items"][0]["freq"] == 7                     # daily default


def test_roundtrip_is_canonical():
    assert rs.encode(rs.parse(CANON)) == CANON


def test_width_autosizes_and_pads_wider_codes():
    # a routine using a 2-char code -> width 2, every code padded, NO commas
    routine = {"phases": [
        {"key": "pm", "items": [{"code": "9z", "freq": 4}]},
        {"key": "am", "items": [{"code": "0", "freq": 7}]},
    ]}
    assert rs.encode(routine) == "r2/a00/p9z~4"                            # am before pm; 0 -> 00; @7 dropped
    assert rs.to_url(routine, "https://x/") == "https://x/r2/a00/p9z~4"


def test_fixed_width_chunking_no_commas():
    r = rs.parse("r2/a0z10ZZ")                                            # width 2 -> 0z,10,ZZ
    assert [it["code"] for it in r["phases"][0]["items"]] == ["z", "10", "ZZ"]  # unpadded canonical


def test_anchor_declares_width_and_is_required():
    assert rs.parse("r1/a4")["phases"][0]["items"][0]["code"] == "4"
    with pytest.raises(ValueError):
        rs.parse("x1/a4")                                                 # not an rW anchor
    with pytest.raises(ValueError):
        rs.parse("r2/a4")                                                 # body not a multiple of width 2


def test_code_may_repeat_across_phases():
    assert rs.codes(rs.parse("r1/a4/p4")) == ["4"]                        # distinct, first-seen


@pytest.mark.parametrize("bad", [
    "r1/a4-",            # non-base62 code char
    "r1/a4~9",           # cadence out of range (7+ is daily/omitted)
    "r1/a4~",            # cadence marker without digit
    "r1/x4",             # unknown phase marker
    "r1/a4/a6",          # duplicate phase
])
def test_parse_rejects_malformed(bad):
    with pytest.raises(ValueError):
        rs.parse(bad)
