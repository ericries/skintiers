"""`sk roster-set` must update a roster entry's last_pulled / backfill_cursor
robustly -- including past a long multi-line `conflict:` field, the exact case
where the old per-cron `range(i, i+8)` line search silently failed and left a
creator perpetually 'oldest'. It must preserve the file's comment header (a yaml
round-trip would drop it) and leave other entries untouched.
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
    loader = importlib.machinery.SourceFileLoader("sk_cli", str(ROOT / "scripts" / "sk"))
    spec = importlib.util.spec_from_loader("sk_cli", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


# `conflict` wraps across several physical lines, pushing last_pulled well past
# any fixed-window line search -- the ella bug.
_ROSTER = (
    "# Vetted creator roster -- comment header must survive edits.\n"
    "- name: Ella\n"
    "  creator_slug: ella\n"
    "  tier: MED\n"
    "  conflict: 'a long conflict note that wraps across several physical lines\n"
    "    to reproduce the failure mode where a fixed-window search cannot reach\n"
    "    the last_pulled line, and this creator never advances its rotation'\n"
    "  last_pulled: '2026-08-14'\n"
    "- name: Flagship\n"
    "  creator_slug: flag\n"
    "  flagship: true\n"
    "  backfill_cursor: 15\n"
    "  last_pulled: '2026-08-01'\n"
)


def _write(tmp_path):
    (tmp_path / "video-sources.yaml").write_text(_ROSTER)


def test_roster_set_last_pulled_past_multiline_field(tmp_path, monkeypatch):
    monkeypatch.setattr(sklib, "DATA_DIR", tmp_path)
    _write(tmp_path)
    sk = _load_sk()
    args = types.SimpleNamespace(slug="ella", last_pulled="2026-08-20", backfill_cursor=None)
    assert sk.cmd_roster_set(args) == 0
    text = (tmp_path / "video-sources.yaml").read_text()
    r = {c["creator_slug"]: c for c in yaml.safe_load(text)}
    assert r["ella"]["last_pulled"] == "2026-08-20"       # advanced past the wrap
    assert r["flag"]["last_pulled"] == "2026-08-01"       # other entry untouched
    assert text.startswith("# Vetted creator roster")     # comment header preserved


def test_roster_set_backfill_cursor(tmp_path, monkeypatch):
    monkeypatch.setattr(sklib, "DATA_DIR", tmp_path)
    _write(tmp_path)
    sk = _load_sk()
    args = types.SimpleNamespace(slug="flag", last_pulled=None, backfill_cursor=30)
    assert sk.cmd_roster_set(args) == 0
    r = {c["creator_slug"]: c for c in yaml.safe_load((tmp_path / "video-sources.yaml").read_text())}
    assert r["flag"]["backfill_cursor"] == 30
    assert r["ella"]["last_pulled"] == "2026-08-14"       # unrelated entry untouched


def test_roster_set_missing_slug_errors(tmp_path, monkeypatch):
    monkeypatch.setattr(sklib, "DATA_DIR", tmp_path)
    _write(tmp_path)
    sk = _load_sk()
    args = types.SimpleNamespace(slug="nobody", last_pulled="2026-08-20", backfill_cursor=None)
    assert sk.cmd_roster_set(args) == 1
    # file unchanged
    assert (tmp_path / "video-sources.yaml").read_text() == _ROSTER
