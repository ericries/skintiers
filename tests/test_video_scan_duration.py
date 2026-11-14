"""The pull crons cannot card a Short, so the scan queue must carry duration.

On 2026-11-13 a YouTube pull tick listed its eight freshest candidates, spent a
yt-dlp call on each to learn the duration, and rejected all eight as Shorts (14s
to 69s). The queue had 505 pending rows and no duration field, so there was no
way to ask for the ones long enough to card. These tests pin both halves of the
fix: the scanner records duration, and --list-pending can filter on it.
"""
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("video_scan", ROOT / "scripts" / "video_scan.py")
video_scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(video_scan)


def _creator():
    return {"name": "Dr Example", "creator_slug": "dr-example",
            "credential": "Board-certified dermatologist",
            "channel": "https://www.youtube.com/@example/videos",
            "tier": "HIGH", "product_recs": "ok", "conflict": None}


def test_build_candidate_records_duration():
    row = {"id": "abc123", "upload_date": "20261113", "title": "A real explainer",
           "duration": 602}
    cand = video_scan.build_candidate(row, _creator())
    assert cand["duration"] == 602


def test_build_candidate_duration_is_none_when_unknown():
    """A missing or NA duration must not become 0, which would read as a Short."""
    cand = video_scan.build_candidate({"id": "x", "upload_date": "", "title": "t"}, _creator())
    assert cand["duration"] is None


def test_rank_pending_min_duration_drops_shorts():
    queue = [
        {"id": "short1", "status": "pending", "platform": "YouTube", "posted": "2026-11-13",
         "feed_rank": 1, "duration": 52},
        {"id": "long1", "status": "pending", "platform": "YouTube", "posted": "2026-11-12",
         "feed_rank": 2, "duration": 602},
    ]
    out = video_scan.rank_pending(queue, set(), min_duration=90)
    assert [q["id"] for q in out] == ["long1"]


def test_rank_pending_min_duration_keeps_unknown_duration():
    """Rows scanned before duration existed must stay listable, not vanish."""
    queue = [{"id": "legacy", "status": "pending", "platform": "YouTube",
              "posted": "2026-11-13", "feed_rank": 1}]
    assert [q["id"] for q in video_scan.rank_pending(queue, set(), min_duration=90)] == ["legacy"]


def test_rank_pending_without_min_duration_is_unchanged():
    queue = [{"id": "short1", "status": "pending", "platform": "YouTube",
              "posted": "2026-11-13", "feed_rank": 1, "duration": 52}]
    assert [q["id"] for q in video_scan.rank_pending(queue, set())] == ["short1"]
