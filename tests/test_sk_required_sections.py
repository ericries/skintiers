import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sklib  # noqa: E402

PROD_META = {"type": "product", "status": "published",
             "grades": [{"effect": "modest", "evidence": "solid", "use": "x"}]}
COND_META = {"type": "condition", "status": "published"}
SOURCES = "\n## Sources\n[^1]: A source.\n"


def _warns(meta, content):
    return sklib.check_required_sections(meta, content)


def test_product_missing_summary_warns():
    w = _warns(PROD_META, "Body text." + SOURCES)
    assert any("Summary" in x for x in w)


def test_product_with_summary_ok():
    w = _warns(PROD_META, "Intro.\n\n## Summary\n\nText." + SOURCES)
    assert not any("Summary" in x for x in w)


def test_condition_missing_howto_warns():
    w = _warns(COND_META, "Body text." + SOURCES)
    assert any("How to know" in x for x in w)


def test_condition_with_howto_ok():
    w = _warns(COND_META, "Intro.\n\n## How to know you have this\n\nText." + SOURCES)
    assert not any("How to know" in x for x in w)


def test_stub_product_exempt_from_summary():
    w = _warns({**PROD_META, "status": "stub"}, "Body." + SOURCES)
    assert not any("Summary" in x for x in w)
