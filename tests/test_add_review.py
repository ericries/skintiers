"""`sk add-review` must serialize review-log entries via the YAML library so
quoting/escaping is never hand-built — the manual-escaping mistake that has
corrupted review-log.yaml before (an unescaped apostrophe in a single-quoted
value). These tests pin the escaping round-trip and the append/replace behavior.
"""
import importlib.machinery
import importlib.util
import pathlib
import sys
import types

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sklib  # noqa: E402


def _load_sk():
    # The CLI file is named `sk` (no .py extension), so load it with an
    # explicit source loader.
    loader = importlib.machinery.SourceFileLoader("sk_cli", str(ROOT / "scripts" / "sk"))
    spec = importlib.util.spec_from_loader("sk_cli", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


TRICKY = "BRAND cron: attributed as brand's own; it's a 'quoted' note with a colon: here"


def test_add_review_escapes_apostrophes_and_colons(tmp_path, monkeypatch):
    monkeypatch.setattr(sklib, "DATA_DIR", tmp_path)
    (tmp_path / "review-log.yaml").write_text(
        "existing-slug:\n  last_reviewed: '2026-01-01'\n  score: 9\n"
        "  verdict: publish\n  note: untouched\n"
    )
    sk = _load_sk()
    args = types.SimpleNamespace(slug="new-slug", verdict="publish", score=8,
                                 note=TRICKY, date="2026-08-19")
    assert sk.cmd_add_review(args) == 0
    data = yaml.safe_load((tmp_path / "review-log.yaml").read_text())  # must parse
    assert data["new-slug"]["note"] == TRICKY  # round-trips exactly
    assert data["new-slug"]["verdict"] == "publish"
    assert data["new-slug"]["score"] == 8
    assert data["existing-slug"]["note"] == "untouched"  # existing entry untouched


def test_add_review_appends_without_reformatting_existing(tmp_path, monkeypatch):
    monkeypatch.setattr(sklib, "DATA_DIR", tmp_path)
    original = ("a-slug:\n  last_reviewed: '2026-01-01'\n  score: 9\n"
                "  verdict: publish\n  note: first\n")
    (tmp_path / "review-log.yaml").write_text(original)
    sk = _load_sk()
    args = types.SimpleNamespace(slug="b-slug", verdict="revise", score=8,
                                 note="second", date="2026-08-19")
    assert sk.cmd_add_review(args) == 0
    text = (tmp_path / "review-log.yaml").read_text()
    assert text.startswith(original)  # existing bytes preserved verbatim (append-only)


def test_add_review_replaces_repeat_slug_in_place(tmp_path, monkeypatch):
    monkeypatch.setattr(sklib, "DATA_DIR", tmp_path)
    (tmp_path / "review-log.yaml").write_text(
        "s:\n  last_reviewed: '2026-01-01'\n  score: 7\n  verdict: revise\n  note: old\n"
    )
    sk = _load_sk()
    args = types.SimpleNamespace(slug="s", verdict="publish", score=9,
                                 note="new", date="2026-08-19")
    assert sk.cmd_add_review(args) == 0
    data = yaml.safe_load((tmp_path / "review-log.yaml").read_text())
    assert len(data) == 1  # replaced, not duplicated
    assert data["s"]["verdict"] == "publish" and data["s"]["note"] == "new"


def test_publish_does_not_grant_opus_for_a_self_verified_review(tmp_path, monkeypatch):
    """`verdict: publish` alone used to earn assurance:opus, even when the review
    was a main-loop self-verify because no Opus critic was available. That claimed
    an assurance the page had not earned and needed a manual downgrade after every
    publish. An entry that names itself self-verified must not earn opus."""
    import importlib.util, pathlib as _pl
    _p = _pl.Path(__file__).resolve().parents[1] / "scripts" / "sk"
    _spec = importlib.util.spec_from_loader("sk_cli", importlib.machinery.SourceFileLoader("sk_cli", str(_p)))
    sk = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(sk)

    # critic-backed type + a genuine critic review -> earns opus
    assert sk._publish_assurance("ingredient", "publish") == "opus"
    # ...but a self-verified review must not
    assert sk._publish_assurance("ingredient", "publish",
                                 reviewer="self (main-loop; Opus critic unavailable)") is None
    assert sk._publish_assurance("ingredient", "publish",
                                 note="Opus critic unavailable (session cap); self-verify") is None
    # non-critic types never earned it anyway
    assert sk._publish_assurance("brand", "publish") is None
