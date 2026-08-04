import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import product_codes as pc


def test_code_index_roundtrip():
    for n in (0, 1, 61, 62, 63, 3843):
        assert pc.to_index(pc.to_code(n)) == n
    assert pc.to_code(0) == "00"
    assert pc.to_code(61) == "0z"
    assert pc.to_code(62) == "10"


def test_code_space_is_bounded():
    with pytest.raises(ValueError):
        pc.to_code(62 ** pc.CODE_W)          # one past the max


def test_sync_mints_deterministically_and_appends(tmp_path):
    reg = tmp_path / "reg.yaml"
    first = pc.sync(["b-product", "a-product"], registry=reg)      # sorted -> a=00, b=01
    assert first == {"a-product": "00", "b-product": "01"}
    # existing codes never move; a new slug takes the next free code
    second = pc.sync(["a-product", "b-product", "c-product"], registry=reg)
    assert second["a-product"] == "00" and second["b-product"] == "01"
    assert second["c-product"] == "02"
    assert reg.exists()

    # a slug that vanishes keeps its code reserved (URL stability)
    third = pc.sync(["a-product"], registry=reg)
    assert third["b-product"] == "01" and third["c-product"] == "02"
