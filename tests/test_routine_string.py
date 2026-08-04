import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import routine_string as rs

# am: 4 o u ; pm: 4 (repeat) Y@5/wk 6 ; wk: M
CANON = "r1/a4,o,u/p4,Y~5,6/wM"


def test_parse_from_path_abs_and_full_url():
    for src in (CANON, "/" + CANON, "https://ericries.github.io/skintiers/" + CANON):
        r = rs.parse(src)
        assert [p["key"] for p in r["phases"]] == ["am", "pm", "wk"]
        assert r["phases"][0]["items"][0] == {"code": "4", "freq": 7}      # daily default
        assert r["phases"][1]["items"][1] == {"code": "Y", "freq": 5}      # ~5 cadence


def test_roundtrip_is_canonical():
    assert rs.encode(rs.parse(CANON)) == CANON


def test_absent_phase_is_absent_segment_and_order_canonical():
    routine = {"phases": [
        {"key": "pm", "items": [{"code": "9z", "freq": 4}]},
        {"key": "am", "items": [{"code": "0", "freq": 7}]},
    ]}
    assert rs.encode(routine) == "r1/a0/p9z~4"                    # am before pm; @7 dropped; no w seg
    assert rs.to_url(routine, "https://x/") == "https://x/r1/a0/p9z~4"


def test_variable_length_codes_no_ceiling():
    r = rs.parse("r1/az,10,ZZ")                                  # 1- and 2-char codes coexist
    assert [it["code"] for it in r["phases"][0]["items"]] == ["z", "10", "ZZ"]


def test_version_segment_required_and_checked():
    assert rs.parse("r1/a4")["phases"][0]["items"][0]["code"] == "4"
    with pytest.raises(ValueError):
        rs.parse("r2/a4")                                        # unknown major
    with pytest.raises(ValueError):
        rs.parse("r1x/a4")                                           # missing version


def test_code_may_repeat_across_phases():
    assert rs.codes(rs.parse("r1/a4/p4")) == ["4"]               # distinct, first-seen


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
