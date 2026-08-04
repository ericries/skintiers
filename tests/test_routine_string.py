import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import routine_string as rs

# am: 4 o u 6 d ; pm: 4 (repeat) Y@5/wk 6 ; wk: M
CANON = "am=4,o,u,6,d&pm=4,Y~5,6&wk=M"


def test_parse_from_query_and_full_url():
    for src in (CANON, "?" + CANON, "https://x.example/routine.html?" + CANON):
        r = rs.parse(src)
        assert [p["key"] for p in r["phases"]] == ["am", "pm", "wk"]
        assert r["phases"][0]["items"][0] == {"code": "4", "freq": 7}      # daily default
        assert r["phases"][1]["items"][1] == {"code": "Y", "freq": 5}      # ~5 cadence


def test_roundtrip_is_canonical():
    assert rs.encode(rs.parse(CANON)) == CANON


def test_absent_phase_is_absent_param_and_order_canonical():
    routine = {"phases": [
        {"key": "pm", "items": [{"code": "9z", "freq": 4}]},
        {"key": "am", "items": [{"code": "0", "freq": 7}]},
    ]}
    assert rs.encode(routine) == "am=0&pm=9z~4"                            # am before pm; @7 dropped; no wk=
    assert rs.to_url(routine) == "routine.html?am=0&pm=9z~4"


def test_variable_length_codes_no_ceiling():
    r = rs.parse("am=z,10,ZZ")                                            # 1- and 2-char codes coexist
    assert [it["code"] for it in r["phases"][0]["items"]] == ["z", "10", "ZZ"]


def test_version_absent_is_v1_unknown_rejected():
    assert rs.parse("v=1&am=4")["phases"][0]["items"][0]["code"] == "4"
    with pytest.raises(ValueError):
        rs.parse("v=2&am=4")


def test_code_may_repeat_across_phases():
    assert rs.codes(rs.parse("am=4&pm=4")) == ["4"]                        # distinct, first-seen


@pytest.mark.parametrize("bad", [
    "am=4-",             # non-base62 code char
    "am=4~9",            # cadence out of range (7+ is daily/omitted)
    "am=4~",             # cadence marker without digit
    "am=4&am=6",         # duplicate phase param
])
def test_parse_rejects_malformed(bad):
    with pytest.raises(ValueError):
        rs.parse(bad)
