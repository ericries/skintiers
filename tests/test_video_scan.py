"""video_scan is the cheap daily sweep that keeps every creator's freshest
uploads flowing: it must extract ids from any card url, know which videos are
already carded, prune queue entries that have since been ingested, and add only
genuinely-new uploads (deduping within the batch and against what it has seen).
"""
import importlib.machinery
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load():
    loader = importlib.machinery.SourceFileLoader(
        "video_scan", str(ROOT / "scripts" / "video_scan.py"))
    spec = importlib.util.spec_from_loader("video_scan", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def test_id_from_url_handles_each_platform():
    vs = _load()
    assert vs.id_from_url("https://www.youtube.com/watch?v=abc123DEF-_") == "abc123DEF-_"
    assert vs.id_from_url("https://youtu.be/xyz789") == "xyz789"
    assert vs.id_from_url("https://www.youtube.com/shorts/short01") == "short01"
    assert vs.id_from_url("https://www.tiktok.com/@who/video/7412345678901234567") == "7412345678901234567"
    assert vs.id_from_url("") is None
    assert vs.id_from_url(None) is None


def test_ingested_ids_reads_every_page_videos_block(tmp_path):
    vs = _load()
    (tmp_path / "ingredients").mkdir()
    (tmp_path / "conditions").mkdir()
    (tmp_path / "ingredients" / "a.md").write_text(
        "---\nslug: a\nvideos:\n"
        "- title: One\n  url: https://www.youtube.com/watch?v=VID_ONE\n"
        "- title: Two\n  url: https://youtu.be/VID_TWO\n"
        "---\nbody\n", encoding="utf-8")
    (tmp_path / "conditions" / "b.md").write_text(
        "---\nslug: b\nvideos:\n"
        "- title: Three\n  url: https://www.youtube.com/watch?v=VID_ONE\n"  # dup across pages
        "---\nbody\n", encoding="utf-8")
    (tmp_path / "ingredients" / "novid.md").write_text(
        "---\nslug: novid\n---\nbody\n", encoding="utf-8")
    ids = vs.ingested_ids(tmp_path)
    assert ids == {"VID_ONE", "VID_TWO"}


def test_new_candidates_excludes_seen_and_dedups_batch():
    vs = _load()
    recent = [
        {"id": "new1", "title": "t1"},
        {"id": "old1", "title": "t2"},   # already seen -> excluded
        {"id": "new2", "title": "t3"},
        {"id": "new1", "title": "dup"},  # dup within batch -> excluded
    ]
    out = vs.new_candidates(recent, seen_ids={"old1"})
    assert [r["id"] for r in out] == ["new1", "new2"]


def test_prune_ingested_drops_carded_pending_entries():
    vs = _load()
    queue = [
        {"id": "still_pending", "status": "pending"},
        {"id": "now_carded", "status": "pending"},
        {"id": "explicitly_skipped", "status": "skipped"},
    ]
    kept = vs.prune_ingested(queue, ingested={"now_carded"})
    assert [q["id"] for q in kept] == ["still_pending", "explicitly_skipped"]


def test_fmt_date_normalizes_yyyymmdd():
    vs = _load()
    assert vs.fmt_date("20260711") == "2026-07-11"
    assert vs.fmt_date("NA") == ""
    assert vs.fmt_date("") == ""
    assert vs.fmt_date(None) == ""
