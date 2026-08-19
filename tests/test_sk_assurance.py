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


def test_opus_rejected_on_non_critic_types():
    # person/brand/condition/goal/list have no Opus critic -> opus is a lint error
    for typ in ("person", "brand", "condition", "goal", "list"):
        meta = {**BASE, "type": typ, "assurance": "opus"}
        if typ == "list":
            meta["kind"] = "best-of"
        errs = _errors(meta)
        assert any("assurance: opus is only valid" in e for e in errs), typ


def test_opus_allowed_on_critic_types():
    for typ in ("product", "ingredient", "study"):
        errs = _errors({**BASE, "type": typ, "assurance": "opus"})
        assert not any("only valid" in e for e in errs), typ


def test_sonnet_allowed_on_any_type():
    for typ in ("person", "brand", "condition"):
        errs = _errors({**BASE, "type": typ, "assurance": "sonnet"})
        assert not any("assurance" in e for e in errs), typ


def _write_profile(tmp_path, assurance=None):
    import frontmatter
    p = tmp_path / "x.md"
    fm = "name: X\nslug: x\ntype: product\nstatus: draft\nupdated: 2026-07-29\n"
    if assurance:
        fm += f"assurance: {assurance}\n"
    p.write_text(f"---\n{fm}---\n\nBody.\n")
    return p


def test_set_assurance_sets_level(tmp_path):
    import frontmatter
    p = _write_profile(tmp_path)
    sklib.set_assurance(p, "opus")
    assert frontmatter.load(p)["assurance"] == "opus"


def test_set_assurance_preserves_human_reviewed(tmp_path):
    import frontmatter
    p = _write_profile(tmp_path, assurance="reviewed")
    sklib.set_assurance(p, "opus")  # must not downgrade a human sign-off
    assert frontmatter.load(p)["assurance"] == "reviewed"
