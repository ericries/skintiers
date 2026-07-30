import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sklib  # noqa: E402

BODY = "Body.[^1]\n\n## Sources\n[^1]: T. https://e.com\n"


def _meta(**kw):
    m = {"name": "Best X", "slug": "best-x", "type": "list", "status": "stub",
         "updated": "2026-07-29", "kind": "best-of"}
    m.update(kw)
    return m


def _errors(meta):
    errors, _ = sklib.check_profile(meta, BODY)
    return errors


def test_list_is_a_valid_type():
    assert "list" in sklib.PROFILE_TYPES
    assert not any("invalid type" in e for e in _errors(_meta()))


def test_list_plural_is_lists():
    assert sklib.TYPE_TO_LIST["list"] == "lists"


def test_list_kind_best_of_and_routine_valid():
    assert not any("kind" in e for e in _errors(_meta(kind="best-of")))
    assert not any("kind" in e for e in _errors(_meta(kind="routine")))


def test_list_invalid_kind_errors():
    assert any("kind" in e for e in _errors(_meta(kind="favorites")))


def test_list_requires_kind():
    m = _meta()
    del m["kind"]
    assert any("kind" in e for e in _errors(m))


def test_non_list_types_do_not_require_kind():
    # a product with no kind field is fine
    m = {"name": "P", "slug": "p", "type": "product", "status": "stub",
         "updated": "2026-07-29"}
    assert not any("kind" in e for e in _errors(m))
