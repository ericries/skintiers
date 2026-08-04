import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import routine_string as rs

# am: 0A 1f 2z ; pm: 0A (repeat) 3k@3/wk 4m
CANON = "r1.a0A1f2z.p0A3k~34m"


def test_parse_basic_structure():
    r = rs.parse(CANON)
    assert [p["key"] for p in r["phases"]] == ["am", "pm"]
    assert r["phases"][0]["items"][0] == {"code": "0A", "freq": 7}      # daily default
    assert r["phases"][1]["items"][1] == {"code": "3k", "freq": 3}      # ~3 cadence


def test_roundtrip_is_canonical():
    assert rs.encode(rs.parse(CANON)) == CANON


def test_encode_drops_daily_and_canonicalizes_phase_order():
    routine = {"phases": [
        {"key": "pm", "items": [{"code": "9z", "freq": 4}]},
        {"key": "am", "items": [{"code": "00", "freq": 7}]},
    ]}
    assert rs.encode(routine) == "r1.a00.p9z~4"                          # am before pm; @7 dropped


def test_fixed_width_codes_need_no_separator():
    r = rs.parse("r1.a0A1f2z")
    assert [it["code"] for it in r["phases"][0]["items"]] == ["0A", "1f", "2z"]


def test_code_may_repeat_across_phases():
    r = rs.parse("r1.a0A.p0A")
    assert rs.codes(r) == ["0A"]                                        # distinct, first-seen


@pytest.mark.parametrize("bad", [
    "r0.a0A",            # wrong version
    "a0A",               # no version
    "r1.x0A",            # unknown phase marker
    "r1.a0",             # truncated code
    "r1.a0-",            # non-base62 code char
    "r1.a0A~9",          # cadence out of range (7+ is daily/omitted)
    "r1.a0A~",           # cadence marker without digit
    "r1.a0A.a1f",        # duplicate phase
    "r1.a0A..p1f",       # empty phase block
])
def test_parse_rejects_malformed(bad):
    with pytest.raises(ValueError):
        rs.parse(bad)
