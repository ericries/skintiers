import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sklib  # noqa: E402

BASE = {"name": "X", "slug": "x", "type": "product", "status": "published",
        "updated": "2026-07-29",
        "grades": [{"effect": "modest", "evidence": "solid", "use": "y"}]}
BODY = "## Summary\n\nText.[^1]\n\n## Sources\n[^1]: T. https://e.com\n"


def _errors(meta):
    errors, _warnings = sklib.check_profile(meta, BODY)
    return errors


def test_valid_assurance_values_pass():
    for level in ("stub", "sonnet", "opus", "reviewed"):
        assert not any("assurance" in e for e in _errors({**BASE, "assurance": level})), level


def test_invalid_assurance_value_errors():
    assert any("assurance" in e for e in _errors({**BASE, "assurance": "gold"}))


def test_assurance_is_optional():
    # a page with no assurance field is still valid
    assert not any("assurance" in e for e in _errors(BASE))


def test_valid_assurance_constant_exposed():
    assert sklib.VALID_ASSURANCE == ("stub", "sonnet", "opus", "reviewed")
