import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import product_codes as pc


def test_code_index_roundtrip():
    for n in (0, 1, 61, 62, 63, 3843, 3844, 999999):
        assert pc.to_index(pc.to_code(n)) == n
    assert pc.to_code(0) == "0"              # shortest form, no zero padding
    assert pc.to_code(61) == "z"
    assert pc.to_code(62) == "10"
    assert pc.to_code(3843) == "zz"


def test_code_space_is_unbounded():
    assert pc.to_code(62 ** 2) == "100"      # past the old fixed-width ceiling, no error


def test_sync_mints_deterministically_and_appends(tmp_path):
    reg = tmp_path / "reg.yaml"
    first = pc.sync(["b-product", "a-product"], registry=reg)      # sorted -> a=0, b=1
    assert first == {"a-product": "0", "b-product": "1"}
    # existing codes never move; a new slug takes the next free code
    second = pc.sync(["a-product", "b-product", "c-product"], registry=reg)
    assert second["a-product"] == "0" and second["b-product"] == "1"
    assert second["c-product"] == "2"
    assert reg.exists()

    # a slug that vanishes keeps its code reserved (URL stability)
    third = pc.sync(["a-product"], registry=reg)
    assert third["b-product"] == "1" and third["c-product"] == "2"
